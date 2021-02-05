from pydantic import BaseModel
from typing import List, Any
from functools import wraps

def SearchSchema(item_class):
    class _SearchSchema(BaseModel):
        count: int
        items: List[item_class]

    _SearchSchema.__name__ = "Search" + item_class.__name__

    return _SearchSchema
