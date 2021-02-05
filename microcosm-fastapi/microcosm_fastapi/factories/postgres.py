from databases import Database
from microcosm_postgres.factories.engine import choose_uri
from microcosm_postgres.context import SessionContext


def configure_postgres(graph):
    # TODO: Refactor into separate config
    # https://www.encode.io/databases/database_queries/
    #SessionContext.session = SpecialSession()

    database_uri = choose_uri(graph.metadata, graph.config.postgres)
    database = Database(database_uri)

    @graph.app.on_event("startup")
    async def startup():
        await database.connect()

    @graph.app.on_event("shutdown")
    async def shutdown():
        await database.disconnect()

    return database
