"""
Naming conventions
"""
from inspect import isclass

from inflection import underscore
from urllib.parse import urlparse, urlencode, urlunparse, parse_qsl


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
    first, *others = snake_str.split('_')
    return ''.join([first.lower(), *map(str.title, others)])


def join_url_with_parameters(url, params):
    url_parts = list(urlparse(url))

    # Merge in new params with the previous params
    query = dict(parse_qsl(url_parts[4]))
    query.update(params)

    url_parts[4] = urlencode(query)

    return urlunparse(url_parts)


def collection_path_for(name):
    """
    Get a path for a collection of things.

    """
    return "/{}".format(
        name_for(name),
    )


def singleton_path_for(name):
    """
    Get a path for a singleton thing.

    """
    return "/{}".format(
        name_for(name),
    )


def instance_path_for(name, identifier_key=None):
    """
    Get a path for thing.

    """
    return "/{}/{{{}}}".format(
        name_for(name),
        identifier_key or "{}_id".format(name_for(name)),
        )


def alias_path_for(name):
    """
    Get a path for an alias to a thing

    """
    return "/{}/{{{}_name}}".format(
        name_for(name),
        name_for(name),
    )


def relation_path_for(from_name, to_name, identifier_key=None):
    """
    Get a path relating a thing to another.

    """
    return "/{}/{{{}}}/{}".format(
        name_for(from_name),
        identifier_key or "{}_id".format(name_for(from_name)),
        name_for(to_name),
        )