"""
Configuring session injection

"""
import functools
from contextlib import asynccontextmanager
from copy import deepcopy
from inspect import Parameter, signature

from fastapi import Depends
from makefun import wraps
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session


SESSION_PARAMETER_NAME = "db_session"


@asynccontextmanager
async def get_session(graph):
    session: AsyncSession = graph.session_maker_async()
    try:
        yield session
        await session.commit()
    except Exception:
        await session.rollback()
        raise
    finally:
        await session.close()


def determine_if_session_param(param: Parameter):
    return param.name == SESSION_PARAMETER_NAME


def get_session_param(graph):
    get_session_partial = functools.partial(get_session, graph)
    return Parameter(
        SESSION_PARAMETER_NAME,
        kind=Parameter.POSITIONAL_OR_KEYWORD,
        annotation=Session,
        default=Depends(get_session_partial),
    )


def modify_signature(graph, sig):
    new_sig = deepcopy(sig)
    params = list(sig.parameters.values())

    params_without_session = [
        param
        for param in params
        if not determine_if_session_param(param)
    ]
    if len(params) == len(params_without_session):
        # We don't have a session_db param so just return original function signature
        return sig

    params_without_session.append(get_session_param(graph))
    return new_sig.replace(parameters=params_without_session)


def configure_session_injection(graph):
    def session_injection(fn):
        sig = signature(fn)
        new_sig = modify_signature(graph, sig)

        @wraps(fn, new_sig=new_sig)
        async def decorator(*args, **kwargs):
            return await fn(*args, **kwargs)

        return decorator

    return session_injection
