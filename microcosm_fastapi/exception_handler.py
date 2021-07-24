from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException
from fastapi.exception_handlers import http_exception_handler

from microcosm_fastapi.errors import (
    extract_context,
    extract_error_message,
    extract_retryable,
    extract_status_code,
)


async def my_exception_handler(request: Request, exception):
    """
    Catches exceptions and converts them into JSON responses that can be returned back to the client
    to fit in with existing microcosm conventions

    """
    error = getattr(request.state, 'error', None)
    if error is not None:
        response_content = {
            "code": extract_status_code(error),
            "context": extract_context(error),
            "message": extract_error_message(error),
            "retryable": extract_retryable(error)
        }
        return JSONResponse(status_code=response_content["code"], content=response_content)
    else:
        # default exception flow
        return await http_exception_handler(request, exception)




def configure_global_exception_handler(graph):
    """
    Configure gobal exception handler - i.e this exception handler is there to catch all exceptions
    """
    # new stuff
    # https://python.plainenglish.io/3-ways-to-handle-errors-in-fastapi-that-you-need-to-know-e1199e833039
    graph.app.exception_handler(StarletteHTTPException)(my_exception_handler)