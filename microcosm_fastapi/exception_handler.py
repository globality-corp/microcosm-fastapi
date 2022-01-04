import traceback
from typing import Any, Awaitable, Callable

from fastapi import Request
from fastapi.responses import JSONResponse
from microcosm.object_graph import ObjectGraph

from microcosm_fastapi.errors import ParsedException
from microcosm_fastapi.utils import bind_to_request_state


async def global_exception_handler(
    request: Request, call_next: Callable[[Request], Awaitable[Any]]
) -> JSONResponse:
    """
    Catches exceptions and converts them into JSON responses that can be returned back to the client
    to fit in with existing microcosm conventions

    """
    try:
        return await call_next(request)
    except Exception as error:
        bind_to_request_state(request, error=error, traceback=traceback.format_exc(limit=10))
        parsed_exception = ParsedException(error)
        return JSONResponse(
            status_code=parsed_exception.status_code, content=parsed_exception.to_dict()
        )


def configure_global_exception_handler(graph: ObjectGraph) -> None:
    """
    Configure global exception middleware - i.e this middleware will catch all exceptions

    """
    graph.app.middleware("http")(global_exception_handler)
