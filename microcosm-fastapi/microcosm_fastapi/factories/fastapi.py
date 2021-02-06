from fastapi import FastAPI
from microcosm.api import defaults, typed


@defaults(
    port=typed(int, default_value=5000),
    host="127.0.0.1",
    debug=True,
)
def configure_fastapi(graph):
    # Docs use 3rd party dependencies by default - if documentation
    # is desired by client callers, use the `graph.use("docs")` bundled
    # with microcosm-fastapi. This hook provides a mirror to the default
    # docs/redocs but while hosted locally.
    app = FastAPI(
        debug=graph.config.app.debug,
        docs_url=None,
        redoc_url=None,
    )

    return app
