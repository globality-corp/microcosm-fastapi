from microcosm_fastapi.conventions.config.models import Config


def configure_config(graph):
    """
    Configure the config endpoint.
    """
    config_discovery = Config(graph)

    @graph.app.get("/api/config")
    def configure_config_endpoint():
        return config_discovery.to_dict()

    return config_discovery
