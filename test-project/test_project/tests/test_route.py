import asyncio
from asyncio import get_event_loop
from unittest.mock import ANY, patch

import pytest
from fastapi.testclient import TestClient
from microcosm_postgres.context import transaction, SessionContext
from microcosm_postgres.identifiers import new_object_id
from microcosm_postgres.operations import recreate_all
from test_project.app import create_app
from test_project.pizza_model import Pizza


class TestRoute:
    def setup_method(self):
        self.graph = create_app(testing=True)
        recreate_all(self.graph)

        self.client = TestClient(self.graph.app)

        self.pizza_id = new_object_id()

    @pytest.mark.asyncio
    async def test_search(self):
        await self.create_pizza_object()

        # response = self.client.get("/api/v1/pizza")
        # assert response.status_code == 200
        # assert response.json()["count"] == 1
        # assert response.json()["items"][0] == dict(
        #     id=ANY,
        #     price=5.0,
        #     toppings="cheese",
        # )

    @pytest.mark.asyncio
    async def test_retrieve(self):
        await self.create_pizza_object()

        # response = self.client.get(f"/api/v1/pizza/{self.pizza_id}")
        # assert response.status_code == 200
        # assert response.json() == dict(
        #     id=ANY,
        #     price=5.0,
        #     toppings="cheese",
        # )

    def test_create(self):
        response = self.client.post(
            f"/api/v1/pizza",
            json=dict(
                toppings="pepperoni"
            )
        )
        assert response.status_code == 201
        assert response.json() == dict(
            id=ANY,
            price=5.0,
            toppings="pepperoni",
        )

    async def create_pizza_object(self):
        new_pizza = Pizza(toppings="cheese")

        with patch.object(self.graph.pizza_store, "new_object_id") as mocked:
            mocked.return_value = self.pizza_id

            with SessionContext(self.graph), transaction():
                pizza_obj = await self.graph.pizza_store.create(new_pizza)
