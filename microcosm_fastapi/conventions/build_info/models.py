from microcosm_fastapi.conventions.build_info.resources import BuildInfoSchema


class BuildInfo:
    def __init__(self, build_num, sha1):
        self.build_num = build_num
        self.sha1 = sha1

    def to_object(self) -> BuildInfoSchema:
        return BuildInfoSchema(
            build_num=self.build_num,
            sha1=self.sha1,
        )

    @classmethod
    def from_config(cls, config):
        return cls(
            build_num=config.build_info_convention.build_num,
            sha1=config.build_info_convention.sha1,
        )

    @staticmethod
    def check_build_num(graph):
        build_info = BuildInfo.from_config(graph.config)
        return build_info.build_num or "undefined"

    @staticmethod
    def check_sha1(graph):
        build_info = BuildInfo.from_config(graph.config)
        return build_info.sha1 or "undefined"
