from fastapi import HTTPException
from typing import Any
import functools
import traceback

from makefun import wraps

from microcosm_fastapi.signature import maybe_modify_signature
from microcosm_fastapi.utils import bind_to_request_state


DEFAULT_SERVER_STATUS_CODE = 500


class ErrorAdapter:
    def __init__(self, error: Any):
        self.error = error

    def __call__(self):
        """
        Converts a microcosm error into a http exception

        """
        return HTTPException(DEFAULT_SERVER_STATUS_CODE)


async def process_func(func, *args, already_contains_request_arg=True, **kwargs):
    request = kwargs['request']
    if not already_contains_request_arg:
        del kwargs['request']

    bind_to_request_state(request, error=None, traceback=None)
    try:
        return await func(*args, **kwargs)
    except Exception as error:
        bind_to_request_state(request, error=error, traceback=traceback.format_exc(limit=10))
        adapter = ErrorAdapter(error)
        raise adapter()


def configure_error_adapter(graph):
    def error_adapter(func):
        new_sig, already_contains_request_arg = maybe_modify_signature(func)

        if already_contains_request_arg:
            # If the func args/kwargs already contain request, then we leave it in
            @functools.wraps(func)
            async def wrapper(*args, **kwargs):
                return await process_func(
                    func,
                    *args,
                    **kwargs
                )

        else:
            # If the func args/kwargs don't already contain request, then we remove it
            @wraps(func, new_sig=new_sig)
            async def wrapper(*args, **kwargs):
                return await process_func(
                    func,
                    *args,
                    already_contains_request_arg=already_contains_request_arg,
                    **kwargs
                )

        return wrapper
    return error_adapter