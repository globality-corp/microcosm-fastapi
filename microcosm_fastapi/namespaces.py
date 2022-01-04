from dataclasses import dataclass
from typing import Any, Optional

from fastapi import Request
from microcosm_logging.decorators import logger

from microcosm_fastapi.naming import name_for
from microcosm_fastapi.operations import OperationInfo, OperationType


@logger
@dataclass
class Namespace:
    subject: Any
    version: Optional[str] = None
    prefix: str = "api"
    object_: Optional[Any] = None

    @property
    def path(self) -> str:
        """
        Build the path (prefix) leading up to this namespace.

        i.e for prefix `api` and version `v1`, this function will return `api/v1`

        """
        return "/".join(
            [
                part
                for part in [
                    self.prefix,
                    self.version,
                ]
                if part
            ]
        )

    def path_for_operation(self, operation: OperationInfo) -> str:
        """
        Converts a defined operation (either a `NODE_PATTERN` or `EDGE_PATTERN`)
        into a convention-based URL that can be called on the server.

        (GET, NODE_PATTERN) -> /api/v1/pizza
        (GET, EDGE_PATTERN) -> /api/v1/pizza/pizza_id/order

        """
        if operation.pattern == OperationType.NODE_PATTERN:
            return "/" + self.path + operation.naming_convention(self.subject)

        elif operation.pattern == OperationType.EDGE_PATTERN:
            return "/" + self.path + operation.naming_convention(self.subject, self.object_)
        else:
            raise ValueError()

    @property
    def subject_name(self):
        return name_for(self.subject)

    @property
    def object_name(self):
        if self.object_ is None:
            return None
        else:
            return name_for(self.object_)

    def extract_hostname_from_request(self, request: Request) -> str:
        url = str(request.url)
        host_name = url.split("/api/")[0]

        return host_name

    def url_for(self, request: Request, operation: OperationInfo, **kwargs) -> str:
        """
        Construct a URL for an operation against a resource.

        :param kwargs: additional arguments for URL path expansion

        """
        host_name = self.extract_hostname_from_request(request)
        return f"{host_name}{self.path_for_operation(operation).format(**kwargs)}"

    def generate_operation_name_for_logging(self, operation: OperationInfo) -> str:
        """
        Generate a logging name (useful for logging)

        """
        return operation.pattern.value.format(
            subject=self.subject_name,
            operation=operation.name,
            object_=self.object_name if self.object_ else None,
            version=self.version or "v1",
        )
