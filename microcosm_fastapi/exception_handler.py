from fastapi import Request
from fastapi.responses import JSONResponse

from microcosm_fastapi.errors import (
    extract_context,
    extract_error_message,
    extract_retryable,
    extract_status_code,
)
from microcosm_fastapi.utils import bind_to_request_state
import traceback


async def global_exception_handler(request: Request, call_next):
    """
    Catches exceptions and converts them into JSON responses that can be returned back to the client
    to fit in with existing microcosm conventions

    """
    try:
        return await call_next(request)
    except Exception as error:
        bind_to_request_state(request, error=error, traceback=traceback.format_exc(limit=10))
        response_content = {
            "code": extract_status_code(error),
            "context": extract_context(error),
            "message": extract_error_message(error),
            "retryable": extract_retryable(error)
        }
        return JSONResponse(status_code=response_content["code"], content=response_content)


def configure_global_exception_handler(graph):
    """
    Configure global exception middleware - i.e this middleware will catch all exceptions

    """
    graph.app.middleware('http')(global_exception_handler)