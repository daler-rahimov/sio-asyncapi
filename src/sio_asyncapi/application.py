import functools
import inspect
import logging
from typing import Any, Callable, Optional, Type, Union

from flask import Flask
from flask_socketio import SocketIO
from sio_asyncapi._pydantic import BaseModel

from sio_asyncapi._compat import (
    BaseValidationError,
    PYDANTIC_VALIDATION_ERRORS,
    is_pydantic_model_instance,
    is_pydantic_model_type,
    model_dump_jsonable,
    model_validate,
)
from sio_asyncapi.asyncapi.docs import AsyncAPIDoc, LIFECYCLE_EVENTS, NotProvidedType

logger = logging.getLogger(__name__)

DEFAULT_NAMESPACE = "/"
SKIP_PAYLOAD_ARG_NAMES = frozenset({"self", "cls", "sid"})


def normalize_namespace(namespace: Optional[str]) -> str:
    """Normalize Socket.IO namespace values."""
    return namespace or DEFAULT_NAMESPACE


def _payload_annotation(handler: Callable, event_name: str) -> Any:
    """Return the typehint for the Socket.IO payload argument."""
    try:
        arg_names = list(inspect.getfullargspec(handler).args)
    except (TypeError, IndexError):
        return None

    while arg_names and arg_names[0] in SKIP_PAYLOAD_ARG_NAMES:
        arg_names.pop(0)

    if event_name == "disconnect":
        return None
    if not arg_names:
        return None
    return handler.__annotations__.get(arg_names[0], "NotProvided")


class RequestValidationError(BaseValidationError):
    pass


class ResponseValidationError(BaseValidationError):
    pass


class EmitValidationError(BaseValidationError):
    pass


