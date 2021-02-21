from microcosm_fastapi.conventions.schemas import BaseSchema


class BuildInfoSchema(BaseSchema):
    build_num: str
    sha1: str
