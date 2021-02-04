from microcosm.api import defaults
from fastapi import FastAPI


@defaults(
    port=5000,
    debug=True,
)
def configure_fastapi(graph):
    app = FastAPI(port=graph.app.port, debug=graph.app.debug)
    return app