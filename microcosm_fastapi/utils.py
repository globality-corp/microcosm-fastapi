from fastapi import Request


def bind_to_request_state(request: Request, **kwargs):
    """
    Takes in a set of kwargs and binds them to request state

    """
    for key, value in kwargs.items():
        setattr(request.state, key, value)