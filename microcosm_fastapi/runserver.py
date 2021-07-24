from click import command, option
from uvicorn import run


def main(entrypoint, graph):
    default_port = graph.config.app.port

    @command()
    @option("--host", default="127.0.0.1")
    @option("--port", default=default_port)
    @option("--access-log", default=True)
    def _runserver(host, port, access_log):
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
            access_log=access_log,
        )

    _runserver()
