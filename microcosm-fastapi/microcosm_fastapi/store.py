"""
Abstraction layer for persistence operations.
As much as `SQLAlchemy` provides a great deal of power, overuse of its features
creates dangerous coupling within applications. The two worst violations are:
 a. Using models directly to perform persistence operations causes persistence code
    to permeate all layers of the application, making it hard to change relationships
    and to write generic service logic in terms of a uniform persistence interface.
 b. Using explicit relationships between models makes it harder to migrate responsiblity
    for one side of the relationship to different services.
Instead, persistence operations should pass through a `Store` layer and should obey
CRUD conventions as much as possible.
"""
from contextlib import contextmanager

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.exc import FlushError, NoResultFound

from microcosm_postgres.context import SessionContext
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


class Store:

    def __init__(self, graph, model_class, auto_filter_fields=()):
        self.graph = graph
        self.model_class = model_class
        self.auto_filters = {
            auto_filter_field.name: auto_filter_field
            for auto_filter_field in auto_filter_fields
        }
        self.postgres_store_metrics = self.graph.postgres_store_metrics
        self.assign_model_class_store()

    def assign_model_class_store(self):
        if self.model_class:
            # Give the model class a backref to allow model-oriented CRUD
            # short cuts while still having an abstraction layer we can replace.
            self.model_class.store = self

    @property
    def model_name(self):
        return self.model_class.__name__ if self.model_class else None

    @property
    def session(self):
        return SessionContext.session

    def new_object_id(self):
        """
        Injectable id generation to facilitate mocking.
        """
        return new_object_id()

    @contextmanager
    def flushing(self):
        """
        Flush the current session, handling common errors.
        """
        try:
            yield
            self.session.flush()
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

    @postgres_metric_timing(action="update_with_diff")
    def update_with_diff(self, identifier, new_instance):
        """
        Update an existing model with a new one.
        :raises `ModelNotFoundError` if there is no existing model
        """
        with self.flushing():
            instance = self.retrieve(identifier)
            before = Version(instance)
            self.merge(instance, new_instance)
            instance.updated_at = instance.new_timestamp()
            after = Version(instance)
        return instance, before - after

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

    @postgres_metric_timing(action="delete")
    def delete(self, identifier):
        """
        Delete a model by primary key.
        :raises `ModelNotFoundError` if the row cannot be deleted.
        """
        return self._delete(self.model_class.id == identifier)

    @postgres_metric_timing(action="count")
    async def count(self, *criterion, **kwargs):
        """
        Count the number of models matching some criterion.
        """
        query = self._query(*criterion)
        query = self._filter(query, **kwargs)
        return await query.count()

    @postgres_metric_timing(action="search")
    async def search(self, *criterion, **kwargs):
        """
        Return the list of models matching some criterion.
        :param offset: pagination offset, if any
        :param limit: pagination limit, if any
        """
        print("RUN THIS")
        query = self._query(*criterion)
        query = self._order_by(query, **kwargs)
        query = self._filter(query, **kwargs)
        # NB: pagination must go last
        query = self._paginate(query, **kwargs)
        return await query.all()

    @postgres_metric_timing(action="search_first")
    def search_first(self, *criterion, **kwargs):
        """
        Returns the first match based on criteria or None.
        """
        query = self._query(*criterion)
        query = self._order_by(query, **kwargs)
        query = self._filter(query, **kwargs)
        # NB: pagination must go last
        query = self._paginate(query, **kwargs)
        return query.first()

    def expunge(self, instance):
        return self.session.expunge(instance)

    def merge(self, instance, new_instance):
        self.session.merge(new_instance)

    def _order_by(self, query, **kwargs):
        """
        Add an order by clause to a (search) query.
        By default, is a noop.
        """
        return query

    def _filter(self, query, **kwargs):
        """
        Filter a query with user-supplied arguments.
        """
        query = self._auto_filter(query, **kwargs)
        return query

    def _auto_filter(self, query, **kwargs):
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

    def _retrieve(self, *criterion):
        """
        Retrieve a model by some criteria.
        :raises `ModelNotFoundError` if the row cannot be deleted.
        """
        try:
            return self._query(*criterion).one()
        except NoResultFound as error:
            raise ModelNotFoundError(
                "{} not found".format(
                    self.model_class.__name__,
                ),
                error,
            )

    def _delete(self, *criterion, synchronize_session="evaluate"):
        """
        Delete a model by some criterion.
        Avoids race-condition check-then-delete logic by checking the count of affected rows.
        NB: The `synchronize_session` keyword param is inherited from
        sqlalchemy.delete to control how sqlalchemy computes the set of rows to
        delete. This can be important for efficiency as well as flexibility. For more details see:
        https://docs.sqlalchemy.org/en/13/orm/query.html?highlight=delete#sqlalchemy.orm.query.Query.delete
        :raises `ResourceNotFound` if the row cannot be deleted.
        """
        with self.flushing():
            count = self._query(*criterion).delete(synchronize_session=synchronize_session)
        if count == 0:
            raise ModelNotFoundError
        return True

    def _query(self, *criterion):
        """
        Construct a query for the model.
        """
        return self.session.query(
            self.model_class
        ).filter(
            *criterion
        )