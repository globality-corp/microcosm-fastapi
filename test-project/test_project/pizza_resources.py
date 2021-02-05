from pydantic import BaseModel
from uuid import UUID


class NewPizzaSchema(BaseModel):
    toppings: str
    random_topping: str

    class Config:
        orm_mode = True


class PizzaSchema(NewPizzaSchema):
    id: UUID
