"""
Create the application.
"""
from microcosm.api import create_object_graph
from microcosm.loaders import load_each, load_from_environ
from microcosm.loaders.compose import load_config_and_secrets

import test_project.pizza_route  # noqa: 401
import test_project.pizza_store  # noqa: 401


def create_app(debug=False, testing=False, model_only=False):
    config_loader = load_each(
        load_from_environ,
    )

    graph = create_object_graph(
        name=__name__.split(".")[0],
        debug=debug,
        testing=testing,
        loader=config_loader,
    )

    graph.use(
        "docs",
        "sessionmaker",
        "postgres",
        "pizza_store",
        "postgres_async",
        "session_manager",
        # Conventions
        "build_info_convention",
        "health_convention",
        "config_convention",
        "landing_convention",
    )

    if not model_only:
        graph.use(
            "pizza_route"
        )

    return graph.lock()
