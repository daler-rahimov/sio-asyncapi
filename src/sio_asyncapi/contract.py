"""Shared AsyncAPI documentation and validation contract for Socket.IO servers."""
from __future__ import annotations

import functools
import inspect
import logging
from typing import Any, Callable, Optional, Type, Union

from pydantic import BaseModel

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
CONNECT_SKIP_ARG_NAMES = SKIP_PAYLOAD_ARG_NAMES | {"environ"}


def normalize_namespace(namespace: Optional[str]) -> str:
    """Normalize Socket.IO namespace values."""
    return namespace or DEFAULT_NAMESPACE


def _arg_names(handler: Callable) -> list[str]:
    try:
        return list(inspect.getfullargspec(inspect.unwrap(handler)).args)
    except (TypeError, IndexError):
        return []


def payload_arg_index(handler: Callable, event_name: str) -> Optional[int]:
    """Return the positional index of the Socket.IO payload argument."""
    names = _arg_names(handler)
    skips = CONNECT_SKIP_ARG_NAMES if event_name == "connect" else SKIP_PAYLOAD_ARG_NAMES
    index = 0
    while index < len(names) and names[index] in skips:
        index += 1
    if event_name == "disconnect" or index >= len(names):
        return None
    return index


def payload_annotation(handler: Callable, event_name: str) -> Any:
    """Return the typehint for the Socket.IO payload argument."""
    names = _arg_names(handler)
    skips = CONNECT_SKIP_ARG_NAMES if event_name == "connect" else SKIP_PAYLOAD_ARG_NAMES
    while names and names[0] in skips:
        names.pop(0)
    if event_name == "disconnect" or not names:
        return None
    return inspect.unwrap(handler).__annotations__.get(names[0], "NotProvided")


class RequestValidationError(BaseValidationError):
    pass


class ResponseValidationError(BaseValidationError):
    pass


class EmitValidationError(BaseValidationError):
    pass


class AsyncAPIContract:
    """Documentation + validation shared by Flask and asyncio Socket.IO servers."""

    validate: bool
    generate_docs: bool
    serve_docs: bool
    auth_model: Optional[Type[BaseModel]]
    asyncapi_doc: AsyncAPIDoc
    emit_models: dict[tuple[str, str], Type[BaseModel]]
    receive_models: dict[tuple[str, str], tuple[Any, Any]]

    def _init_contract(
        self,
        *,
        validate: bool = False,
        generate_docs: bool = True,
        serve_docs: Optional[bool] = None,
        version: str = "1.0.0",
        title: str = "Demo Chat API",
        description: str = "Demo Chat API",
        server_url: str = "http://localhost:5000",
        server_name: str = "BACKEND",
        auth_model: Optional[Type[BaseModel]] = None,
        security_scheme: Optional[dict] = None,
        security_scheme_name: str = "socketioAuth",
    ) -> None:
        self.validate = validate
        self.generate_docs = generate_docs
        self.serve_docs = generate_docs if serve_docs is None else serve_docs
        self.auth_model = auth_model
        self.asyncapi_doc = AsyncAPIDoc.default_init(
            version=version,
            title=title,
            description=description,
            server_url=server_url,
            server_name=server_name,
            security_scheme=security_scheme,
            security_scheme_name=security_scheme_name,
            auth_model=auth_model if generate_docs else None,
        )
        self.emit_models = {}
        self.receive_models = {}

    def get_agent_schema(self) -> dict[str, Any]:
        """Return the compact agent-friendly event catalog."""
        return self.asyncapi_doc.get_agent_schema()

    def get_agent_schema_json(self) -> str:
        """Return the compact agent-friendly event catalog as JSON."""
        return self.asyncapi_doc.get_agent_schema_json()

    def doc_emit(
        self,
        event: str,
        model: Type[BaseModel],
        description: str = "",
        namespace: Optional[str] = None,
        *,
        discription: Optional[str] = None,
    ):
        """Register a server-to-client emit event for validation and docs."""
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

    def _validate_emit_payload(
        self,
        event: str,
        payload: Any,
        namespace: Optional[str],
    ) -> None:
        if not self.validate:
            return
        model = self.emit_models.get((event, normalize_namespace(namespace)))
        if model is None:
            return
        try:
            model_validate(model, payload)
        except PYDANTIC_VALIDATION_ERRORS as e:
            logger.error("Error validating emit '%s': %s", event, e)
            raise EmitValidationError.init_from_super(e) from e

    def _register_receiver(
        self,
        handler: Callable,
        message: str,
        namespace: Optional[str] = None,
        *,
        get_from_typehint: bool = False,
        response_model: Optional[Union[Type[BaseModel], NotProvidedType]] = None,
        request_model: Optional[Union[Type[BaseModel], NotProvidedType]] = None,
    ) -> Callable:
        if get_from_typehint:
            possible_request_model = payload_annotation(handler, message)
            possible_response_model = inspect.unwrap(handler).__annotations__.get(
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

        normalized_namespace = normalize_namespace(namespace)
        self.receive_models[(message, normalized_namespace)] = (
            request_model,
            response_model,
        )

        if self.generate_docs:
            self.asyncapi_doc.add_new_receiver(
                handler,
                message,
                ack_data_model=response_model,
                payload_model=request_model,
                namespace=normalized_namespace,
            )

        return self._wrap_handler(
            handler,
            request_model=request_model,
            response_model=response_model,
            event_name=message,
        )

    def _inject_request(
        self,
        handler: Callable,
        event_name: str,
        args: tuple,
        kwargs: dict,
        request_model: Any,
    ) -> tuple[tuple, dict]:
        index = payload_arg_index(handler, event_name)
        request = None
        request_provided = False
        did_request_came_as_arg = False

        if index is not None and len(args) > index:
            did_request_came_as_arg = True
            request_provided = True
            request = args[index]
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
            if did_request_came_as_arg and index is not None:
                args = args[:index] + (request,) + args[index + 1:]
            else:
                kwargs["request"] = request
        return args, kwargs

    def _process_response(
        self,
        event_name: Optional[str],
        response_model: Any,
        response: Any,
    ) -> Any:
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

        if event_name not in LIFECYCLE_EVENTS and is_pydantic_model_instance(response):
            return model_dump_jsonable(response)
        return response

    def _wrap_handler(
        self,
        handler: Callable,
        request_model: Any,
        response_model: Any,
        event_name: str,
    ) -> Callable:
        if inspect.iscoroutinefunction(inspect.unwrap(handler)):
            @functools.wraps(handler)
            async def async_wrapper(*args, **kwargs):
                args, kwargs = self._inject_request(
                    handler, event_name, args, kwargs, request_model
                )
                response = await handler(*args, **kwargs)
                return self._process_response(event_name, response_model, response)

            return async_wrapper

        @functools.wraps(handler)
        def wrapper(*args, **kwargs):
            args, kwargs = self._inject_request(
                handler, event_name, args, kwargs, request_model
            )
            response = handler(*args, **kwargs)
            return self._process_response(event_name, response_model, response)

        return wrapper
