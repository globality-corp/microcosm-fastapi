from contextlib import asynccontextmanager
from functools import wraps

from microcosm_postgres.operations import recreate_all
from sqlalchemy.ext.asyncio import AsyncSession


class SessionContextAsync:
    """
    Save current session in well-known location and provide context management.
    """
    session = None

    def __init__(self, graph, expire_on_commit=False):
        self.graph = graph
        self.expire_on_commit = expire_on_commit

    def open(self):
        SessionContextAsync.session = AsyncSession(self.graph.postgres_async)
        return self

    async def close(self):
        if SessionContextAsync.session:
            await SessionContextAsync.session.close()
            SessionContextAsync.session = None

    def recreate_all(self):
        """
        Recreate all database tables, but only in a testing context.
        """
        if self.graph.metadata.testing:
            recreate_all(self.graph)

    @classmethod
    def make(cls, graph, expire_on_commit=False):
        """
        Create an opened context.
        """
        return cls(graph, expire_on_commit).open()

    # context manager

    def __enter__(self):
        return self.open()

    def __exit__(self, *args, **kwargs):
        self.close()


@asynccontextmanager
async def transaction_async(commit=True):
    """
    Wrap a context with a commit/rollback.
    """
    try:
        yield SessionContextAsync.session
        if commit:
            await SessionContextAsync.session.commit()
    except Exception:
        if SessionContextAsync.session:
            await SessionContextAsync.session.rollback()
        raise


def transactional_async(func):
    """
    Decorate a function call with a commit/rollback and pass the session as the first arg.
    """
    @wraps(func)
    async def wrapper(*args, **kwargs):
        async with transaction_async():
            return await func(*args, **kwargs)
    return wrapper


def maybe_transactional_async(func):
    """
    Variant of `transactional` that will not commit if there's an argument `commit` with a falsey value.
    Useful for dry-run style operations.
    """
    @wraps(func)
    async def wrapper(*args, **kwargs):
        commit = kwargs.get("commit", True)
        async with transaction_async(commit=commit):
            return await func(*args, **kwargs)
    return wrapper