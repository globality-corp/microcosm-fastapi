"""
Helper functions for pubsub daemons

"""
from asyncio import get_event_loop
from functools import partial
from typing import Callable


async def run_as_async(sync_fn: Callable, *args, **kwargs):
    loop = get_event_loop()
    request_func = partial(sync_fn, *args, **kwargs)
    return await loop.run_in_executor(None, request_func)
