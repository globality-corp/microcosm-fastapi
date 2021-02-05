from microcosm_fastapi.context import SessionContext

def configure_session_manager(graph):
    """
    Provide a default session manager if explicitly imported into the 
    graph. This is useful to configure the current instance of the fastapi application
    to have the necessary database context during launch.

    """
    return SessionContext(graph).open()
