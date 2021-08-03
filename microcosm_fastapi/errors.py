from typing import Optional, List

from microcosm_fastapi.conventions.schemas import BaseSchema


class SubErrorSchema(BaseSchema):
    message: str


class ErrorContextSchema(BaseSchema):
    errors: List[SubErrorSchema]


class ErrorSchema(BaseSchema):
    message: str
    code: int
    retryable: bool
    context: Optional[ErrorContextSchema]