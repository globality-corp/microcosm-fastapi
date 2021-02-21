from microcosm_pubsub.conventions import created
from microcosm_pubsub.decorators import handles
from microcosm.api import binding
from microcosm_pubsub.chain import assign

from microcosm_fastapi.pubsub.handlers.chain_handlers import ChainURIHandlerAsync
from microcosm_fastapi.pubsub.chain.chain import ChainAsync
from microcosm_logging.decorators import logger


class PizzaModel:
    def __init__(self, toppings):
        self.toppings = toppings


@logger
@binding("pizza_daemon_handler")
@handles(created("Pizza"))
class PizzaDaemonHandler(ChainURIHandlerAsync):
    def get_chain(self):
        return ChainAsync(
            assign("pizza.toppings").to("toppings"),
            self.process_topping_sync,
            self.process_topping_async,
        )

    def process_topping_sync(self, toppings):
        return toppings + "_processed"

    async def process_topping_async(self, toppings):
        if toppings == "pineapple":
            raise ValueError()
        return toppings + "_processed"

    @property
    def resource_name(self):
        return "pizza"

    @property
    def resource_type(self):
        return PizzaModel
