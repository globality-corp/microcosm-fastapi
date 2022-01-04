from contextlib import asynccontextmanager
from typing import Optional

from microcosm_postgres.diff import Version
from microcosm_postgres.errors import (
    DuplicateModelError,
    MissingDependencyError,
    ModelIntegrityError,
    ModelNotFoundError,
    ReferencedModelError,
)
from microcosm_postgres.identifiers import new_object_id
from microcosm_postgres.metrics import postgres_metric_timing
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm.exc import FlushError, NoResultFound


class StoreAsync:
    def __init__(self, graph, model_class, auto_filter_fields=()):
        if graph:
            self.graph = graph
            self.session_maker = graph.session_maker_async
            self.postgres_store_metrics = self.graph.postgres_store_metrics
        else:
            # no-op function for metrics if graph isn't passed
            self.postgres_store_metrics = lambda *args, **kwargs: None

        self.model_class = model_class
        self.auto_filters = {
            auto_filter_field.name: auto_filter_field
            for auto_filter_field in auto_filter_fields
        }
        self.assign_model_class_store()

        # Error checking on subclass definitions
        if hasattr(self, "_filter"):
            raise ValueError("_filter is no longer supported, use _where")

    def assign_model_class_store(self):
        if self.model_class:
            # Give the model class a backref to allow model-oriented CRUD
            # short cuts while still having an abstraction layer we can replace.
            self.model_class.store = self

    @property
    def model_name(self):
        return self.model_class.__name__ if self.model_class else None

    def new_object_id(self):
        """
        Injectable id generation to facilitate mocking.
        """
        return new_object_id()

    @asynccontextmanager
    async def flushing(self, session):
        """
        Flush the current session, handling common errors.
        """
        try:
            yield
            await session.flush()
        except (FlushError, IntegrityError) as error:
            error_message = str(error)
            # There ought to be a cleaner way to capture this condition
            if "duplicate" in error_message:
                raise DuplicateModelError(error)
            if "already exists" in error_message:
                raise DuplicateModelError(error)
            if "conflicts with" in error_message and "identity key" in error_message:
                raise DuplicateModelError(error)
            elif "still referenced" in error_message:
                raise ReferencedModelError(error)
            elif "is not present" in error_message:
                raise MissingDependencyError(error)
            else:
                raise ModelIntegrityError(error)

    @asynccontextmanager
    async def with_transaction(self, session):
        try:
            yield
            await session.commit()
        except Exception:
            await session.rollback()
            raise

    @asynccontextmanager
    async def with_maybe_transactional_flushing_session(
        self, session: Optional[AsyncSession] = None
    ):
        if session:
            # if providing a session then transactions should be managed outside
            # of this context manager
            async with self.flushing(session):
                yield session

        else:
            async with self.session_maker() as session:
                async with self.with_transaction(session):
                    async with self.flushing(session):
                        yield session

    @asynccontextmanager
    async def with_maybe_session(self, session: Optional[AsyncSession] = None):
        if session:
            yield session

        else:
            async with self.session_maker() as session:
                yield session

    @postgres_metric_timing(action="create")
    async def create(self, instance, session: Optional[AsyncSession] = None):
        """
        Create a new model instance.
        """
        async with self.with_maybe_transactional_flushing_session(session) as session:
            if instance.id is None:
                instance.id = self.new_object_id()
            session.add(instance)

        return instance

    @postgres_metric_timing(action="retrieve")
    async def retrieve(self, identifier, *criterion, session: Optional[AsyncSession] = None):
        """
        Retrieve a model by primary key and zero or more other criteria.
        :raises `NotFound` if there is no existing model
        """
        return await self._retrieve(self.model_class.id == identifier, *criterion, session=session)

    @postgres_metric_timing(action="update")
    async def update(self, identifier, new_instance, session: Optional[AsyncSession] = None):
        """
        Update an existing model with a new one.
        :raises `ModelNotFoundError` if there is no existing model
        """
        async with self.with_maybe_transactional_flushing_session(session) as session:
            instance = await self.retrieve(identifier)
            await self.merge(instance, new_instance, session)
            instance.updated_at = instance.new_timestamp()

        return instance

    @postgres_metric_timing(action="update_with_diff")
    async def update_with_diff(
        self, identifier, new_instance, session: Optional[AsyncSession] = None
    ):
        """
        Update an existing model with a new one.
        :raises `ModelNotFoundError` if there is no existing model
        """
        async with self.with_maybe_transactional_flushing_session(session) as session:
            instance = await self.retrieve(identifier, session=session)
            before = Version(instance)
            await self.merge(instance, new_instance, session)
            instance.updated_at = instance.new_timestamp()
            after = Version(instance)

        return instance, before - after

    async def replace(self, identifier, new_instance, session: Optional[AsyncSession] = None):
        """
        Create or update a model.
        """
        try:
            # Note that `self.update()` ultimately calls merge, which will not enforce
            # a strict replacement; absent fields will default to the current values.
            return await self.update(identifier, new_instance, session=session)
        except ModelNotFoundError:
            return await self.create(new_instance)

    @postgres_metric_timing(action="delete")
    async def delete(self, identifier, session: Optional[AsyncSession] = None):
        """
        Delete a model by primary key.
        :raises `ModelNotFoundError` if the row cannot be deleted.
        """
        return await self._delete(self.model_class.id == identifier)

    @postgres_metric_timing(action="count")
    async def count(self, *criterion, session: Optional[AsyncSession] = None, **kwargs):
        """
        Count the number of models matching some criterion.
        """
        query = self._query(*criterion)
        query = self._where(query, **kwargs).subquery()
        query = select(func.count(query.c.id))
        return await self.get_first(query, session=session)

    @postgres_metric_timing(action="search")
    async def search(self, *criterion, session: Optional[AsyncSession] = None, **kwargs):
        """
        Return the list of models matching some criterion.
        :param offset: pagination offset, if any
        :param limit: pagination limit, if any
        :param session: sqlalchemy session, if any
        """
        query = self._query(*criterion)
        query = self._order_by(query, **kwargs)
        query = self._where(query, **kwargs)
        # NB: pagination must go last
        query = self._paginate(query, **kwargs)

        return await self.get_all(query, session=session)

    @postgres_metric_timing(action="search_first")
    async def search_first(self, *criterion, session: Optional[AsyncSession] = None, **kwargs):
        """
        Returns the first match based on criteria or None.
        """
        query = self._query(*criterion)
        query = self._order_by(query, **kwargs)
        query = self._where(query, **kwargs)
        # NB: pagination must go last
        query = self._paginate(query, **kwargs)

        return await self.get_first(query, session=session)

    async def expunge(self, instance, session: Optional[AsyncSession] = None):
        async with self.with_maybe_session(session) as session:
            return session.expunge(instance)

    async def merge(self, instance, new_instance, session: AsyncSession):
        await session.merge(new_instance)

    async def get_all(self, query, session: Optional[AsyncSession] = None):
        async with self.with_maybe_session(session) as session:
            results = await session.execute(query)
            return [response[0] for response in results.all()]

    async def get_first(self, query, session: Optional[AsyncSession] = None):
        async with self.with_maybe_session(session) as session:
            results = await session.execute(query)
            first_result = results.first()

        if not first_result:
            return None
        return first_result[0]

    def _order_by(self, query, **kwargs):
        """
        Add an order by clause to a (search) query.
        By default, is a noop.
        """
        return query

    def _where(self, query, **kwargs):
        """
        Filter a query with user-supplied arguments.
        """
        query = self._auto_where(query, **kwargs)
        return query

    def _auto_where(self, query, **kwargs):
        for key, value in kwargs.items():
            if value is None:
                continue
            field = self.auto_filters.get(key)
            if field is None:
                continue
            query = query.filter(field == value)

        return query

    def _paginate(self, query, **kwargs):
        offset, limit = kwargs.get("offset"), kwargs.get("limit")
        if offset is not None:
            query = query.offset(offset)
        if limit is not None:
            query = query.limit(limit)

        return query

    async def _retrieve(self, *criterion, session: Optional[AsyncSession] = None):
        """
        Retrieve a model by some criteria.
        :raises `ModelNotFoundError` if the row cannot be deleted.
        """
        try:
            query = self._query(*criterion)
            async with self.with_maybe_session(session) as session:
                results = await session.execute(query)
                return results.one()[0]

        except NoResultFound as error:
            raise ModelNotFoundError(
                "{} not found".format(
                    self.model_class.__name__,
                ),
                error,
            )

    async def _delete(self, *criterion, session: Optional[AsyncSession] = None):
        """
        Delete a model by some criterion.
        """
        query = self._query(*criterion)
        async with self.with_maybe_transactional_flushing_session(session) as session:
            count = len([await session.delete(row[0]) for row in await session.execute(query)])

        if count == 0:
            raise ModelNotFoundError
        return True

    def _query(self, *criterion):
        """
        Construct a query for the model.
        """
        query = select(self.model_class)

        if criterion:
            query = query.where(*criterion)

        return query
