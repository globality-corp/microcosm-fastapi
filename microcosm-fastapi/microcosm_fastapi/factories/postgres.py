from databases import Database
from microcosm_postgres.factories.engine import choose_uri
from microcosm_postgres.context import SessionContext

class SpecialSelector:
    def __init__(self, raw_select, database):
        self.raw_select = raw_select
        self.database = database

    def filter(self, *args, **kwargs):
        if len(args) == 0 and len(kwargs) == 0:
            return SpecialSelector(
                self.raw_select,
                database=self.database
            )

        return SpecialSelector(
            self.raw_select.where(*args, **kwargs),
            database=self.database
        )

    async def all(self):
        return await self.database.fetch_all(query=self.raw_select)

    async def count(self):
        return await self.database.fetch_all(query=self.raw_select.count())

    def __getattr__(self, attr):
        # TODO: Add function call
        # Proxy other requests to the internal raw selector
        return SpecialSelector(
            getattr(self.raw_select, attr),
            database=self.database
        )

    def __call__(self, *args, **kwargs):
        return SpecialSelector(
            self.raw_select(*args, **kwargs),
            database=self.database
        )


class SpecialSession:
    def __init__(self, database):
        self.database = database

    def query(self, obj):
        print("DIR", dir(obj.__table__.select()))
        return SpecialSelector(obj.__table__.select(), self.database)

    #Pizza.__table__

def configure_postgres(graph):
    # TODO: Refactor into separate config
    # https://www.encode.io/databases/database_queries/
    #SessionContext.session = SpecialSession()

    database_uri = choose_uri(graph.metadata, graph.config.postgres)
    database = Database(database_uri)

    SessionContext.session = SpecialSession(database)

    @graph.app.on_event("startup")
    async def startup():
        await database.connect()

    @graph.app.on_event("shutdown")
    async def shutdown():
        await database.disconnect()
