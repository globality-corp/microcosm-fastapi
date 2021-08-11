"""
Audit log support for FastAPI routes.

"""
from typing import Dict, Any, Optional
from collections import namedtuple
from distutils.util import strtobool
from json import loads
from json.decoder import JSONDecodeError
from logging import getLogger
import json
from uuid import UUID
from functools import partial
from inflection import underscore

from fastapi import Request

from microcosm.api import defaults, typed
from microcosm.metadata import Metadata
from microcosm.config.types import boolean
from microcosm_logging.timing import elapsed_time
from microcosm_fastapi.errors import (
    extract_context,
    extract_error_message,
    extract_include_stack_trace,
    extract_status_code,
)
from microcosm_fastapi.utils import AsyncIteratorWrapper
from microcosm_fastapi.logging_data_map import LoggingInfo


DEFAULT_INCLUDE_REQUEST_BODY = 400
DEFAULT_INCLUDE_RESPONSE_BODY = 400
ERROR_MESSAGE_LIMIT = 2048

AUDIT_LOGGER_NAME = "audit"


AuditOptions = namedtuple("AuditOptions", [
    "include_request_body",
    "include_response_body",
    "include_path",
    "include_query_string",
    "log_as_debug",
])


SKIP_LOGGING = "_microcosm_flask_skip_audit_logging"


def is_uuid(value):
    try:
        UUID(value)
        return True
    except Exception:
        return False


def should_skip_logging(request: Request):
    """
    Should we skip logging for this handler?

    """
    return strtobool(request.headers.get("x-request-nolog", "false"))


class RequestInfo:
    """
    Capture of key information for requests.

    """
    def __init__(self, options: AuditOptions, request: Request, request_context: Dict[str, Any], app_metadata: Metadata):
        self.options = options
        self.app_metadata = app_metadata
        self.operation = None
        self.func = None
        self.method = request.method
        self.args = request.query_params

        self.request = request
        self.path = request.url.path
        self.query = request.url.query
        self.request_state = request.state

        self.request_context = request_context
        self.timing = dict()

        self.error = None
        self.stack_trace = None
        self.request_body = None
        self.response_body = None
        self.response_headers = None
        self.status_code = None
        self.success = None

    def to_dict(self):
        dct = dict(
            operation=self.operation,
            func=self.func,
            method=self.method,
            **self.timing
        )

        if self.options.include_query_string and self.args:
            dct.update({
                key: values
                for key, values in self.args.items()
            })

        if self.request_context is not None:
            dct.update(self.request_context)

        if self.success is True:
            dct.update(
                success=self.success,
                status_code=self.status_code,
            )
        if self.success is False:
            dct.update(
                success=self.success,
                message=extract_error_message(self.error)[:ERROR_MESSAGE_LIMIT],
                context=extract_context(self.error),
                stack_trace=self.stack_trace,
                status_code=self.status_code,
            )

        self.post_process_request_body(dct)
        self.post_process_response_body(dct)
        self.post_process_response_headers(dct)

        return dct

    def log(self, logger):
        if self.status_code == 500:
            # something actually went wrong; investigate
            logger.warning(self.to_dict())

        else:
            # usually log at INFO; a raised exception can be an error or
            # expected behavior (e.g. 404)
            if not self.options.log_as_debug:
                logger.info(self.to_dict())
            else:
                logger.debug(self.to_dict())

    async def capture_request(self):
        # TODO - still need to work out how to capture a request
        # https://github.com/tiangolo/fastapi/issues/394#issuecomment-513051977
        if not self.app_metadata.debug:
            # only capture request body on debug
            return

        if not self.options.include_request_body:
            # only capture request body if requested
            return

        if (
                self.content_length and
                self.options.include_request_body is not True and
                self.content_length >= self.options.include_request_body
        ):
            # don't capture request body if it's too large
            return

        self.request_body = await self.get_json()

    async def capture_response(self, response):
        self.success = True

        body, self.status_code, self.response_headers = await parse_response(response)

        if not self.app_metadata.debug:
            # only capture responsebody on debug
            return

        if not self.options.include_response_body:
            # only capture response body if requested
            return

        if not body:
            # only capture request body if there is one
            return

        if (
                self.options.include_response_body is not True and
                len(body) >= self.options.include_response_body
        ):
            # don't capture response body if it's too large
            return

        try:
            self.response_body = loads(body)
        except (TypeError, ValueError):
            # not json
            pass

    def capture_error(self, error):
        self.error = error
        self.status_code = extract_status_code(error)
        self.success = 0 < self.status_code < 400
        include_stack_trace = extract_include_stack_trace(error)
        self.stack_trace = getattr(self.request_state, 'traceback', None) \
            if (not self.success and include_stack_trace) else None

    def post_process_request_body(self, dct):
        if not self.request_body:
            return

        dct.update(
            request_body=self.request_body,
        )

    def post_process_response_body(self, dct):
        if not self.response_body:
            return

        dct.update(
            response_body=self.response_body,
        )

    def post_process_response_headers(self, dct):
        """
        Rewrite X-<>-Id header into audit logs.
        """
        if not self.response_headers:
            return

        for key, value in self.response_headers.items():
            parts = key.split("-")
            if len(parts) != 3:
                continue
            if parts[0] != "X":
                continue
            if parts[-1] != "Id":
                continue

            dct["{}_id".format(underscore(parts[1]))] = value

    def set_operation_and_func_name(self, logging_info):
        """
        Setting operation and function name from logging_info

        """
        self.func = logging_info.function_name
        self.operation = logging_info.operation_name

    @property
    def content_length(self):
        content_length = self.request.headers.get("Content-Length")
        if content_length is not None:
            try:
                return max(0, int(content_length))
            except (ValueError, TypeError):
                pass

        return None

    async def get_json(
            self,
    ) -> Optional[Any]:

        data = None
        try:
            data = await self.request.json()
        except JSONDecodeError:
            pass
        return data


