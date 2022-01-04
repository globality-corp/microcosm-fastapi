"""
Naming conventions
"""
from inspect import isclass
from typing import Any
from urllib.parse import (
    parse_qsl,
    urlencode,
    urlparse,
    urlunparse,
)

from inflection import underscore


def name_for(obj):
    """
    Get a standard name for a given object, using python's snake case notation.

    Allows overriding of default names using the `__alias__` attribute.
    """
    if isinstance(obj, str):
        return obj

    cls = obj if isclass(obj) else obj.__class__

    if hasattr(cls, "__alias__"):
        return underscore(cls.__alias__)
    else:
        return underscore(cls.__name__)


def to_camel(snake_str):
    first, *others = snake_str.split("_")
    return "".join([first.lower(), *map(str.title, others)])


def join_url_with_parameters(url, params):
    url_parts = list(urlparse(url))

    # Merge in new params with the previous params
    query = dict(parse_qsl(url_parts[4]))
    query.update(params)

    url_parts[4] = urlencode(query)

    return urlunparse(url_parts)


def collection_path_for(name: Any) -> str:
    """
    Get a path for a collection of things.

    """
    return f"/{name_for(name)}"


def singleton_path_for(name: Any) -> str:
    """
    Get a path for a singleton thing.

    """
    return f"/{name_for(name)}"


def instance_path_for(name: Any, identifier_key: str = None) -> str:
    """
    Get a path for thing.

    """
    if identifier_key:
        return f"/{name_for(name)}/{identifier_key}"
    else:
        return f"/{name_for(name)}/{{{name_for(name)}_id}}"


def alias_path_for(name):
    """
    Get a path for an alias to a thing

    """
    return f"/{name_for(name)}/{{{name_for(name)}_name}}"


def relation_path_for(from_name: Any, to_name: Any, identifier_key: str = None) -> str:
    """
    Get a path relating a thing to another.

    """
    if identifier_key:
        return f"/{name_for(to_name)}/{identifier_key}/{name_for(to_name)}"
    else:
        return f"/{name_for(from_name)}/{{{name_for(from_name)}_id}}/{name_for(to_name)}"
