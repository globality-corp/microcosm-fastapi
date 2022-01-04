from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker


def configure_session_maker(graph):
    # expire_on_commit=False
    # In async settings, we don't want SQLAlchemy to issue new SQL queries
    # to the database when accessing already commited objects.
    return sessionmaker(
        graph.postgres_async,
        class_=AsyncSession,
        expire_on_commit=False,
    )
