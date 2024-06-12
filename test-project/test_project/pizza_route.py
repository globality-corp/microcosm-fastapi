from typing import List
from uuid import UUID

from microcosm.api import binding
from test_project.pizza_model import Pizza
from test_project.pizza_resources import NewPizzaSchema, PizzaSchema

from microcosm_fastapi.conventions.crud import configure_crud
from microcosm_fastapi.conventions.crud_adapter import CRUDStoreAdapter
from microcosm_fastapi.conventions.schemas import SearchSchema
from microcosm_fastapi.namespaces import Namespace
from microcosm_fastapi.operations import Operation


@binding("pizza_route")
class PizzaController(CRUDStoreAdapter):
    def __init__(self, graph):
        super().__init__(graph, graph.pizza_store)

        ns = Namespace(
            subject=Pizza,
            version="v1",
        )

        mappings = {
            Operation.Create: self.create,
            Operation.Retrieve: self.retrieve,
            Operation.Search: self.search,
        }
        configure_crud(graph, ns, mappings)

    async def create(self, pizza: NewPizzaSchema) -> PizzaSchema:
        return await super()._create(pizza)

    async def retrieve(self, pizza_id: UUID) -> PizzaSchema:
        return await super()._retrieve(pizza_id)

    async def search(self, limit: int = 20, offset: int = 0) -> SearchSchema(PizzaSchema):
        return await super()._search(limit=limit, offset=offset)
