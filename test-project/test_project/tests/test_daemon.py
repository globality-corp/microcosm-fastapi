from test_project.daemons.pizza_daemon.main import PizzaDaemon
from unittest.mock import Mock, patch
from test_project.daemons.pizza_daemon.handler import PizzaModel
import pytest

class TestDaemon:
    def setup(self):
        self.graph = PizzaDaemon.create_for_testing().graph
        self.handler = self.graph.pizza_daemon_handler

        self.message = dict(uri="http://pizza.uri")

    @pytest.mark.asyncio
    async def test_pizza_daemon(self):
        with patch.object(self.handler, "get_resource") as mocked_get_resource:
            mocked_get_resource.return_value = PizzaModel(
                toppings="cheese"
            )

            assert await self.handler(self.message) == True

    @pytest.mark.asyncio
    async def test_pizza_daemon_raise_exception(self):
        with patch.object(self.handler, "get_resource") as mocked_get_resource:
            mocked_get_resource.return_value = PizzaModel(
                toppings="pineapple"
            )

            with pytest.raises(ValueError):
                await self.handler(self.message)
