from typing import (
    Any,
    List,
    Optional,
    no_type_check,
)

from pydantic.validators import str_validator


class SeparatedList(str):
    separator = ","

    @classmethod
    def __get_validators__(cls) -> 'CallableGenerator':
        yield cls.validate

    @classmethod
    def validate(cls, value: Any, field: "ModelField", config: "BaseConfig") -> "SeparatedList":
        if value.__class__ == cls:
            return value
        value = str_validator(value)
        value = value.strip()

        return value.split(cls.separator)
