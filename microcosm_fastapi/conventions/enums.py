"""
Enum conventions

"""
from enum import Enum
from typing import Any, Dict


class BaseEnum(Enum):
    # Base Enum class that contains a pydantic validator to deserialise Enum
    # keys into their corresponding Enum value
    @classmethod
    def __get_validators__(cls):
        cls.lookup = {key: value for key, value in cls.__members__.items()}
        yield cls.validate

    @classmethod
    def validate(cls, value):
        if isinstance(value, Enum):
            return value

        try:
            return cls.lookup[value]
        except KeyError:
            raise ValueError('invalid value')

    # This is used to modify the enum schema so we can use enum names
    # instead of enum values which isn't desirable in all cases
    # i.e where you have nested non-string values (python objects)
    @classmethod
    def __modify_schema__(cls, field_schema: Dict[str, Any]) -> None:
        field_schema.update(enum=[value.name for value in cls])