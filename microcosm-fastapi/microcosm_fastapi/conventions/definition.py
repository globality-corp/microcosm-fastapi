from dataclasses import dataclass
from pydantic import BaseModel, 

@dataclass
class EndpointDefinition:
    """
    Define an operation that can be conducted on a model node or edge.

    :param func: The function to parse the incoming request
    :param request_schema: Optional request schema
    :param response_schema: Optional response schema

    """
    func: Callable
    request_schema: Optional[BaseModel] = None
    response_schema: Optional[BaseModel] = None
