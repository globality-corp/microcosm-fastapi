from uuid import UUID

from microcosm_fastapi.conventions.schemas import BaseSchema


class NewPizzaSchema(BaseSchema):
    toppings: str


class PizzaSchema(NewPizzaSchema):
    id: UUID
    price: float
