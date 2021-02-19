from microcosm_fastapi.conventions.schemas import BaseSchema
from typing import Optional, Dict


class HealthResultSchema(BaseSchema):
    name: str
    okay: str


class HealthSchema(BaseSchema):
    name: str
    okay: str
    checks: Optional[Dict[str, HealthResultSchema]]
