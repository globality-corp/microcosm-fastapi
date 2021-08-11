from microcosm_fastapi.logging_data_map import LoggingDataMap
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

        self.logging_data_map.add_entry(self.ns_pizza, self.retrieve_operation.value)
        self.logging_data_map.add_entry(self.ns_pizza_orders, self.retrieve_for_operation.value)

    def test_retrieve_operation_name_for_pizza(self):
        # '/api/v1/pizza/11111111-2222-4d55-3333-444444444444' -> '/api/v1/pizza/{pizza_id}'
        expected_operation_name = "pizza.retrieve.v1"

        example_path = '/api/v1/pizza/11111111-2222-4d55-3333-444444444444'
        example_operation_method = "GET"
        breakpoint()
        actual_operation_name = self.logging_data_map.get_entry(example_operation_method, example_path)





    def test_retrieve_for_operation_name_for_pizza_orders(self):
        # '/api/v1/pizza/11111111-2222-4d55-3333-444444444444/order' -> '/api/v1/pizza/{pizza_id}/order'
        expected_operation_name = "pizza.retrieve_for.order.v1"





