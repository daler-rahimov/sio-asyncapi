"""Typed Socket.IO clients that reuse server-side Pydantic models."""
from __future__ import annotations

from typing import Any, Callable, Optional, Type

import socketio
from pydantic import BaseModel

from sio_asyncapi._compat import (
    PYDANTIC_VALIDATION_ERRORS,
    is_pydantic_model_instance,
    is_pydantic_model_type,
    model_dump_jsonable,
    model_validate,
)
from sio_asyncapi.contract import (
    AsyncAPIContract,
    EmitValidationError,
    RequestValidationError,
    ResponseValidationError,
    normalize_namespace,
)


def _dump_payload(payload: Any) -> Any:
    if is_pydantic_model_instance(payload):
        return model_dump_jsonable(payload)
    return payload


class _ClientContract:
    """Shared emit/ack/on validation for sync and async clients."""

    def __init__(
        self,
        url: str,
        *,
        receive_models: dict[tuple[str, str], tuple[Any, Any]],
        emit_models: dict[tuple[str, str], Type[BaseModel]],
        validate: bool = True,
    ) -> None:
        self.url = url
        self.receive_models = receive_models
        self.emit_models = emit_models
        self.validate = validate

    @classmethod
    def models_from_server(cls, server: AsyncAPIContract) -> dict[str, Any]:
        return {
            "receive_models": dict(server.receive_models),
            "emit_models": dict(server.emit_models),
        }

    def _outgoing_models(self, event: str, namespace: Optional[str]) -> tuple[Any, Any]:
        return self.receive_models.get(
            (event, normalize_namespace(namespace)),
            (None, None),
        )

    def prepare_emit(
        self, event: str, payload: Any, namespace: Optional[str] = None
    ) -> Any:
        request_model, _ = self._outgoing_models(event, namespace)
        data = _dump_payload(payload)
        if self.validate and is_pydantic_model_type(request_model):
            try:
                model_validate(request_model, data)
            except PYDANTIC_VALIDATION_ERRORS as e:
                raise RequestValidationError.init_from_super(e) from e
        return data

    def prepare_ack(
        self, event: str, ack: Any, namespace: Optional[str] = None
    ) -> Any:
        _, response_model = self._outgoing_models(event, namespace)
        if not self.validate or not is_pydantic_model_type(response_model) or ack is None:
            return ack
        try:
            validated = model_validate(response_model, ack)
        except PYDANTIC_VALIDATION_ERRORS as e:
            raise ResponseValidationError.init_from_super(e) from e
        return model_dump_jsonable(validated)

    def prepare_incoming(
        self, event: str, payload: Any, namespace: Optional[str] = None
    ) -> Any:
        model = self.emit_models.get((event, normalize_namespace(namespace)))
        if not self.validate or not is_pydantic_model_type(model):
            return payload
        try:
            return model_validate(model, payload)
        except PYDANTIC_VALIDATION_ERRORS as e:
            raise EmitValidationError.init_from_super(e) from e


