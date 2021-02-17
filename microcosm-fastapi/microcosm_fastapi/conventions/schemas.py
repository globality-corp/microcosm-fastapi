from typing import Any, List

from pydantic import BaseModel as BaseModel
from microcosm_fastapi.naming import to_camel


class BaseSchema(BaseModel):
    class Config:
        # Hydrate SQLAlchemy models
        orm_mode = True

        # Convert to camel case for json payloads
        alias_generator = to_camel
        allow_population_by_field_name = True

        # Allow "Any" to be used
        arbitrary_types_allowed = True


def SearchSchema(item_class):
    class _SearchSchema(BaseModel):
        count: int
        items: List[item_class]

    _SearchSchema.__name__ = "Search" + item_class.__name__

    return _SearchSchema
