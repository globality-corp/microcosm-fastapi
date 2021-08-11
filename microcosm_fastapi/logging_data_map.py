from microcosm.api import binding


# @binding("logging_data_map")
class LoggingDataMap:
    def __init__(self):
        self.data_map = {}

    def add_entry(self, namespace, operation):
        url_path = namespace.path_for_operation(operation)
        operation_name = namespace.generate_operation_name_for_logging(operation)
        key = (operation.method, url_path)
        self.data_map[key] = operation_name

        # let's store it either like ['pizza']['GET']
        # or like ['pizza']['order']['GET']

    def get_entry(self, operation_method, url_path):
        key = (operation_method, url_path)
        try:
            return self.data_map[key]
        except KeyError:
            return None

    def match_

    def _generate_key_from_request_url(self, path, operation_method):
        # single subject -> key = ('pizza', 'GET')
        # subject + object -> key = ('pizza', 'order', 'GET')
        pass

    def _generate_key_from_namespace(self, namespace, operation_method):
        # single subject -> key = ('pizza', 'GET')
        # subject + object -> key = ('pizza', 'order', 'GET')
        key = (namespace.subject,

        path_parts = path.split('/')
        if len(path_parts) == 5:
            # Must be a node pattern
            key = ()
        elif len(path_parts) == 6:
            # Must be an edge pattern

        else:
            raise Exception('Unable to parse the url path. Please investigate')


def configure_logging_data_map(graph):
    return LoggingDataMap()
