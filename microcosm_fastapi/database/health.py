"""
Simple Postgres health check.

"""
from alembic.script import ScriptDirectory


async def check_health(graph):
    """
    Basic database health check.

    """
    async with graph.session_maker_async() as session:
        await session.execute("SELECT 1;")


async def check_alembic(graph):
    """
    Check connectivity to an alembic database.

    Returns the current migration.

    """
    async with graph.session_maker_async() as session:
        result = await session.execute(
            "SELECT version_num FROM alembic_version LIMIT 1;",
        )
        return result.scalar()


async def get_current_head_version(graph):
    """
    Returns the current head version.

    """
    script_dir = ScriptDirectory("/", version_locations=[graph.metadata.get_path("migrations")])
    return script_dir.get_current_head()
