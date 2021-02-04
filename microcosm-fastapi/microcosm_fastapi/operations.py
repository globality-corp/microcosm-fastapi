from collections import namedtuple
from enum import Enum, unique
from dataclasses import dataclass


# NB: Namespace.parse_endpoint requires that operation is the second argument
NODE_PATTERN = "{subject}.{operation}.{version}"
EDGE_PATTERN = "{subject}.{operation}.{object_}.{version}"


class OperationInfo:
    name: str
    method: str
    pattern: str
    default_code: int


@unique
class Operation(Enum):
    # collection operations
    Search = OperationInfo("search", "GET", NODE_PATTERN, 200)
    Count = OperationInfo("count", "HEAD", NODE_PATTERN, 200)
    Create = OperationInfo("create", "POST", NODE_PATTERN, 201)

    # instance operations
    Retrieve = OperationInfo("retrieve", "GET", NODE_PATTERN, 200)
    Delete = OperationInfo("delete", "DELETE", NODE_PATTERN, 204)
    Replace = OperationInfo("replace", "PUT", NODE_PATTERN, 200)
    Update = OperationInfo("update", "PATCH", NODE_PATTERN, 200)

    @classmethod
    def from_name(cls, name):
        for operation in cls:
            if operation.value.name.lower() == name.lower():
                return operation
        else:
            raise ValueError(name)

    @property
    def endpoint_pattern(self):
        """
        Convert the operation's pattern into a regex matcher.
        """
        parts = self.value.pattern.split(".")
        return "[.]".join(
            "(?P<{}>[^.]*)".format(part[1:-1])
            for part in parts
        )