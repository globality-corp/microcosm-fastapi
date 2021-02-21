from microcosm_fastapi.conventions.schemas import BaseSchema
from typing import Optional, Dict


class HealthResultSchema(BaseSchema):
    name: str
    ok: str


class HealthSchema(BaseSchema):
    name: str
    ok: str
    checks: Optional[Dict[str, HealthResultSchema]]
