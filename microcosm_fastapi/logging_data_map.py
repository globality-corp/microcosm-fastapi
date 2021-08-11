"""
Used to store information that useful for audit logging purposes

"""
from typing import Optional
from dataclasses import dataclass


@dataclass(frozen=True)
class LoggingInfo:
    operation_name: Optional[str] = None
    function_name: Optional[str] = None


class LoggingDataMap:
    def __init__(self):
        self.data_map = {}

    def add_entry(self, namespace, operation, function_name):
        operation_name = namespace.generate_operation_name_for_logging(operation)
        operation_method = operation.method

        key = self._generate_key_from_namespace(namespace, operation_method)
        self.data_map[key] = LoggingInfo(operation_name, function_name)

    def get_entry(self, url_path, operation_method):
        key = self._generate_key_from_path_url(url_path, operation_method)
        try:
            return self.data_map[key]
        except KeyError:
            # Return empty LoggingInfo
            return LoggingInfo()

    def _generate_key_from_path_url(self, path, operation_method):
        # single subject -> key = ('v1', 'pizza', 'GET')
        # subject + object -> key = ('v1', 'pizza', 'order', 'GET')
        path_parts = path.split('/')
        if len(path_parts) == 5:
            # Must be a node pattern
            return (path_parts[2], path_parts[3], None, operation_method)
        elif len(path_parts) == 6:
            # Must be an edge pattern
            return (path_parts[2], path_parts[3], path_parts[5], operation_method)
        else:
            raise Exception("Unable to parse url path. Please investigate")

    def _generate_key_from_namespace(self, namespace, operation_method):
        # single subject -> key = ('v1', 'pizza', 'GET')
        # subject + object -> key = ('v1', 'pizza', 'order', 'GET')
        return (namespace.version, namespace.subject_name, namespace.object_name, operation_method)


def configure_logging_data_map(graph):
    return LoggingDataMap()
