from microcosm_fastapi.runserver import main as runserver_main
from microcosm_postgres.createall import main as createall_main

from test_project.app import create_app


def runserver():
    graph = create_app(debug=True)
    runserver_main(graph)

def createall():
    graph = create_app(debug=True, model_only=True)
    createall_main(graph)
