from distutils import dist
from io import StringIO
from json import dumps
from pkg_resources import DistributionNotFound, get_distribution

from fastapi.responses import HTMLResponse
from jinja2 import Template

from microcosm_fastapi.templates.landing import template


def configure_landing(graph):  # noqa: C901
    def get_properties_and_version():
        """
        Parse the properties from the package information
        """
        try:
            distribution = get_distribution(graph.metadata.name)
            metadata_str = distribution.get_metadata(distribution.PKG_INFO)
            package_info = dist.DistributionMetadata()
            package_info.read_pkg_file(StringIO(metadata_str))
            return package_info
        except DistributionNotFound:
            return None

    def iter_endpoints(graph, match_func):
        for route in graph.app.routes:
            if match_func(route.path):
                yield route

    def get_swagger_versions():
        """
        Finds all swagger conventions that are bound to the graph

        """
        versions = []

        def is_swagger_endpoint(path):
            """
            Defines a condition to determine which endpoints are swagger type

            """
            return graph.config.swagger_convention.name in path

        for route in iter_endpoints(graph, is_swagger_endpoint):
            # route comes in as /api/v2/swagger
            # so we split to get this -> ['', 'api', 'v2', 'swagger']
            # and then get the version value from the array
            versions.append(route.path.split("/")[2])

        return versions

    def pretty_dict(dict_):
        return dumps(dict_, sort_keys=True, indent=2, separators=(",", ": "))

    def get_env_file_commands(config, conf_key, conf_string=None):
        if conf_string is None:
            conf_string = []
        for key, value in config.items():
            if isinstance(value, dict):
                get_env_file_commands(value, "{}__{}".format(conf_key, key), conf_string)
            else:
                conf_string.append(
                    "export {}__{}='{}'".format(conf_key.upper(), key.upper(), value)
                )
        return conf_string

    def get_links(swagger_versions, properties):
        # add links set in config
        links = {
            key: value
            for (key, value) in graph.config.landing_convention.get("links", {}).items()
        }

        # add links for each swagger version
        for swagger_version in swagger_versions:
            links["swagger {}".format(swagger_version)] = "api/{}/swagger".format(swagger_version)

        # add link to home page
        if hasattr(properties, "url"):
            links["home page"] = properties.url

        return links

    @graph.app.get("/")
    async def render_landing_page():
        """
        Render landing page

        """
        config = graph.config_convention.to_dict()
        env = get_env_file_commands(config, graph.metadata.name)

        health = await graph.health_convention.to_object()
        health = health.dict()

        properties = get_properties_and_version()
        swagger_versions = get_swagger_versions()

        html = Template(template).render(
            config=pretty_dict(config),
            description=properties.description if properties else None,
            env=env,
            health=pretty_dict(health),
            links=get_links(swagger_versions, properties),
            service_name=graph.metadata.name,
            version=getattr(properties, "version", None),
        )

        return HTMLResponse(html)
