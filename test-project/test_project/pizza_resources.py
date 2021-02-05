from uuid import UUID

from pydantic import BaseModel


class NewPizzaSchema(BaseModel):
    toppings: str

    class Config:
        orm_mode = True


class PizzaSchema(NewPizzaSchema):
    id: UUID
    price: float
