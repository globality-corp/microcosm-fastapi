from microcosm_fastapi.namespaces import Namespace
from microcosm_fastapi.operations import Operation, OperationType

class Pizza:
    pass

class Waiter:
    pass


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