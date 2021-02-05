from dataclasses import dataclass
from typing import Any, Optional
from microcosm_fastapi.operations import Operation, OperationType
from microcosm_fastapi.naming import name_for


@dataclass
class Namespace:
    subject: Any
    version: Optional[str] = None
    prefix: str = "api"

    def path_for_operation(self, operation: Operation):
        """
        Converts a defined operation (either a `NODE_PATTERN` or `EDGE_PATTERN`)
        into a convention-based URL that can be called on the server.

        (GET, NODE_PATTERN) -> v1/pizza
        (GET, EDGE_PATTERN) -> v1/pizza/pizza_id

        """
        if operation.pattern == OperationType.NODE_PATTERN:
            return "/" + "/".join(self.path_prefix)
        elif operation.pattern == OperationType.EDGE_PATTERN:
            object_id_key = "{" + f"{self.subject_name}_id" + "}"
            return "/" + "/".join(self.path_prefix + [object_id_key])
        else:
            raise ValueError()

    @property
    def path_prefix(self):
        return [
            part
            for part in [self.prefix, self.version, self.subject_name]
            if part
        ]

    @property
    def subject_name(self):
        return name_for(self.subject)
