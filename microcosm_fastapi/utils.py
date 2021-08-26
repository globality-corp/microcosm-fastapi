from fastapi import Request


def bind_to_request_state(request: Request, **kwargs):
    """
    Takes in a set of kwargs and binds them to request state

    """
    for key, value in kwargs.items():
        setattr(request.state, key, value)


class AsyncIteratorWrapper:
    def __init__(self, obj):
        self._it = iter(obj)

    def __aiter__(self):
        return self

    async def __anext__(self):
        try:
            value = next(self._it)
        except StopIteration:
            raise StopAsyncIteration
        return value
