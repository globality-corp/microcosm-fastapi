"""
Configuring session injection

"""
import functools
from inspect import signature, Parameter
from copy import deepcopy
from sqlalchemy.orm import Session
from fastapi import Depends
from makefun import wraps
from sqlalchemy.ext.asyncio import AsyncSession
from contextlib import asynccontextmanager


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
    return Parameter(SESSION_PARAMETER_NAME, kind=Parameter.POSITIONAL_OR_KEYWORD, annotation=Session, default=Depends(get_session_partial))


def modify_signature(graph, sig):
    new_sig = deepcopy(sig)
    params = list(sig.parameters.values())

    params_without_session = [param for param in params if not determine_if_session_param(param)]
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
