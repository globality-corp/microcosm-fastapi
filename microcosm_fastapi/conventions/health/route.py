from microcosm.api import defaults, typed
from microcosm.config.types import boolean

from microcosm_fastapi.conventions.health.models import Health
from microcosm_fastapi.conventions.health.resources import HealthSchema


@defaults(
    include_build_info=typed(boolean, default_value=True),
)
def configure_health(graph):
    """
    Mount the health endpoint to the graph

    """
    health_container = Health(graph, graph.config.health_convention.include_build_info)

    @graph.app.get("/api/health")
    async def configure_health_endpoint(full: bool = False) -> HealthSchema:
        response_data = await health_container.to_object(full=full)

        if not response_data.ok:
            raise

        return response_data

    return health_container
