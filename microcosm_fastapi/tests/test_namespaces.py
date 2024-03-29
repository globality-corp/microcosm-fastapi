from types import SimpleNamespace

import pytest

from microcosm_fastapi.namespaces import Namespace
from microcosm_fastapi.operations import Operation


class Pizza:
    pass


class Waiter:
    pass


class FakeRequest:
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
    @pytest.fixture
    def base_fixture(self):
        pizza_ns = Namespace(
            subject=Pizza,
            version="v1",
        )
        sn = SimpleNamespace(ns=pizza_ns)
        return sn

    def test_extract_https_hostname(self, base_fixture):
        request = FakeRequest(url="https://www.google.com")
        actual_result = base_fixture.ns.extract_hostname_from_request(request)
        expected_result = "https://www.google.com"
        assert actual_result == expected_result

    def test_extract_http_hostname(self, base_fixture):
        request = FakeRequest(url="http://www.google.com")
        actual_result = base_fixture.ns.extract_hostname_from_request(request)
        expected_result = "http://www.google.com"
        assert actual_result == expected_result

    def test_url_for(self, base_fixture):
        request = FakeRequest(url="http://www.my-service.com")
        operation = Operation.Search.value
        actual_result = base_fixture.ns.url_for(request, operation)
        expected_result = "http://www.my-service.com/api/v1/pizza"
        assert actual_result == expected_result
