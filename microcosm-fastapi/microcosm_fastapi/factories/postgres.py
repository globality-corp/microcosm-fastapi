from microcosm_postgres.factories.engine import choose_uri, choose_args
from microcosm_fastapi.context import SessionContext
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.ext.asyncio import AsyncSession

def make_engine(metadata, config):
    uri = choose_uri(metadata, config.postgres)
    args = choose_args(metadata, config.postgres)
    return create_async_engine(
        uri,
        **args,
    )


def configure_postgres(graph):
    # TODO: Refactor into separate config
    # https://www.encode.io/databases/database_queries/
    #SessionContext.session = SpecialSession()

    engine = make_engine(graph.metadata, graph.config)

    #SessionContext.session = SpecialSession(database)

    @graph.app.on_event("startup")
    async def startup():
        print("STARTUP")
        SessionContext.session = AsyncSession(engine)
        print("Value", SessionContext.session)
       #await database.connect()

    #@graph.app.on_event("shutdown")
    #async def shutdown():
    #    await database.disconnect()

    return engine
