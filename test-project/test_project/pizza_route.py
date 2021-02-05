from microcosm.api import binding
from microcosm_fastapi.namespaces import Namespace
from microcosm_fastapi.operations import Operation
from microcosm_fastapi.conventions.crud_adapter import CRUDStoreAdapter
from microcosm_fastapi.conventions.crud import configure_crud
from test_project.pizza_model import Pizza
from microcosm_postgres.context import transactional
from test_project.pizza_resources import NewPizzaSchema, PizzaSchema
from microcosm_fastapi.conventions.schemas import SearchSchema
from uuid import UUID
from typing import List


@binding("pizza_route")
class PizzaController(CRUDStoreAdapter):
    def __init__(self, graph):
        super().__init__(graph, graph.pizza_store)

        ns = Namespace(
            subject=Pizza,
            version="v1",
        )

        mappings = {
            #Operation.Create: transactional(self.create),
            Operation.Retrieve: self.retrieve,
            Operation.Search: self.search,
        }
        configure_crud(graph, ns, mappings)

    async def retrieve(self, pizza_id: UUID) -> PizzaSchema:
        return await super()._retrieve(pizza_id)

    async def search(self, limit: int = 20, offset: int = 0) -> SearchSchema(PizzaSchema):
        #return super()._search(limit=limit, offset=offset)
        values = await super()._search(limit=limit, offset=offset)
        print(values)
        return values
        print("ITEM", values["items"][0])
        return values["items"]
        #values = await self.store.session.query(Pizza).filter().offset(10).all()
        #print(values)
        return dict(
            testing=True
        )