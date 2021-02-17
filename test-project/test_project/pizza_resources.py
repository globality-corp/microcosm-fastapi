from uuid import UUID

from microcosm_fastapi.conventions.schemas import BaseModel


class NewPizzaSchema(BaseModel):
    toppings: str


class PizzaSchema(NewPizzaSchema):
    id: UUID
    price: float
