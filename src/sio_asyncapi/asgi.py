"""Asyncio / ASGI Socket.IO server with AsyncAPI documentation."""
from __future__ import annotations

from typing import Any, Callable, Optional

import socketio
from pydantic import BaseModel

from sio_asyncapi.contract import AsyncAPIContract
from sio_asyncapi.http import DocsASGIApp


class AsyncAPIAsyncServer(AsyncAPIContract, socketio.AsyncServer):
    """python-socketio AsyncServer with Pydantic validation and AsyncAPI 3.1 docs.

    Use :meth:`asgi_app` to mount the server (and optional docs routes) in
    FastAPI, Starlette, or any ASGI server::

        sio = AsyncAPIAsyncServer(validate=True, generate_docs=True)
        app = FastAPI()
        asgi_app = sio.asgi_app(app)
    """

    def __init__(
        self,
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
        super().__init__(*args, **kwargs)

    def asgi_app(
        self,
        other_asgi_app: Any = None,
        socketio_path: str = "socket.io",
    ) -> Any:
        """Return an ASGI app that serves Socket.IO plus optional docs routes."""
        inner = socketio.ASGIApp(self, other_asgi_app, socketio_path=socketio_path)
        if not self.serve_docs:
            return inner
        return DocsASGIApp(self, inner)

    async def emit(
        self,
        event: str,
        data: Any = None,
        to: Any = None,
        room: Any = None,
        skip_sid: Any = None,
        namespace: Optional[str] = None,
        callback: Optional[Callable] = None,
        ignore_queue: bool = False,
    ):
        self._validate_emit_payload(event, data, namespace)
        return await super().emit(
            event,
            data,
            to=to,
            room=room,
            skip_sid=skip_sid,
            namespace=namespace,
            callback=callback,
            ignore_queue=ignore_queue,
        )

    def event(self, *args, **kwargs):
        """Register a handler using the function name as the event name."""
        extra = {
            key: kwargs.pop(key)
            for key in ("get_from_typehint", "request_model", "response_model")
            if key in kwargs
        }
        if len(args) == 1 and not kwargs and callable(args[0]) and not extra:
            return self.on(args[0].__name__)(args[0])

        def set_handler(handler):
            return self.on(handler.__name__, *args, **kwargs, **extra)(handler)

        return set_handler

    def on(
        self,
        event: str,
        handler: Optional[Callable] = None,
        namespace: Optional[str] = None,
        *,
        get_from_typehint: bool = False,
        response_model=None,
        request_model=None,
    ):
        if handler is None:
            def decorator(func: Callable):
                return self.on(
                    event,
                    func,
                    namespace,
                    get_from_typehint=get_from_typehint,
                    response_model=response_model,
                    request_model=request_model,
                )
            return decorator

        wrapped = self._register_receiver(
            handler,
            event,
            namespace,
            get_from_typehint=get_from_typehint,
            response_model=response_model,
            request_model=request_model,
        )
        super().on(event, wrapped, namespace=namespace)
        return wrapped
