"""
Naming conventions
"""
from inspect import isclass

from inflection import underscore
from urllib.parse import urlparse, urlencode, urlunparse


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


def join_url_with_parameters(url, query):
    url_parts = list(urlparse(url))
    url_parts[4] = urlencode(query)

    return urlunparse(url_parts)
