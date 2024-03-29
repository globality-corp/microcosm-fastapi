from microcosm.api import binding
from test_project.pizza_model import Pizza

from microcosm_fastapi.database.store import StoreAsync


@binding("pizza_store")
class PizzaStore(StoreAsync):

    def __init__(self, graph):
        print(dir(Pizza))
        print(type(Pizza.__table__))
        super().__init__(
            graph,
            Pizza,
        )
