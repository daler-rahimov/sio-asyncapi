from typing import Optional

from flask import Flask
from flask_socketio import SocketIO
from pydantic import BaseModel

from sio_asyncapi.contract import AsyncAPIContract
from sio_asyncapi.http import register_flask_docs


class AsyncAPISocketIO(AsyncAPIContract, SocketIO):
    """Flask-SocketIO server with Pydantic validation and AsyncAPI 3.1 docs.

    Module-level :func:`flask_socketio.emit` looks up this instance from the
    Flask extension map, so emit validation still applies when handlers use
    those helpers.
    """

    def __init__(
        self,
        app: Optional[Flask] = None,
        *args,
        validate: bool = False,
        generate_docs: bool = True,
        serve_docs: Optional[bool] = None,
        version: str = "1.0.0",
        title: str = "Demo Chat API",
        description: str = "Demo Chat API",
        server_url: str = "http://localhost:5000",
        server_name: str = "BACKEND",
        auth_model: Optional[type[BaseModel]] = None,
        security_scheme: Optional[dict] = None,
        security_scheme_name: str = "socketioAuth",
        **kwargs,
    ):
        self._init_contract(
            validate=validate,
            generate_docs=generate_docs,
            serve_docs=serve_docs,
            version=version,
            title=title,
            description=description,
            server_url=server_url,
            server_name=server_name,
            auth_model=auth_model,
            security_scheme=security_scheme,
            security_scheme_name=security_scheme_name,
        )
        super().__init__(app=app, *args, **kwargs)

    def init_app(self, app, **kwargs):
        super().init_app(app, **kwargs)
        if app is not None:
            self._maybe_register_docs(app)

    def _maybe_register_docs(self, app: Flask) -> None:
        if self.serve_docs and not getattr(app, "_sio_asyncapi_docs_registered", False):
            register_flask_docs(app, self)
            app._sio_asyncapi_docs_registered = True

    def emit(self, event: str, *args, **kwargs):
        namespace = kwargs.get("namespace")
        payload = args[0] if args else None
        self._validate_emit_payload(event, payload, namespace)
        return super().emit(event, *args, **kwargs)

    def event(self, *args, **kwargs):
        """Register a handler using the function name as the event name."""
        if len(args) == 1 and len(kwargs) == 0 and callable(args[0]):
            return self.on(args[0].__name__)(args[0])

        def set_handler(handler):
            return self.on(handler.__name__, *args, **kwargs)(handler)

        return set_handler

    def on(
        self,
        message,
        namespace=None,
        *,
        get_from_typehint: bool = False,
        response_model=None,
        request_model=None,
    ):
        def decorator(handler):
            wrapped = self._register_receiver(
                handler,
                message,
                namespace,
                get_from_typehint=get_from_typehint,
                response_model=response_model,
                request_model=request_model,
            )
            super(AsyncAPISocketIO, self).on(message, namespace)(wrapped)
            return wrapped

        return decorator
