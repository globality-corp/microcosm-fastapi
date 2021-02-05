"""
Naming conventions
"""
from inspect import isclass

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
