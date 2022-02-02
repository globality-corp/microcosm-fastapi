import ssl

from microcosm_postgres.factories.engine import choose_uri
from sqlalchemy.ext.asyncio import create_async_engine


def choose_connect_args(metadata, config):
    """
    Choose the SSL mode and optional root cert for the connection.
    """
    if not config.require_ssl and not config.verify_ssl:
        return dict(
            ssl="prefer",
        )

    if config.require_ssl and not config.verify_ssl:
        return dict(
            ssl="require",
        )

    if not config.ssl_cert_path:
        raise Exception(
            "SSL certificate path (`ssl_cert_path`) must be configured for verification"
        )

    return dict(
        ssl=ssl.create_default_context(
            capath=config.ssl_cert_path,
        )
    )


def choose_args(metadata, config):
    """
    Choose database connection arguments.
    """
    return dict(
        connect_args=choose_connect_args(metadata, config),
        echo=config.echo,
        max_overflow=config.max_overflow,
        pool_size=config.pool_size,
        pool_timeout=config.pool_timeout,
        # GLOB-60776 - move to microcosm @defaults + deal with postgres / postgres_async bindings
        pool_pre_ping=True,
    )


def make_engine(metadata, config):
    # GLOB-60776 - move to microcosm @defaults + deal with postgres / postgres_async bindings
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
