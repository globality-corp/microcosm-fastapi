from enum import Enum
from typing import (
    Any,
    Dict,
    List,
    Optional,
    Type,
)

from pydantic import AnyHttpUrl, BaseModel as BaseModel, Field

from microcosm_fastapi.naming import to_camel


class EnhancedBaseModel(BaseModel):
    @classmethod
    def _get_value(
        cls,
        value: Any,
        to_dict: bool,
        by_alias: bool,
        include,
        exclude,
        exclude_unset: bool,
        exclude_defaults: bool,
        exclude_none: bool,
    ) -> Any:
        # The reason that we're overriding the Pydantic's BaseModel is so that
        # we can create our own Config parameters such as 'use_enum_names'

        # 'use_enum_names' is bespoke pydantic config parameter used to indicate when
        # enum names (keys) should/shouldn't be used.
        # Because it is more common to want to use enum names, consumers of the enum
        # base class that don't want to use enum names have to explicitly
        # put `use_enum_names` = False in their cls.Config.
        if isinstance(value, Enum) and getattr(cls.Config, "use_enum_names", True):
            return value.name

        return super()._get_value(
            value,
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

        @staticmethod
        def schema_extra(schema: Dict[str, Any], model: Type["BaseSchema"]) -> None:
            """
            Pydantic hook to post process the json schema output.

            """
            for field_name, model_field in model.__fields__.items():
                if model_field.type_ == float:
                    # We need to add the format `float` value to fit with existing microcosm conventions
                    # The format `float` is used when converting from a V3 openapi spec -> V2
                    schema["properties"][f"{field_name}"]["format"] = "float"


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
        offset: int
        limit: int

        __config__ = item_class.__config__

    _SearchSchema.__name__ = item_class.__name__ + "List"

    return _SearchSchema
