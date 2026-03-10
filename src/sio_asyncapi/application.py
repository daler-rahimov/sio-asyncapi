import inspect
from typing import Callable, Optional, Type, Union

from flask import Flask
from flask_socketio import SocketIO
from loguru import logger
from sio_asyncapi._pydantic import BaseModel

from sio_asyncapi._compat import (
    BaseValidationError,
    PYDANTIC_VALIDATION_ERRORS,
    is_pydantic_model_instance,
    is_pydantic_model_type,
    model_dump_json,
    model_validate,
)
from sio_asyncapi.asyncapi.docs import AsyncAPIDoc, NotProvidedType


DEFAULT_NAMESPACE = "/"


def normalize_namespace(namespace: Optional[str]) -> str:
    """Normalize Socket.IO namespace values."""
    return namespace or DEFAULT_NAMESPACE


class RequestValidationError(BaseValidationError):
    pass


class ResponseValidationError(BaseValidationError):
    pass


class EmitValidationError(BaseValidationError):
    pass


class AsyncAPISocketIO(SocketIO):
    """Inherits the :class:`flask_socketio.SocketIO` class.
    Adds ability to validate with pydantic models and generate AsycnAPI spe.

    Example::
        socket = AsyncAPISocketIO(app, async_mode='threading', logger=True)
        class TokenModel(BaseModel):
            token: int

        class UserModel(BaseModel):
            name: str
            id: int

        @socket.on('get_user', response_model=UserModel)
        def get_user():
            return {"name": Bob, "id": 123}
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
        **kwargs,
    ):
        """Create AsycnAPISocketIO

        Args:
            app (Optional[Flask]): flask app
            validation (bool, optional): If True request and response will be validated. Defaults to True.
            generate_docs (bool, optional): If True AsyncAPI specs will be generated. Defaults to False.
            version (str, optional): AsyncAPI version. Defaults to "1.0.0".
            title (str, optional): AsyncAPI title. Defaults to "Demo Chat API".
            description (str, optional): AsyncAPI description. Defaults to "Demo Chat API".
            server_url (str, optional): AsyncAPI server url. Defaults to "http://localhost:5000".
            server_name (str, optional): AsyncAPI server name. Defaults to "BACKEND".
        """
        self.validate = validate
        self.generate_docs = generate_docs
        self.asyncapi_doc: AsyncAPIDoc = AsyncAPIDoc.default_init(
            version=version,
            title=title,
            description=description,
            server_url=server_url,
            server_name=server_name,
        )
        super().__init__(app=app, *args, **kwargs)
        self.emit_models: dict[tuple[str, str], Type[BaseModel]] = {}

    def emit(self, event: str, *args, **kwargs):
        """
        Overrides emit in order to validate data with pydantic models

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
                    logger.error(f"Error validating emit '{event}': {e}")
                    raise EmitValidationError.init_from_super(e) from e
        return super().emit(event, *args, **kwargs)

    def doc_emit(
        self,
        event: str,
        model: Type[BaseModel],
        discription: str = "",
        namespace: Optional[str] = None,
    ):
        """
        Decorator to register/document a SocketIO emit event. This will be
        used to generate AsyncAPI specs and validate emits calls.

        Args:
            event (str): event name
            model (Type[BaseModel]): pydantic model
        """

        def decorator(func):
            normalized_namespace = normalize_namespace(namespace)
            event_key = (event, normalized_namespace)
            if self.emit_models.get(event_key):
                raise ValueError(
                    f"Event {event} already registered for namespace {normalized_namespace}"
                )
            self.emit_models[event_key] = model
            self.asyncapi_doc.add_new_sender(
                event,
                model,
                discription,
                namespace=normalized_namespace,
            )
            return func

        return decorator

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
                try:
                    first_arg_name = inspect.getfullargspec(handler)[0][0]
                except IndexError:
                    posible_request_model = None
                else:
                    posible_request_model = handler.__annotations__.get(
                        first_arg_name, "NotProvided"
                    )
                posible_response_model = handler.__annotations__.get(
                    "return", "NotProvided"
                )
                if request_model is None:
                    request_model = posible_request_model  # type: ignore
                if response_model is None:
                    response_model = posible_response_model  # type: ignore

            if self.generate_docs:
                self.asyncapi_doc.add_new_receiver(
                    handler,
                    message,
                    ack_data_model=response_model,
                    payload_model=request_model,
                    namespace=normalize_namespace(namespace),
                )

            def wrapper(*args, **kwargs):
                new_handler = self._handle_all(
                    request_model=request_model,
                    response_model=response_model,
                )(handler)
                return new_handler(*args, **kwargs)

            super(AsyncAPISocketIO, self).on(message, namespace)(wrapper)
            return wrapper

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

                if request_provided:
                    try:
                        if self.validate and request_model and is_pydantic_model_type(
                            request_model
                        ):
                            model_validate(request_model, request)
                    except PYDANTIC_VALIDATION_ERRORS as e:
                        logger.error(f"ValidationError for incoming request: {e}")
                        raise RequestValidationError.init_from_super(e) from e

                    if request_model and is_pydantic_model_type(request_model):
                        request = model_validate(request_model, request)
                        if did_request_came_as_arg:
                            args = (request, *args[1:])
                        else:
                            kwargs["request"] = request

                response = handler(*args, **kwargs)
                if response is not None:
                    try:
                        if self.validate and response_model and is_pydantic_model_type(
                            response_model
                        ):
                            model_validate(response_model, response)
                    except PYDANTIC_VALIDATION_ERRORS as e:
                        logger.error(f"ValidationError for outgoing response: {e}")
                        raise ResponseValidationError.init_from_super(e) from e

                if is_pydantic_model_instance(response):
                    return model_dump_json(response)
                return response

            return wrapper

        return decorator
