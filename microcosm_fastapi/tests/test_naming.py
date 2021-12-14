"""
Naming tests.

"""
from hamcrest import assert_that, equal_to, is_

from microcosm_fastapi.naming import (
    alias_path_for,
    collection_path_for,
    instance_path_for,
    name_for,
    relation_path_for,
    singleton_path_for,
)


class FooBar:
    pass


class TheBaz:
    __alias__ = "baz"


def test_name_for():
    cases = [
        ("foo", "foo"),
        (FooBar, "foo_bar"),
        (FooBar(), "foo_bar"),
        (TheBaz, "baz"),
        (TheBaz(), "baz"),
    ]
    for obj, name in cases:
        assert_that(name_for(obj), is_(equal_to(name)))


def test_collection_path():
    assert_that(collection_path_for("foo"), is_(equal_to("/foo")))


def test_singletone_path():
    assert_that(singleton_path_for("foo"), is_(equal_to("/foo")))


def test_instance_path():
    assert_that(instance_path_for("foo"), is_(equal_to("/foo/{foo_id}")))
    assert_that(instance_path_for("foo"), is_(equal_to("/foo/{foo_id}")))


def test_relation_path():
    assert_that(relation_path_for("foo", "bar"), is_(equal_to("/foo/{foo_id}/bar")))
    assert_that(relation_path_for("foo", "bar"), is_(equal_to("/foo/{foo_id}/bar")))


def test_alias_path():
    assert_that(alias_path_for("foo"), is_(equal_to("/foo/{foo_name}")))
