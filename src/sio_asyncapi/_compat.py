"""Pydantic v2 helpers used across the library."""
import json
from typing import Any, Type

from pydantic import BaseModel, ValidationError

PYDANTIC_VALIDATION_ERRORS = (ValidationError,)


def is_pydantic_model_type(model: Any) -> bool:
    """Return True when the value is a Pydantic v2 model class."""
    return isinstance(model, type) and issubclass(model, BaseModel)


def is_pydantic_model_instance(value: Any) -> bool:
    """Return True when the value is a Pydantic v2 model instance."""
    return isinstance(value, BaseModel)


def model_validate(model: Type[BaseModel], data: Any) -> Any:
    """Validate data against a Pydantic v2 model class."""
    return model.model_validate(data)


def model_schema(model: Type[BaseModel]) -> dict[str, Any]:
    """Return a JSON Schema 2020-12 document for a Pydantic v2 model."""
    return model.model_json_schema()


def model_dump(instance: Any, **kwargs: Any) -> dict[str, Any]:
    """Dump a model to a Python dict."""
    return instance.model_dump(**kwargs)


def model_dump_jsonable(instance: Any) -> dict[str, Any]:
    """Dump a model to a JSON-compatible dict for Socket.IO payloads."""
    return instance.model_dump(mode="json")


def model_dump_json(instance: Any, **kwargs: Any) -> str:
    """Dump a model to a JSON string."""
    return instance.model_dump_json(**kwargs)


def field_schema_extra(**extra: Any) -> dict[str, Any]:
    """Return Field kwargs that attach JSON Schema extras (Pydantic v2)."""
    return {"json_schema_extra": extra}


class BaseValidationError(Exception):
    """Wrapper around a Pydantic validation error."""

    def __init__(self, parent: Exception):
        super().__init__(str(parent))
        self.parent = parent
        self.model = getattr(parent, "model", None)
        self.raw_errors = getattr(parent, "raw_errors", None)

    @classmethod
    def init_from_super(cls, parent: Exception) -> "BaseValidationError":
        return cls(parent)

    def errors(self) -> list[dict[str, Any]]:
        return self.parent.errors()

    def json(self, *args: Any, **kwargs: Any) -> str:
        if hasattr(self.parent, "json"):
            return self.parent.json(*args, **kwargs)
        return json.dumps(self.errors())

    def __getattr__(self, name: str) -> Any:
        return getattr(self.parent, name)
