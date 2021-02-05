from microcosm.api import binding
#from microcosm_postgres.store import Store
from microcosm_fastapi.store import Store

from test_project.pizza_model import Pizza


@binding("pizza_store")
class PizzaStore(Store):

    def __init__(self, graph):
        print(dir(Pizza))
        print(type(Pizza.__table__))
        super().__init__(
            graph,
            Pizza,
        )
