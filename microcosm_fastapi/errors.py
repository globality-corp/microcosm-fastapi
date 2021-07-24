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


def extract_context(error):
    """
    Extract extract context from an error.

    Errors may (optionally) provide a context attribute which will be encoded
    in the response.

    """
    return getattr(error, "context", {"errors": []})


def extract_retryable(error):
    """
    Extract a retryable status from an error.

    It's not usually helpful to retry on an error, but it's useful to do so
    when the application knows it might.

    """
    return getattr(error, "retryable", False)


def extract_error_message(error):
    """
    Extract a useful message from an error.

    Prefer the description attribute, then the message attribute, then
    the errors string conversion. In each case, fall back to the error class's
    name in the event that the attribute value was set to a uselessly empty string.

    """
    try:
        return error.description or error.__class__.__name__
    except AttributeError:
        try:
            return str(error.message) or error.__class__.__name__
        except AttributeError:
            return str(error) or error.__class__.__name__


def extract_status_code(error):
    """
    Extract an error code from a message.

    """
    try:
        return int(error.code)
    except (AttributeError, TypeError, ValueError):
        try:
            return int(error.status_code)
        except (AttributeError, TypeError, ValueError):
            try:
                return int(error.errno)
            except (AttributeError, TypeError, ValueError):
                return 500


def extract_include_stack_trace(error):
    """
    Extract whether error should include a stack trace.

    """
    return getattr(error, "include_stack_trace", True)
