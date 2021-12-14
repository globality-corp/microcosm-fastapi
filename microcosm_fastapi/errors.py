from typing import (
    Any,
    Dict,
    List,
    Optional,
)

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


class ParsedException:
    def __init__(self, error):
        self.error = error

        self.context: Dict[Any, Any] = self.extract_context()
        self.retryable: bool = self.extract_retryable()
        self.error_message: str = self.extract_error_message()
        self.status_code: int = self.extract_status_code()
        self.include_stack_trace: bool = self.extract_include_stack_trace()

    def extract_context(self) -> Dict[Any, Any]:
        """
        Extract context from an error.

        Errors may (optionally) provide a context attribute which will be encoded
        in the response.

        """
        return getattr(self.error, "context", {"errors": []})

    def extract_retryable(self) -> bool:
        """
        Extract a retryable status from an error.

        It's not usually helpful to retry on an error, but it's useful to do so
        when the application knows it might.

        """
        return getattr(self.error, "retryable", False)

    def extract_error_message(self) -> str:
        """
        Extract a useful message from an error.

        Prefer the description attribute, then the message attribute, then
        the errors string conversion. In each case, fall back to the error class's
        name in the event that the attribute value was set to a uselessly empty string.

        """
        try:
            return self.error.description or self.error.__class__.__name__
        except AttributeError:
            try:
                return str(self.error.message) or self.error.__class__.__name__
            except AttributeError:
                return str(self.error) or self.error.__class__.__name__

    def extract_status_code(self) -> int:
        """
        Extract an error code from a message.

        """
        try:
            return int(self.error.code)
        except (AttributeError, TypeError, ValueError):
            try:
                return int(self.error.status_code)
            except (AttributeError, TypeError, ValueError):
                try:
                    return int(self.error.errno)
                except (AttributeError, TypeError, ValueError):
                    return 500

    def extract_include_stack_trace(self) -> bool:
        """
        Extract whether error should include a stack trace.

        """
        return getattr(self.error, "include_stack_trace", True)

    def to_dict(self):
        return {
            "code": self.status_code,
            "context": self.context,
            "message": self.error_message,
            "retryable": self.retryable,
        }
