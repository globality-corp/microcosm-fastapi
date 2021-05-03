from contextlib import asynccontextmanager
from functools import wraps

from microcosm_postgres.operations import recreate_all
from sqlalchemy.ext.asyncio import AsyncSession


class SessionContextAsync:
    """
    Save current session in well-known location and provide context management.
    """
    session_maker = None

    def __init__(self, graph, expire_on_commit=False):
        self.graph = graph
        self.expire_on_commit = expire_on_commit

        SessionContextAsync.session_maker = graph.session_maker_async

    def recreate_all(self):
        """
        Recreate all database tables, but only in a testing context.
        """
        if self.graph.metadata.testing:
            recreate_all(self.graph)

    async def __aenter__(self):
        self.session = await SessionContextAsync.session_maker()
        return self.session

    async def __aexit__(self, *args, **kwargs):
        await self.session.close()
        self.session = None


@asynccontextmanager
async def transaction_async(commit=True):
    """
    Wrap a context with a commit/rollback.
    """
    async with SessionContextAsync.session_maker() as session:
        try:
            yield session
            if commit:
                await session.commit()
        except Exception:
            await session.rollback()
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