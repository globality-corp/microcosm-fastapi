from contextlib import contextmanager

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.exc import FlushError, NoResultFound
from sqlalchemy import select

from microcosm_fastapi.context import SessionContext
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
from sqlalchemy import func

class Store:

    def __init__(self, graph, model_class, auto_filter_fields=()):
        self.graph = graph
        self.model_class = model_class
        self.auto_filters = {
            auto_filter_field.name: auto_filter_field
            for auto_filter_field in auto_filter_fields
        }
        self.postgres_store_metrics = self.graph.postgres_store_metrics

    @property
    def model_name(self):
        return self.model_class.__name__ if self.model_class else None

    def new_object_id(self):
        """
        Injectable id generation to facilitate mocking.
        """
        return new_object_id()

    @postgres_metric_timing(action="create")
    def create(self, instance):
        """
        Create a new model instance.
        """
        with self.flushing():
            if instance.id is None:
                instance.id = self.new_object_id()
            self.session.add(instance)
        return instance

    @postgres_metric_timing(action="retrieve")
    def retrieve(self, identifier, *criterion):
        """
        Retrieve a model by primary key and zero or more other criteria.
        :raises `NotFound` if there is no existing model
        """
        return self._retrieve(
            self.model_class.id == identifier,
            *criterion
        )

    @postgres_metric_timing(action="update")
    def update(self, identifier, new_instance):
        """
        Update an existing model with a new one.
        :raises `ModelNotFoundError` if there is no existing model
        """
        with self.flushing():
            instance = self.retrieve(identifier)
            self.merge(instance, new_instance)
            instance.updated_at = instance.new_timestamp()
        return instance

    def replace(self, identifier, new_instance):
        """
        Create or update a model.
        """
        try:
            # Note that `self.update()` ultimately calls merge, which will not enforce
            # a strict replacement; absent fields will default to the current values.
            return self.update(identifier, new_instance)
        except ModelNotFoundError:
            return self.create(new_instance)

    # @postgres_metric_timing(action="delete")
    # def delete(self, identifier):
    #     """
    #     Delete a model by primary key.
    #     :raises `ModelNotFoundError` if the row cannot be deleted.
    #     """
    #     return self._delete(self.model_class.id == identifier)

    @postgres_metric_timing(action="count")
    async def count(self, **kwargs):
        """
        Count the number of models matching some criterion.
        """
        # TODO: Use count object
        objects = await self.search(**kwargs)
        return len(objects)

    @postgres_metric_timing(action="search")
    async def search(self, **kwargs):
        """
        Return the list of models matching some criterion.
        :param offset: pagination offset, if any
        :param limit: pagination limit, if any
        """
        query = select(self.model_class)
        query = self._order_by(query, **kwargs)
        query = self._where(query, **kwargs)
        # NB: pagination must go last
        query = self._paginate(query, **kwargs)
        return await self.graph.fast_postgres.fetch_all(query=query)

    @postgres_metric_timing(action="search_first")
    async def search_first(self, *criterion, **kwargs):
        """
        Returns the first match based on criteria or None.
        """
        query = self._query(*criterion)
        query = self._order_by(query, **kwargs)
        query = self._where(query, **kwargs)
        # NB: pagination must go last
        query = self._paginate(query, **kwargs)
        return await self.graph.fast_postgres.fetch_one(query=query)

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
            query = query.where(field == value)

        return query

    def _paginate(self, query, **kwargs):
        offset, limit = kwargs.get("offset"), kwargs.get("limit")
        if offset is not None:
            query = query.offset(offset)
        if limit is not None:
            query = query.limit(limit)

        return query

    def _retrieve(self, identifier):
        """
        Retrieve a model by some criteria.
        :raises `ModelNotFoundError` if the row cannot be deleted.
        """
        try:
            return self.search_first(
                id=identifier,
            )
        except NoResultFound as error:
            raise ModelNotFoundError(
                "{} not found".format(
                    self.model_class.__name__,
                ),
                error,
            )

    # def _delete(self, *criterion, synchronize_session="evaluate"):
    #     """
    #     Delete a model by some criterion.
    #     Avoids race-condition check-then-delete logic by checking the count of affected rows.
    #     NB: The `synchronize_session` keyword param is inherited from
    #     sqlalchemy.delete to control how sqlalchemy computes the set of rows to
    #     delete. This can be important for efficiency as well as flexibility. For more details see:
    #     https://docs.sqlalchemy.org/en/13/orm/query.html?highlight=delete#sqlalchemy.orm.query.Query.delete
    #     :raises `ResourceNotFound` if the row cannot be deleted.
    #     """
    #     with self.flushing():
    #         count = self._query(*criterion).delete(synchronize_session=synchronize_session)
    #     if count == 0:
    #         raise ModelNotFoundError
    #     return True
