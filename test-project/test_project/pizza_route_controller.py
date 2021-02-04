from microcosm.api import binding
from microcosm_fastapi.namespaces import Namespace
from microcosm_fastapi.conventions.crud_adapter import CRUDStoreAdapter


@binding("pizza_controller")
class PizzaController(CRUDStoreAdapter):
    def __init__(self, graph):
        super().__init__(graph, graph.pizza_store)
        self.ns = Namespace(
            subject=ServiceOfferingClassification,
            version="v2",
        )

    def create(self, text=None, items=None, company_id=None, **kwargs):
        pass
