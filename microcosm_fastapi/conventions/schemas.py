from typing import Any, List, Optional

from pydantic import BaseModel as BaseModel, AnyHttpUrl, Field

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


class HrefSchema(BaseModel):
    href: AnyHttpUrl


class LinksSchema(BaseModel):
    next: Optional[HrefSchema]
    self: HrefSchema
    prev: Optional[HrefSchema]

    def dict(self, *args, exclude_none=True, **kwargs):
        # Exclude next/prev key if not present
        return BaseModel.dict(self, *args, exclude_none=True, **kwargs)


def SearchSchema(item_class):
    class _SearchSchema(BaseModel):
        links: Optional[LinksSchema] = Field(alias="_links")
        count: int
        items: List[item_class]
        offset: Optional[int]
        limit: Optional[int]

        __config__ = item_class.__config__

    _SearchSchema.__name__ = "Search" + item_class.__name__

    return _SearchSchema
