from dataclasses import dataclass
from enum import Enum, unique
from typing import Callable

from microcosm_fastapi.naming import (
    collection_path_for,
    instance_path_for,
    relation_path_for,
    singleton_path_for,
)


@unique
class OperationType(Enum):
    NODE_PATTERN = "{subject}.{operation}.{version}"
    EDGE_PATTERN = "{subject}.{operation}.{object_}.{version}"


@dataclass
class OperationInfo:
    name: str
    method: str
    pattern: OperationType
    default_code: int
    naming_convention: Callable


@unique
class Operation(Enum):
    # collection operations
    Search = OperationInfo("search", "GET", OperationType.NODE_PATTERN, 200, singleton_path_for)
    Count = OperationInfo("count", "HEAD", OperationType.NODE_PATTERN, 200, singleton_path_for)
    Create = OperationInfo("create", "POST", OperationType.NODE_PATTERN, 201, singleton_path_for)

    # instance operations
    Retrieve = OperationInfo("retrieve", "GET", OperationType.NODE_PATTERN, 200, instance_path_for)
    Delete = OperationInfo("delete", "DELETE", OperationType.NODE_PATTERN, 204, instance_path_for)
    Replace = OperationInfo("replace", "PUT", OperationType.NODE_PATTERN, 200, instance_path_for)
    Update = OperationInfo("update", "PATCH", OperationType.NODE_PATTERN, 200, instance_path_for)

    # batch operations
    DeleteBatch = OperationInfo(
        "delete_batch", "DELETE", OperationType.NODE_PATTERN, 204, collection_path_for
    )
    UpdateBatch = OperationInfo(
        "update_batch", "PATCH", OperationType.NODE_PATTERN, 200, collection_path_for
    )
    CreateCollection = OperationInfo(
        "create_collection", "POST", OperationType.NODE_PATTERN, 200, collection_path_for
    )
    SavedSearch = OperationInfo(
        "saved_search", "POST", OperationType.NODE_PATTERN, 200, collection_path_for
    )

    # relation operations
    CreateFor = OperationInfo(
        "create_for", "POST", OperationType.EDGE_PATTERN, 201, relation_path_for
    )
    DeleteFor = OperationInfo(
        "delete_for", "DELETE", OperationType.EDGE_PATTERN, 204, relation_path_for
    )
    ReplaceFor = OperationInfo(
        "replace_for", "PUT", OperationType.EDGE_PATTERN, 200, relation_path_for
    )
    RetrieveFor = OperationInfo(
        "retrieve_for", "GET", OperationType.EDGE_PATTERN, 200, relation_path_for
    )
    SearchFor = OperationInfo(
        "search_for", "GET", OperationType.EDGE_PATTERN, 200, relation_path_for
    )
    UpdateFor = OperationInfo(
        "update_for", "PATCH", OperationType.EDGE_PATTERN, 200, relation_path_for
    )
