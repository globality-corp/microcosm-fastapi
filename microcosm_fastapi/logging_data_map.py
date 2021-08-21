"""
Used to store information that useful for audit logging purposes

"""
from typing import Optional, Tuple
from dataclasses import dataclass

from microcosm_fastapi.namespaces import Namespace
from microcosm_fastapi.operations import OperationInfo


@dataclass(frozen=True)
class LoggingInfo:
    operation_name: Optional[str] = None
    function_name: Optional[str] = None


class LoggingDataMap:
    def __init__(self):
        self.data_map = {}

    def add_entry(self, namespace: Namespace, operation: OperationInfo, function_name: str):
        operation_name = namespace.generate_operation_name_for_logging(operation)
        key = self._generate_key_from_namespace(namespace, operation.method)
        self.data_map[key] = LoggingInfo(operation_name, function_name)

    def get_entry(self, url_path: str, operation_method: str) -> LoggingInfo:
        key = self._generate_key_from_path_url(url_path, operation_method)
        try:
            return self.data_map[key]
        except KeyError:
            # Return empty LoggingInfo
            return LoggingInfo()

    def _generate_key_from_path_url(self, path: str, operation_method: str) -> Tuple[str, str, Optional[str], str]:
        # single subject -> key = ('v1', 'pizza', None, 'GET')
        # subject + object -> key = ('v1', 'pizza', 'order', 'GET')

        # We only care about paths that start with 'api/v'
        if not path.startswith('/api/v'):
            return None

        path_parts = path.split('/')
        if len(path_parts) == 6:
            # Must be an edge pattern
            return (path_parts[2], path_parts[3], path_parts[5], operation_method)

        # Must be a node pattern
        return (path_parts[2], path_parts[3], None, operation_method)

    def _generate_key_from_namespace(self, namespace: Namespace, operation_method) -> Tuple[str, str, Optional[str], str]:
        # single subject -> key = ('v1', 'pizza', None, 'GET')
        # subject + object -> key = ('v1', 'pizza', 'order', 'GET')
        return (namespace.version, namespace.subject_name, namespace.object_name, operation_method)


def configure_logging_data_map(graph):
    return LoggingDataMap()
