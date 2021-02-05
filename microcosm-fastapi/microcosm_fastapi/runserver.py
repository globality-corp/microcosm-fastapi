from uvicorn import run

def main(graph):
    """
    Launch the local debugging server

    For production deployments - run instead with gunicorn:
    ```gunicorn example:app -w 4 -k uvicorn.workers.UvicornWorker```
    """
    run(
        graph.app,
        host=graph.config.app.host,
        port=graph.config.app.port,
        log_level="info",
    )