class AsyncAPIClient(_ClientContract):
    """Synchronous python-socketio client with the same models as the server."""

    def __init__(
        self,
        url: str,
        *,
        receive_models: Optional[dict[tuple[str, str], tuple[Any, Any]]] = None,
        emit_models: Optional[dict[tuple[str, str], Type[BaseModel]]] = None,
        validate: bool = True,
        **socketio_kwargs: Any,
    ) -> None:
        super().__init__(
            url,
            receive_models=receive_models or {},
            emit_models=emit_models or {},
            validate=validate,
        )
        self._client = socketio.Client(**socketio_kwargs)

    @classmethod
    def from_server(
        cls,
        server: AsyncAPIContract,
        url: str,
        *,
        validate: bool = True,
        **socketio_kwargs: Any,
    ) -> "AsyncAPIClient":
        return cls(url, validate=validate, **cls.models_from_server(server), **socketio_kwargs)

    def connect(self, **kwargs: Any) -> None:
        self._client.connect(self.url, **kwargs)

    def disconnect(self) -> None:
        self._client.disconnect()

    def emit(
        self,
        event: str,
        payload: Any = None,
        namespace: Optional[str] = None,
        callback: Optional[Callable] = None,
        **kwargs: Any,
    ) -> None:
        data = self.prepare_emit(event, payload, namespace)
        self._client.emit(event, data, namespace=namespace, callback=callback, **kwargs)

    def call(
        self,
        event: str,
        payload: Any = None,
        namespace: Optional[str] = None,
        timeout: int = 10,
        **kwargs: Any,
    ) -> Any:
        data = self.prepare_emit(event, payload, namespace)
        ack = self._client.call(
            event, data, namespace=namespace, timeout=timeout, **kwargs
        )
        return self.prepare_ack(event, ack, namespace)

    def on(
        self,
        event: str,
        namespace: Optional[str] = None,
        model: Optional[Type[BaseModel]] = None,
    ):
        ns = normalize_namespace(namespace)
        if model is not None:
            self.emit_models[(event, ns)] = model

        def decorator(handler: Callable):
            def wrapper(*args, **kwargs):
                payload = args[0] if args else kwargs.get("data")
                validated = self.prepare_incoming(event, payload, ns)
                if args:
                    args = (validated, *args[1:])
                else:
                    kwargs["data"] = validated
                return handler(*args, **kwargs)

            self._client.on(event, wrapper, namespace=namespace)
            return wrapper

        return decorator


class AsyncAPIAsyncClient(_ClientContract):
    """Asyncio python-socketio client with the same models as the server."""

    def __init__(
        self,
        url: str,
        *,
        receive_models: Optional[dict[tuple[str, str], tuple[Any, Any]]] = None,
        emit_models: Optional[dict[tuple[str, str], Type[BaseModel]]] = None,
        validate: bool = True,
        **socketio_kwargs: Any,
    ) -> None:
        super().__init__(
            url,
            receive_models=receive_models or {},
            emit_models=emit_models or {},
            validate=validate,
        )
        self._client = socketio.AsyncClient(**socketio_kwargs)

    @classmethod
    def from_server(
        cls,
        server: AsyncAPIContract,
        url: str,
        *,
        validate: bool = True,
        **socketio_kwargs: Any,
    ) -> "AsyncAPIAsyncClient":
        return cls(url, validate=validate, **cls.models_from_server(server), **socketio_kwargs)

    async def connect(self, **kwargs: Any) -> None:
        await self._client.connect(self.url, **kwargs)

    async def disconnect(self) -> None:
        await self._client.disconnect()

    async def emit(
        self,
        event: str,
        payload: Any = None,
        namespace: Optional[str] = None,
        callback: Optional[Callable] = None,
        **kwargs: Any,
    ) -> None:
        data = self.prepare_emit(event, payload, namespace)
        await self._client.emit(event, data, namespace=namespace, callback=callback, **kwargs)

    async def call(
        self,
        event: str,
        payload: Any = None,
        namespace: Optional[str] = None,
        timeout: int = 10,
        **kwargs: Any,
    ) -> Any:
        data = self.prepare_emit(event, payload, namespace)
        ack = await self._client.call(
            event, data, namespace=namespace, timeout=timeout, **kwargs
        )
        return self.prepare_ack(event, ack, namespace)

    def on(
        self,
        event: str,
        namespace: Optional[str] = None,
        model: Optional[Type[BaseModel]] = None,
    ):
        ns = normalize_namespace(namespace)
        if model is not None:
            self.emit_models[(event, ns)] = model

        def decorator(handler: Callable):
            async def wrapper(*args, **kwargs):
                payload = args[0] if args else kwargs.get("data")
                validated = self.prepare_incoming(event, payload, ns)
                if args:
                    args = (validated, *args[1:])
                else:
                    kwargs["data"] = validated
                result = handler(*args, **kwargs)
                if hasattr(result, "__await__"):
                    return await result
                return result

            self._client.on(event, wrapper, namespace=namespace)
            return wrapper

        return decorator