async def parse_response(response):
    """
    Parse a FastAPI response into a body, a status code, and headers

    """
    # Taken from SO: https://stackoverflow.com/questions/60778279/fastapi-middleware-peeking-into-responses
    # Consuming FastAPI response and grabbing body here
    resp_body = [section async for section in response.__dict__['body_iterator']]

    # Repairing FastAPI response
    response.__setattr__('body_iterator', AsyncIteratorWrapper(resp_body))

    # Formatting response body for logging
    try:
        body = json.loads(resp_body[0].decode())
    except:
        body = str(resp_body)

    return body, response.status_code, response.headers


def create_audit_request(graph, options):
    async def audit_request(graph, options: AuditOptions, request: Request, call_next):
        """
        Audit request

        """
        logger = getLogger(AUDIT_LOGGER_NAME)

        request_context = graph.request_context(request)
        request_info = RequestInfo(options, request, request_context, graph.metadata)

        logging_info: LoggingInfo = graph.logging_data_map.get_entry(request.url.path, request.method)
        request_info.set_operation_and_func_name(logging_info)

        with elapsed_time(request_info.timing):
            response = await call_next(request)

        # Look at reworking this bit
        request_error = getattr(request.state, 'error', None)
        if request_error is not None:
            request_info.capture_error(request_error)
        else:
            await request_info.capture_response(response)

        if not should_skip_logging(request):
            request_info.log(logger)

        return response

    return partial(audit_request, graph, options)


@defaults(
    include_request_body=typed(type=int, default_value=DEFAULT_INCLUDE_REQUEST_BODY),
    include_response_body=typed(type=int, default_value=DEFAULT_INCLUDE_RESPONSE_BODY),
    include_path=typed(type=boolean, default_value=False),
    include_query_string=typed(type=boolean, default_value=False),
    log_as_debug=typed(type=boolean, default_value=False),
)
def configure_audit_middleware(graph):
    """
    Configure audit middleware

    """
    options = AuditOptions(
        include_request_body=graph.config.audit_middleware.include_request_body,
        include_response_body=graph.config.audit_middleware.include_response_body,
        include_path=graph.config.audit_middleware.include_path,
        include_query_string=graph.config.audit_middleware.include_query_string,
        log_as_debug=graph.config.audit_middleware.log_as_debug,
    )

    graph.app.middleware("http")(create_audit_request(graph, options))
