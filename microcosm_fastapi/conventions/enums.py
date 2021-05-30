"""
Enum conventions

"""
from enum import Enum


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