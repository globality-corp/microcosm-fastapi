from collections import namedtuple
from dataclasses import dataclass
from enum import Enum, unique


@unique
class OperationType(Enum):
    NODE_PATTERN = "NODE_PATTERN"
    EDGE_PATTERN = "EDGE_PATTERN"


@dataclass
class OperationInfo:
    name: str
    method: str
    pattern: OperationType
    default_code: int


@unique
class Operation(Enum):
    # collection operations
    Search = OperationInfo("search", "GET", OperationType.NODE_PATTERN, 200)
    Count = OperationInfo("count", "HEAD", OperationType.NODE_PATTERN, 200)
    Create = OperationInfo("create", "POST", OperationType.NODE_PATTERN, 201)

    # instance operations
    Retrieve = OperationInfo("retrieve", "GET", OperationType.EDGE_PATTERN, 200)
    Delete = OperationInfo("delete", "DELETE", OperationType.EDGE_PATTERN, 204)
    Replace = OperationInfo("replace", "PUT", OperationType.EDGE_PATTERN, 200)
    Update = OperationInfo("update", "PATCH", OperationType.EDGE_PATTERN, 200)
