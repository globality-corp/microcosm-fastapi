from microcosm_fastapi.runserver import main as runserver_main
from test_project.app import create_app

def runserver():
    graph = create_app(debug=True)
    runserver_main(graph)