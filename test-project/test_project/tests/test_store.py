from unittest.mock import patch

import pytest
from microcosm_postgres.errors import ModelNotFoundError
from microcosm_postgres.identifiers import new_object_id
from microcosm_postgres.operations import recreate_all

from test_project.app import create_app
from test_project.pizza_model import Pizza


class TestStore:
    def setup(self):
        self.graph = create_app(testing=True)
        recreate_all(self.graph)

        self.pizza_id = new_object_id()

    @pytest.mark.asyncio
    async def test_create(self):
        new_pizza = Pizza(toppings="cheese")

        with patch.object(self.graph.pizza_store, "new_object_id") as mocked:
            mocked.return_value = self.pizza_id

            async with transaction_async():
                pizza_obj = await self.graph.pizza_store.create(new_pizza)

        assert pizza_obj.id == self.pizza_id

    @pytest.mark.asyncio
    async def test_search(self):
        cheese_pizza = Pizza(toppings="cheese")
        pepperoni_pizza = Pizza(toppings="pepperoni")

        async with transaction_async():
            await self.graph.pizza_store.create(cheese_pizza)
            await self.graph.pizza_store.create(pepperoni_pizza)

        pizza_results = await self.graph.pizza_store.search()
        assert len(pizza_results) == 2

    @pytest.mark.asyncio
    async def test_search_first(self):
        cheese_pizza = Pizza(toppings="cheese")
        pepperoni_pizza = Pizza(toppings="pepperoni")

        async with transaction_async():
            await self.graph.pizza_store.create(cheese_pizza)
            await self.graph.pizza_store.create(pepperoni_pizza)

        pizza = await self.graph.pizza_store.search_first()
        assert pizza.toppings == "cheese"

    @pytest.mark.asyncio
    async def test_retrieve(self):
        with patch.object(self.graph.pizza_store, "new_object_id") as mocked:
            mocked.return_value = self.pizza_id

            async with transaction_async():
                new_pizza = Pizza(toppings="cheese")
                await self.graph.pizza_store.create(new_pizza)

        pizza_object = await self.graph.pizza_store.retrieve(self.pizza_id)
        assert pizza_object.id == self.pizza_id
        assert pizza_object.toppings == "cheese"

    @pytest.mark.asyncio
    async def test_delete(self):
        with patch.object(self.graph.pizza_store, "new_object_id") as mocked:
            mocked.return_value = self.pizza_id

            async with transaction_async():
                new_pizza = Pizza(toppings="cheese")
                await self.graph.pizza_store.create(new_pizza)

        await self.graph.pizza_store.retrieve(self.pizza_id)

        await self.graph.pizza_store.delete(self.pizza_id)

        with pytest.raises(ModelNotFoundError):
            await self.graph.pizza_store.retrieve(self.pizza_id)