class AsyncAPISocketIO(SocketIO):
    """Inherits the :class:`flask_socketio.SocketIO` class.

    Adds Pydantic validation and AsyncAPI 3.1 documentation generation.

    Module-level :func:`flask_socketio.emit` and :func:`flask_socketio.send`
    look up this instance from the Flask extension map, so emit validation
    still applies when handlers use those helpers.

    Example::
        socket = AsyncAPISocketIO(app, async_mode='threading', logger=True)
        class TokenModel(BaseModel):
            token: int

        class UserModel(BaseModel):
            name: str
            id: int

        @socket.on('get_user', response_model=UserModel)
        def get_user():
            return {"name": "Bob", "id": 123}
    """

    def __init__(
        self,
        app: Optional[Flask] = None,
        *args,
        validate: bool = False,
        generate_docs: bool = True,
        version: str = "1.0.0",
        title: str = "Demo Chat API",
        description: str = "Demo Chat API",
        server_url: str = "http://localhost:5000",
        server_name: str = "BACKEND",
        auth_model: Optional[Type[BaseModel]] = None,
        security_scheme: Optional[dict] = None,
        security_scheme_name: str = "socketioAuth",
        **kwargs,
    ):
        """Create AsyncAPISocketIO.

        Args:
            app: Flask application.
            validate: If True, request, response, and emit payloads are
                validated. Defaults to False.
            generate_docs: If True, AsyncAPI specs are generated. Defaults to True.
            version: AsyncAPI info.version. Defaults to "1.0.0".
            title: AsyncAPI info.title. Defaults to "Demo Chat API".
            description: AsyncAPI info.description. Defaults to "Demo Chat API".
            server_url: AsyncAPI server URL. Defaults to "http://localhost:5000".
            server_name: AsyncAPI server name. Defaults to "BACKEND".
            auth_model: Optional Pydantic model documenting Socket.IO handshake
                auth (the connect event payload). When set, a default security
                scheme is also added unless ``security_scheme`` is provided.
            security_scheme: Optional AsyncAPI Security Scheme object. When
                set (or inferred from ``auth_model``), it is attached to the
                documented server.
            security_scheme_name: Component name for ``security_scheme``.
        """
        self.validate = validate
        self.generate_docs = generate_docs
        self.auth_model = auth_model
        self.asyncapi_doc: AsyncAPIDoc = AsyncAPIDoc.default_init(
            version=version,
            title=title,
            description=description,
            server_url=server_url,
            server_name=server_name,
            security_scheme=security_scheme,
            security_scheme_name=security_scheme_name,
            auth_model=auth_model if generate_docs else None,
        )
        super().__init__(app=app, *args, **kwargs)
        self.emit_models: dict[tuple[str, str], Type[BaseModel]] = {}

    def emit(self, event: str, *args, **kwargs):
        """
        Overrides emit in order to validate data with pydantic models.

        ``flask_socketio.emit`` delegates to this method through the Flask
        extension registry, so documented emit events are validated either way.

        for more info refer to :meth:`flask_socketio.SocketIO.emit`
        """
        if self.validate:
            namespace = normalize_namespace(kwargs.get("namespace"))
            model = self.emit_models.get((event, namespace))
            if model is not None:
                payload = args[0] if args else None
                try:
                    model_validate(model, payload)
                except PYDANTIC_VALIDATION_ERRORS as e:
                    logger.error("Error validating emit '%s': %s", event, e)
                    raise EmitValidationError.init_from_super(e) from e
        return super().emit(event, *args, **kwargs)

    def doc_emit(
        self,
        event: str,
        model: Type[BaseModel],
        description: str = "",
        namespace: Optional[str] = None,
        *,
        discription: Optional[str] = None,
    ):
        """
        Decorator to register a Socket.IO emit event for validation and docs.

        Always registers ``model`` for emit validation. AsyncAPI send
        operations are added only when ``generate_docs`` is True.

        Args:
            event: Event name.
            model: Pydantic model for the emit payload.
            description: Human-readable description for AsyncAPI.
            namespace: Socket.IO namespace. Defaults to "/".
            discription: Deprecated alias for ``description``.
        """
        if discription is not None and not description:
            description = discription

        def decorator(func):
            normalized_namespace = normalize_namespace(namespace)
            event_key = (event, normalized_namespace)
            if self.emit_models.get(event_key):
                raise ValueError(
                    f"Event {event} already registered for namespace {normalized_namespace}"
                )
            self.emit_models[event_key] = model
            if self.generate_docs:
                self.asyncapi_doc.add_new_sender(
                    event,
                    model,
                    description,
                    namespace=normalized_namespace,
                )
            return func

        return decorator

    def event(self, *args, **kwargs):
        """Register a handler using the function name as the event name.

        Accepts the same extra keyword arguments as :meth:`on`:
        ``get_from_typehint``, ``request_model``, and ``response_model``.
        """
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
        response_model: Optional[Union[Type[BaseModel], NotProvidedType]] = None,
        request_model: Optional[Union[Type[BaseModel], NotProvidedType]] = None,
    ):
        """Decorator to register a SocketIO event handler with additional functionalities

        Args:
            message (str): refer to SocketIO.on(message)
            namespace (str, optional): refer to SocketIO.on(namespace). Defaults to None.
            get_from_typehint (bool, optional): Get request and response models from typehint.
                request_model and response_model take precedence over typehints if not None.
                Defaults to False.
            response_model (Optional[Type[BaseModel]], optional): Acknowledge model used
                for validation and documentation. Defaults to None.
            request_model (Optional[Type[BaseModel]], optional): Request payload model used
                for validation and documentation. Defaults to None.
        """

        def decorator(handler: Callable):
            nonlocal request_model
            nonlocal response_model
            if get_from_typehint:
                possible_request_model = _payload_annotation(handler, message)
                possible_response_model = handler.__annotations__.get(
                    "return", "NotProvided"
                )
                if request_model is None:
                    request_model = possible_request_model
                if response_model is None:
                    response_model = possible_response_model

            if (
                message == "connect"
                and request_model is None
                and self.auth_model is not None
            ):
                request_model = self.auth_model

            if message in LIFECYCLE_EVENTS:
                response_model = None

            if self.generate_docs:
                self.asyncapi_doc.add_new_receiver(
                    handler,
                    message,
                    ack_data_model=response_model,
                    payload_model=request_model,
                    namespace=normalize_namespace(namespace),
                )

            wrapped_handler = self._handle_all(
                request_model=request_model,
                response_model=response_model,
                event_name=message,
            )(handler)
            super(AsyncAPISocketIO, self).on(message, namespace)(wrapped_handler)
            return wrapped_handler

        return decorator

    def get_agent_schema(self):
        """Return the compact agent-friendly event catalog."""
        return self.asyncapi_doc.get_agent_schema()

    def get_agent_schema_json(self) -> str:
        """Return the compact agent-friendly event catalog as JSON."""
        return self.asyncapi_doc.get_agent_schema_json()

    def _handle_all(
        self,
        response_model: Optional[Union[Type[BaseModel], NotProvidedType]] = None,
        request_model: Optional[Union[Type[BaseModel], NotProvidedType]] = None,
        event_name: Optional[str] = None,
    ):
        """Decorator to validate request and response with pydantic models
        Args:
            handler (Callable, optional): handler function. Defaults to None.
            response_model (Optional[Type[BaseModel]], optional): Acknowledge model used
                for validation and documentation. Defaults to None.
            request_model (Optional[Type[BaseModel]], optional): Request payload model used
                for validation and documentation. Defaults to None.

        Raises: RequestValidationError, ResponseValidationError
        """

        def decorator(handler: Callable):
            @functools.wraps(handler)
            def wrapper(*args, **kwargs):
                did_request_came_as_arg = False
                request_provided = False
                request = None
                if len(args) > 0:
                    did_request_came_as_arg = True
                    request_provided = True
                    request = args[0]
                elif "request" in kwargs:
                    request_provided = True
                    request = kwargs.get("request")

                if request_provided and is_pydantic_model_type(request_model):
                    try:
                        request = model_validate(request_model, request)
                    except PYDANTIC_VALIDATION_ERRORS as e:
                        if self.validate:
                            logger.error("ValidationError for incoming request: %s", e)
                            raise RequestValidationError.init_from_super(e) from e
                        raise
                    if did_request_came_as_arg:
                        args = (request, *args[1:])
                    else:
                        kwargs["request"] = request

                response = handler(*args, **kwargs)
                if (
                    event_name not in LIFECYCLE_EVENTS
                    and response is not None
                    and is_pydantic_model_type(response_model)
                    and self.validate
                ):
                    try:
                        model_validate(response_model, response)
                    except PYDANTIC_VALIDATION_ERRORS as e:
                        logger.error("ValidationError for outgoing response: %s", e)
                        raise ResponseValidationError.init_from_super(e) from e

                if event_name not in LIFECYCLE_EVENTS and is_pydantic_model_instance(
                    response
                ):
                    return model_dump_jsonable(response)
                return response

            return wrapper

        return decorator
