from microcosm.api import defaults

from microcosm_fastapi.conventions.build_info.models import BuildInfo
from microcosm_fastapi.conventions.build_info.resources import BuildInfoSchema


@defaults(
    build_num=None,
    sha1=None,
)
def configure_build_info(graph):
    """
    Configure the build info endpoint.
    """
    build_info = BuildInfo.from_config(graph.config)

    @graph.app.get("/api/build_info")
    def configure_build_info_endpoint() -> BuildInfoSchema:
        return build_info.to_object()

    return build_info
