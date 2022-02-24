from microcosm_postgres.createall import main as createall_main
from test_project.app import create_app

from microcosm_fastapi.runserver import main as runserver_main


graph = create_app(debug=True)
app = graph.app

def runserver():
    runserver_main("test_project.main:app", graph)

def createall():
    createall_main(graph)
