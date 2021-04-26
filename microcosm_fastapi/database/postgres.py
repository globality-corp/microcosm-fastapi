from microcosm_postgres.factories.engine import choose_args, choose_uri
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine


def make_engine(metadata, config):
    # Required for async engine - so override user preferences
    config.postgres.driver = "postgresql+asyncpg"

    uri = choose_uri(metadata, config.postgres)
    args = choose_args(metadata, config.postgres)
    return create_async_engine(
        uri,
        **args,
    )


def configure_postgres(graph):
    engine = make_engine(graph.metadata, graph.config)
    return engine
