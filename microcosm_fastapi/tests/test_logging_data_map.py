from microcosm_fastapi.logging_data_map import LoggingDataMap, LoggingInfo
from microcosm_fastapi.namespaces import Namespace
from microcosm_fastapi.operations import Operation


class TestLoggingDataMap:
    def setup(self):

        self.logging_data_map = LoggingDataMap()
        self.ns_pizza = Namespace(
            subject="pizza",
            version="v1",
        )
        self.ns_pizza_orders = Namespace(
            subject="pizza",
            version="v1",
            object_="order"
        )
        self.retrieve_operation = Operation.Retrieve
        self.retrieve_for_operation = Operation.RetrieveFor
        self.retrieve_function_name = "retrieve"

        self.logging_data_map.add_entry(self.ns_pizza, self.retrieve_operation.value, self.retrieve_function_name)
        self.logging_data_map.add_entry(self.ns_pizza_orders, self.retrieve_for_operation.value, self.retrieve_function_name)

    def test_retrieve_operation_name_for_pizza(self):
        expected_operation_name = "pizza.retrieve.v1"
        example_path = '/api/v1/pizza/11111111-2222-4d55-3333-444444444444'
        example_operation_method = "GET"

        logging_info: LoggingInfo = self.logging_data_map.get_entry(example_path, example_operation_method)
        assert logging_info.operation_name == expected_operation_name

    def test_retrieve_for_operation_name_for_pizza_orders(self):
        expected_operation_name = "pizza.retrieve_for.order.v1"
        example_path = '/api/v1/pizza/11111111-2222-4d55-3333-444444444444/order'
        example_operation_method = "GET"

        logging_info: LoggingInfo = self.logging_data_map.get_entry(example_path, example_operation_method)
        assert logging_info.operation_name == expected_operation_name





