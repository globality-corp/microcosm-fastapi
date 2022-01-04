from fastapi import FastAPI
from fastapi.testclient import TestClient
from microcosm.api import defaults, typed

from microcosm_fastapi.errors import ErrorSchema


class FastAPIWrapper(FastAPI):
    """
    Provide basic extensions to FastAPI's syntax.

    - Type-decoration, specify return schema via the return type annotation.
    - Easily create a test client

    """

    def get(self, *args, **kwargs):
        def _get(fn):
            _kwargs = self.inject_return_type(fn, kwargs)
            _kwargs = self.inject_default_response(_kwargs)
            return super(FastAPIWrapper, self).get(*args, **_kwargs)(fn)

        return _get

    def post(self, *args, **kwargs):
        def _post(fn):
            _kwargs = self.inject_return_type(fn, kwargs)
            _kwargs = self.inject_default_response(_kwargs)
            return super(FastAPIWrapper, self).post(*args, **_kwargs)(fn)

        return _post

    def patch(self, *args, **kwargs):
        def _patch(fn):
            _kwargs = self.inject_return_type(fn, kwargs)
            _kwargs = self.inject_default_response(_kwargs)
            return super(FastAPIWrapper, self).patch(*args, **_kwargs)(fn)

        return _patch

    def delete(self, *args, **kwargs):
        def _delete(fn):
            _kwargs = self.inject_return_type(fn, kwargs)
            _kwargs = self.inject_default_response(_kwargs)
            return super(FastAPIWrapper, self).delete(*args, **_kwargs)(fn)

        return _delete

    def options(self, *args, **kwargs):
        def _options(fn):
            _kwargs = self.inject_return_type(fn, kwargs)
            _kwargs = self.inject_default_response(_kwargs)
            return super(FastAPIWrapper, self).options(*args, **_kwargs)(fn)

        return _options

    def head(self, *args, **kwargs):
        def _head(fn):
            _kwargs = self.inject_return_type(fn, kwargs)
            _kwargs = self.inject_default_response(_kwargs)
            return super(FastAPIWrapper, self).head(*args, **_kwargs)(fn)

        return _head

    def trace(self, *args, **kwargs):
        def _trace(fn):
            _kwargs = self.inject_return_type(fn, kwargs)
            _kwargs = self.inject_default_response(_kwargs)
            return super(FastAPIWrapper, self).trace(*args, **_kwargs)(fn)

        return _trace

    def test_client(self):
        return TestClient(self)

    def inject_return_type(self, fn, kwargs):
        # If the user's function signature has provided a return type via a python
        # annotation, they want to serialize their response with this type
        try:
            if "return" in fn.__annotations__:
                kwargs["response_model"] = fn.__annotations__["return"]
        except AttributeError:
            pass
        return kwargs

    def inject_default_response(self, kwargs):
        if kwargs.get("responses", None):
            kwargs["responses"]["default"] = {"model": ErrorSchema}
        else:
            kwargs["responses"] = {"default": {"model": ErrorSchema}}

        return kwargs


@defaults(
    port=typed(int, default_value=5000),
    host="127.0.0.1",
)
def configure_fastapi(graph):
    # Docs use 3rd party dependencies by default - if documentation
    # is desired by client callers, use the `graph.use("docs")` bundled
    # with microcosm-fastapi. This hook provides a mirror to the default
    # docs/redocs but while hosted locally.
    app = FastAPIWrapper(
        port=graph.config.app.port,
        debug=graph.metadata.debug,
        docs_url=None,
        redoc_url=None,
    )

    # Request_context is used for logging purposes
    graph.use("request_context")

    return app
