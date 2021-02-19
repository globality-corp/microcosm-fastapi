from fastapi import FastAPI
from microcosm.api import defaults, typed


class FastAPIWrapper(FastAPI):
    """
    Provide basic extensions to FastAPI's syntax.

    - Type-decoration, specify return schema via the return type annotation.

    """
    def get(self, fn, *args, **kwargs):
        kwargs = self.inject_return_type(kwargs)
        return super.get(fn, *args, **kwargs)

    def post(self, fn, *args, **kwargs):
        kwargs = self.inject_return_type(kwargs)
        return super.post(fn, *args, **kwargs)

    def patch(self, fn, *args, **kwargs):
        kwargs = self.inject_return_type(kwargs)
        return super.patch(fn, *args, **kwargs)

    def delete(self, fn, *args, **kwargs):
        kwargs = self.inject_return_type(kwargs)
        return super.delete(fn, *args, **kwargs)

    def options(self, fn, *args, **kwargs):
        kwargs = self.inject_return_type(kwargs)
        return super.options(fn, *args, **kwargs)

    def head(self, fn, *args, **kwargs):
        kwargs = self.inject_return_type(kwargs)
        return super.head(fn, *args, **kwargs)

    def trace(self, fn, *args, **kwargs):
        kwargs = self.inject_return_type(kwargs)
        return super.trace(fn, *args, **kwargs)
    
    def inject_return_type(self, fn, kwargs):
        # If the user's function signature has provided a return type via a python
        # annotation, they want to serialize their response with this type
        if "return" in fn.__annotations__:
            kwargs["response_model"] = fn.__annotations__["return"]

        return kwargs


@defaults(
    port=typed(int, default_value=5000),
    host="127.0.0.1",
    debug=True,
)
def configure_fastapi(graph):
    # Docs use 3rd party dependencies by default - if documentation
    # is desired by client callers, use the `graph.use("docs")` bundled
    # with microcosm-fastapi. This hook provides a mirror to the default
    # docs/redocs but while hosted locally.
    app = FastAPIWrapper(
        debug=graph.config.app.debug,
        docs_url=None,
        redoc_url=None,
    )

    return app
