"""
Used to store information that useful for audit logging purposes

"""
from dataclasses import dataclass
from typing import Any, Optional, Tuple

from microcosm_fastapi.namespaces import Namespace
from microcosm_fastapi.operations import OperationInfo


@dataclass(frozen=True)
class LoggingInfo:
    operation_name: Optional[str] = None
    function_name: Optional[str] = None

    def is_empty(self) -> bool:
        return self.operation_name is None and self.function_name is None


class LoggingDataMap:
    def __init__(self):
        self.data_map = {}

    def add_entry(self, namespace: Namespace, operation: OperationInfo, function_name: str):
        operation_name = namespace.generate_operation_name_for_logging(operation)
        key = self._generate_key_from_namespace_and_operation(namespace, operation)
        self.data_map[key] = LoggingInfo(operation_name, function_name)

    def get_entry(self, url_path: str, operation_method: str) -> LoggingInfo:
        key = self._generate_key_from_path_url(url_path, operation_method)
        try:
            return self.data_map[key]
        except KeyError:
            # Return empty LoggingInfo
            return LoggingInfo()

    def _generate_key_from_path_url(
        self, path: str, operation_method: str
    ) -> Optional[Tuple[str, str, Optional[str], str, Optional[str]]]:
        # single subject -> key = ("v1", "pizza", None, "GET", None)
        # subject + object -> key = ("v1", "pizza", "order", "GET", None)

        # We only care about paths that start with "api/v"
        if not path.startswith("/api/v"):
            return None

        path_parts = path.split("/")
        if len(path_parts) == 6:
            # Must be an edge pattern
            return (path_parts[2], path_parts[3], path_parts[5], operation_method, None)

        resource_name = self._extract_resource_name(path_parts[3])
        if operation_method == "GET":
            # "GET" is a special case as both retrieve and search have similar keys
            if len(path_parts) == 5:
                # we know that we have a Retrieve operation if there are 5 path_parts
                # e.g ["", "api", "v1", "pizza", "1234"]
                return (path_parts[2], resource_name, None, operation_method, "retrieve")
            elif len(path_parts) == 4:
                return (path_parts[2], resource_name, None, operation_method, "search")

        # Must be a node pattern
        return (path_parts[2], resource_name, None, operation_method, None)

    def _generate_key_from_namespace_and_operation(
        self, namespace: Namespace, operation: OperationInfo
    ) -> Tuple[Optional[str], Any, Any, str, Optional[str]]:
        # single subject -> key = ("v1", "pizza", None, "GET", None)
        # subject + object -> key = ("v1", "pizza", "order", "GET", None)
        optional_identifier = self._get_optional_identifier(operation)
        return (
            namespace.version,
            namespace.subject_name,
            namespace.object_name,
            operation.method,
            optional_identifier,
        )

    def _get_optional_identifier(self, operation: OperationInfo) -> Optional[str]:
        """
        There is a potential clash between search and retrieve so we use an extra identifier
        inside to distinguish between these two methods
        """
        if operation.method == "GET" and operation.name in ["search", "retrieve"]:
            return operation.name
        else:
            return None

    def _extract_resource_name(self, url_path_part: str) -> str:
        # e.g url_path_part -> "pizza?name=margherita"
        return url_path_part.split("?")[0]


def configure_logging_data_map(graph):
    return LoggingDataMap()
