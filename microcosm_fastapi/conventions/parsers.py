from typing import Any

from fastapi import Request
from pydantic import BaseConfig
from pydantic.fields import ModelField
from pydantic.typing import CallableGenerator
from pydantic.validators import str_validator

from microcosm_fastapi.naming import join_url_with_parameters


class SeparatedList(str):
    separator = ","

    @classmethod
    def __get_validators__(cls) -> "CallableGenerator":
        yield cls.validate

    @classmethod
    def validate(cls, value: Any, field: "ModelField", config: "BaseConfig") -> "SeparatedList":
        if value.__class__ == cls:
            return value
        value = str_validator(value)
        value = value.strip()

        return value.split(cls.separator)


def LinkProvider(request: Request, offset: int = 0, limit: int = 20):
    """
    Parse the URL so we are able to create a paginated links record that's relative
    to the current location.

    """

    def CreateLinks(total_count):
        links_payload = dict(
            self=dict(
                href=join_url_with_parameters(str(request.url), dict(offset=offset, limit=limit))
            )
        )

        if offset - limit >= 0:
            links_payload["prev"] = dict(
                href=join_url_with_parameters(
                    str(request.url), dict(offset=offset - limit, limit=limit)
                )
            )

        if offset + limit <= total_count:
            links_payload["next"] = dict(
                href=join_url_with_parameters(
                    str(request.url), dict(offset=offset + limit, limit=limit)
                )
            )

        return links_payload

    return CreateLinks
