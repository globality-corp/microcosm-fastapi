from typing import Dict, Optional

from microcosm_fastapi.conventions.schemas import BaseSchema


class HealthResultSchema(BaseSchema):
    message: str
    ok: str


class HealthSchema(BaseSchema):
    name: str
    ok: str
    checks: Optional[Dict[str, HealthResultSchema]]
