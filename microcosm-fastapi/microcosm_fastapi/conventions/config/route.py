from microcosm.api import defaults
from microcosm_fastapi.conventions.config.models import Config


def configure_config(graph):
    """
    Configure the config endpoint.
    """
    @graph.app.get("/config")
    def configure_config_endpoint() -> Dict[str, Any]::
        config_discovery = Config(graph)
        return config_discovery.to_dict()
