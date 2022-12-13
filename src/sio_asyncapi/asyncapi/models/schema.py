from typing import Optional

from pydantic import BaseModel

from .json_schema import JsonSchemaObject
from .external_documentation import ExternalDocumentation


class Schema(BaseModel):
    """
    The Schema Object allows the definition of input and output data types.
    These types can be objects, but also primitives and arrays. This object
    is a superset of the JSON Schema Specification Draft 07.

    Further information about the properties can be found in JSON Schema Core
    and JSON Schema Validation. Unless stated otherwise, the property definitions
    follow the JSON Schema specification as referenced here.

    The AsyncAPI Schema Object is a JSON Schema vocabulary which extends JSON
    Schema Core and Validation vocabularies.
    """

    discriminator: Optional[str] = None
    """
    Adds support for polymorphism. The discriminator is the schema property name
    that is used to differentiate between other schema that inherit this schema.
    The property name used MUST be defined at this schema and it MUST be in the
    required property list. When used, the value MUST be the name of this schema
    or any schema that inherits it.
    """

    externalDocs: Optional[ExternalDocumentation] = None
    """
    Additional external documentation for this schema.
    """

    deprecated: Optional[bool] = False
    """
    Specifies that a schema is deprecated and SHOULD be transitioned out of usage.
    Default value is false.
    """


    class Config:
        extra = "allow"
        schema_extra = {
            "examples": [
                {
                    "type": "string",
                    "format": "email"
                }
            ]
        }
