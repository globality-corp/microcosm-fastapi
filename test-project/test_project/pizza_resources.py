from pydantic import BaseModel
from uuid import UUID


class NewPizzaSchema(BaseModel):
    toppings: str


class PizzaSchema(NewPizzaSchema):
    id: UUID
