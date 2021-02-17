from uvicorn import run
from click import command, option

def main(entrypoint, graph):
    default_port = graph.config.app.port

    @command()
    @option("--host", default="127.0.0.1")
    @option("--port", default=default_port)
    def _runserver(host, port):
        """
        Launch the local debugging server

        For production deployments - run instead with gunicorn:
        ```gunicorn example:app -w 4 -k uvicorn.workers.UvicornWorker```
        """
        run(
            entrypoint,
            host=host,
            port=port,
            log_level="info",
            reload=True,
        )

    _runserver()