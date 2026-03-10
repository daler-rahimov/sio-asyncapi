import json
from typing import Any, Type

from pydantic import BaseModel as BaseModelV2
from pydantic import ValidationError as ValidationErrorV2

from sio_asyncapi._pydantic import BaseModel as BaseModelV1Compat
from sio_asyncapi._pydantic import ValidationError as ValidationErrorV1Compat

PYDANTIC_MODEL_TYPES = tuple(
    model_type
    for model_type in (BaseModelV2, BaseModelV1Compat)
    if isinstance(model_type, type)
)

PYDANTIC_VALIDATION_ERRORS = tuple(
    error_type
    for error_type in (ValidationErrorV2, ValidationErrorV1Compat)
    if isinstance(error_type, type)
)


def is_pydantic_model_type(model: Any) -> bool:
    """Return True when the value is a supported Pydantic model class."""
    return isinstance(model, type) and issubclass(model, PYDANTIC_MODEL_TYPES)


def is_pydantic_model_instance(value: Any) -> bool:
    """Return True when the value is a supported Pydantic model instance."""
    return isinstance(value, PYDANTIC_MODEL_TYPES)


def model_validate(model: Type[Any], data: Any) -> Any:
    """Validate data against either a Pydantic v1 or v2 model class."""
    if hasattr(model, "model_validate"):
        return model.model_validate(data)
    return model.parse_obj(data)


def model_schema(model: Type[Any]) -> dict[str, Any]:
    """Return a JSON schema for either a Pydantic v1 or v2 model class."""
    if hasattr(model, "model_json_schema"):
        return model.model_json_schema()
    return model.schema()


def model_dump(instance: Any, **kwargs: Any) -> dict[str, Any]:
    """Dump a model to a Python dict for either Pydantic major version."""
    if hasattr(instance, "model_dump"):
        return instance.model_dump(**kwargs)
    return instance.dict(**kwargs)


def model_dump_json(instance: Any, **kwargs: Any) -> str:
    """Dump a model to JSON for either Pydantic major version."""
    if hasattr(instance, "model_dump_json"):
        return instance.model_dump_json(**kwargs)
    return instance.json(**kwargs)


class BaseValidationError(Exception):
    """Version-agnostic wrapper around a Pydantic validation error."""

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
