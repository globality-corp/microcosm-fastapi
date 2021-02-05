from microcosm_fastapi.namespaces import Namespace
from microcosm_fastapi.operations import Operation
from typing import Callable, Dict

def configure_crud(graph, namespace: Namespace, mappings: Dict[Operation, Callable]):
    """
    Mounts the given mappings into the graph URL.

    :param mappings: Dict[]

    """
    for operation, fn in mappings.items():
        optional_configuration = dict()

        # If the user's function signature has provided a return type via a python
        # annotation, they want to serialize their response with this type
        if "return" in fn.__annotations__:
            optional_configuration["response_model"] = fn.__annotations__["return"]

        url_path = namespace.path_for_operation(operation)
        print("MOUNT", operation, url_path)
        graph.app.get(url_path, **optional_configuration)(fn)
