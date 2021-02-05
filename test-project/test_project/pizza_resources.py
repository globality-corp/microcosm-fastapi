from pydantic import BaseModel
from uuid import UUID


class NewPizzaSchema(BaseModel):
    toppings: str

    class Config:
        orm_mode = True


class PizzaSchema(NewPizzaSchema):
    id: UUID
    random_topping: str
