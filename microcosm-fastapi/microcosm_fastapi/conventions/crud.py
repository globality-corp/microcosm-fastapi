from microcosm_fastapi.namespaces import Namespace
from microcosm_fastapi.operations import Operation
from typing import Callable, Dict


def configure_crud(graph, namespace: Namespace, mappings: Dict[Operation, Callable]):
    """
    Mounts the supported namespace operations into the FastAPI graph, following our
    conventions for setting up URL patterns.

    :param mappings: Dict[
        Operation: function
    ]

    """
    for operation, fn in mappings.items():
        operation = operation.value

        # Configuration params for this swagger endpoint
        # Some are generated dynamically depending on the specific configurations
        # and user definitions, which we add next
        configuration = dict(
            operation_id=operation.name,
            status_code=operation.default_code,
        )

        # If the user's function signature has provided a return type via a python
        # annotation, they want to serialize their response with this type
        if "return" in fn.__annotations__:
            configuration["response_model"] = fn.__annotations__["return"]

        # Construct the unique path for this operation & object namespace
        url_path = namespace.path_for_operation(operation)

        method_mapping = {
            "GET": graph.app.get,
            "POST": graph.app.post,
            "PATCH": graph.app.patch,
            "DELETE": graph.app.delete,
            "OPTIONS": graph.app.options,
            "HEAD": graph.app.head,
            "TRACE": graph.app.trace,
        }
        method_mapping[operation.method](url_path, **configuration)(fn)
