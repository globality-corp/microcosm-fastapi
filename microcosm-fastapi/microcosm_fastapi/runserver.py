from uvicorn import run

def main(graph):
    """
    Launch the local debugging server

    For production deployments - run instead with gunicorn:
    ```gunicorn example:app -w 4 -k uvicorn.workers.UvicornWorker```
    """
    run(
        graph.app, host="127.0.0.1", port=5000, log_level="info"
    )
