import pytest
import os
from unittest import mock

from microcosm_fastapi.namespaces import Namespace
from microcosm_fastapi.operations import Operation, OperationType
from fastapi import Request


class Pizza:
    pass


class Waiter:
    pass


class FakeRequest():
    def __init__(self, url):
        self.url = url


def test_create_path_for_search_operation():
    pizza_namespace = Namespace(
        subject=Pizza,
        version="v1",
    )
    operation = Operation.Search.value
    api_path = pizza_namespace.path_for_operation(operation)
    assert api_path == "/api/v1/pizza"


def test_create_path_for_retrieve_operation():
    pizza_namespace = Namespace(
        subject=Pizza,
        version="v1",
    )
    operation = Operation.Retrieve.value
    api_path = pizza_namespace.path_for_operation(operation)
    assert api_path == "/api/v1/pizza/{pizza_id}"


def test_create_path_for_delete_operation():
    pizza_namespace = Namespace(
        subject=Pizza,
        version="v1",
    )
    operation = Operation.Delete.value
    api_path = pizza_namespace.path_for_operation(operation)
    assert api_path == "/api/v1/pizza/{pizza_id}"


def test_create_path_for_create_collection_operation():
    pizza_namespace = Namespace(
        subject=Pizza,
        version="v1",
    )
    operation = Operation.CreateCollection.value
    api_path = pizza_namespace.path_for_operation(operation)
    assert api_path == "/api/v1/pizza"


def test_create_path_for_create_for_operation():
    pizza_namespace = Namespace(
        subject=Pizza,
        version="v1",
        object_=Waiter,
    )
    operation = Operation.CreateFor.value
    api_path = pizza_namespace.path_for_operation(operation)
    assert api_path == "/api/v1/pizza/{pizza_id}/waiter"


def test_create_path_for_search_for_operation():
    pizza_namespace = Namespace(
        subject=Pizza,
        version="v1",
        object_=Waiter,
    )
    operation = Operation.SearchFor.value
    api_path = pizza_namespace.path_for_operation(operation)
    assert api_path == "/api/v1/pizza/{pizza_id}/waiter"


class TestHostnameExtraction:

    @pytest.fixture()
    def env_vars(self):
        with mock.patch.dict(os.environ, {"MICROCOSM_ENVIRONMENT": "dev"}):
            yield

    @pytest.fixture
    def base_fixture(self, base):
        pizza_ns = Namespace(
            subject=Pizza,
            version="v1",
        )
        base.add_attrs(
            ns=pizza_ns
        )
        return base

    def test_extract_https_hostname(self, base_fixture, env_vars):
        request = FakeRequest(url="https://www.google.com")
        actual_result = base_fixture.ns.extract_hostname_from_request(request)
        expected_result = "https://www.google.com"
        assert actual_result == expected_result

    def test_extract_http_hostname(self, base_fixture, env_vars):
        request = FakeRequest(url="http://www.google.com")
        actual_result = base_fixture.ns.extract_hostname_from_request(request)
        expected_result = "https://www.google.com"
        assert actual_result == expected_result

    def test_extract_https_hostname_no_environment_set(self, base_fixture):
        request = FakeRequest(url="https://www.google.com")
        actual_result = base_fixture.ns.extract_hostname_from_request(request)
        expected_result = "https://www.google.com"
        assert actual_result == expected_result

    def test_extract_http_hostname_no_environment_set(self, base_fixture):
        request = FakeRequest(url="http://www.google.com")
        actual_result = base_fixture.ns.extract_hostname_from_request(request)
        expected_result = "http://www.google.com"
        assert actual_result == expected_result





