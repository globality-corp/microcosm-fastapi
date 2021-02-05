from fastapi import FastAPI
from microcosm.api import defaults, typed


@defaults(
    port=typed(int, default_value=5000),
    host="127.0.0.1",
    debug=True,
)
def configure_fastapi(graph):
    app = FastAPI(debug=graph.config.app.debug)

    return app
