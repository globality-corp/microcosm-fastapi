from typing import Any, List, Optional
from enum import Enum

from pydantic import BaseModel as BaseModel, AnyHttpUrl, Field

from microcosm_fastapi.naming import to_camel


class EnhancedBaseModel(BaseModel):

    @classmethod
    def _get_value(
            cls,
            v: Any,
            to_dict: bool,
            by_alias: bool,
            include,
            exclude,
            exclude_unset: bool,
            exclude_defaults: bool,
            exclude_none: bool,
    ) -> Any:
        # The reason that we're overriding the Pydantic's BaseModel is so that
        # we can create our own Config parameters such as 'not_use_enum_names'

        # 'not_use_enum_names' is bespoke pydantic config parameter used to indicate when
        # enum names shouldn't be used. Because it is more common to want to use enum names
        # the default execution flow for Enums will be to use their names.
        if isinstance(v, Enum) and not getattr(cls.Config, 'not_use_enum_names', False):
            return v.name

        return super()._get_value(
            v,
            to_dict,
            by_alias,
            include,
            exclude,
            exclude_unset,
            exclude_defaults,
            exclude_none,
        )

class BaseSchema(EnhancedBaseModel):
    class Config:
        # Hydrate SQLAlchemy models
        orm_mode = True

        # Convert to camel case for json payloads
        alias_generator = to_camel
        allow_population_by_field_name = True

        # Allow "Any" to be used
        arbitrary_types_allowed = True


class HrefSchema(EnhancedBaseModel):
    href: AnyHttpUrl


class LinksSchema(EnhancedBaseModel):
    next: Optional[HrefSchema]
    self: HrefSchema
    prev: Optional[HrefSchema]

    def dict(self, *args, exclude_none=True, **kwargs):
        # Exclude next/prev key if not present
        return BaseModel.dict(self, *args, exclude_none=True, **kwargs)


def SearchSchema(item_class):
    class _SearchSchema(EnhancedBaseModel):
        links: Optional[LinksSchema] = Field(alias="_links")
        count: int
        items: List[item_class]
        offset: Optional[int]
        limit: Optional[int]

        __config__ = item_class.__config__

    _SearchSchema.__name__ = "Search" + item_class.__name__

    return _SearchSchema
