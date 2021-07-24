"""
Functions to do with modifying/updating function signatures

"""
from inspect import signature, Parameter
from copy import deepcopy

from fastapi import Request


def maybe_modify_signature(func):
    """
    Maybe modifies signature of function to include the request:Request argument

    """
    old_signature = signature(func)

    new_signature = deepcopy(old_signature)
    params = list(new_signature.parameters.values())
    has_request_param = False
    for param in params:
        if param.name == 'request':
            has_request_param = True

    if not has_request_param:
        params.append(Parameter('request', kind=Parameter.POSITIONAL_OR_KEYWORD, annotation=Request))
        return new_signature.replace(parameters=params), has_request_param

    return new_signature, has_request_param