"""
Metrics extensions for routes.

"""
from functools import partial

from fastapi import Request
from microcosm.api import defaults, typed
from microcosm.config.types import boolean
from microcosm.errors import NotBoundError
from microcosm_metrics.naming import name_for

from microcosm_fastapi.audit import RequestInfo


def get_metrics(graph):
    """
    Fetch the metrics client from the graph.

    Metrics will be disabled if not configured

    """
    try:
        return graph.metrics
    except NotBoundError:
        return None


def normalize_status_code(status_code: int) -> str:
    return str(status_code)[0] + "xx"


def create_route_metrics(graph):
    async def route_metrics(graph, request: Request, call_next):
        response = await call_next(request)

        if getattr(request.state, "request_info", None):
            request_info: RequestInfo = request.state.request_info

            key = "route"
            tags = [
                f"endpoint:{request_info.operation}",
                "backend_type:microcosm_fastapi",
            ]
            if request_info.status_code is not None:
                graph.metrics.increment(
                    name_for(
                        key,
                        "call",
                        "count",
                    ),
                    tags=tags + [f"classifier:{normalize_status_code(request_info.status_code)}"],
                )

            if request_info.timing.get("elapsed_time"):
                elapsed_ms = request_info.timing["elapsed_time"]
                graph.metrics.histogram(
                    name_for(key),
                    elapsed_ms,
                    tags=tags,
                )

        return response

    return partial(route_metrics, graph)


@defaults(
    enabled=typed(boolean, default_value=True),
)
def configure_route_metrics(graph):
    """
    Configure route metrics

    """
    metrics = get_metrics(graph)
    enabled = bool(metrics and metrics.host != "localhost" and graph.config.route_metrics.enabled)
    if enabled:
        graph.app.middleware("http")(create_route_metrics(graph))
