from typing import List, Optional, Union

from pydantic import BaseModel, Extra

from .reference import Reference
from .tag import Tag
from .external_documentation import ExternalDocumentation
from .schema import Schema
from .message_bindings import MessageBindings
from .message_example import MessageExample
from .correlation_id import CorrelationId


class MessageTrait(BaseModel):
    """
    Describes a trait that MAY be applied to a Message Object. This object MAY contain
    any property from the Message Object, except payload and traits.

    If you're looking to apply traits to an operation, see the Operation Trait Object.
    """

    headers: Optional[Union[Schema, Reference]] = None
    """
    Schema definition of the application headers. Schema MUST be of type "object". It
    MUST NOT define the protocol headers.
    """

    correlationId: Optional[Union[CorrelationId, Reference]] = None
    """
    Definition of the correlation ID used for message tracing or matching.
    """

    schemaFormat: Optional[str] = None
    """
    A string containing the name of the schema format/language used to define the message
    payload. If omitted, implementations should parse the payload as a Schema object.
    """

    contentType: Optional[str] = None
    """
    The content type to use when encoding/decoding a message's payload. The value MUST be
    a specific media type (e.g. application/json). When omitted, the value MUST be the
    one specified on the defaultContentType field.
    """

    name: Optional[str] = None
    """
    A machine-friendly name for the message.
    """

    title: Optional[str] = None
    """
    A human-friendly title for the message.
    """

    summary: Optional[str] = None
    """
    A short summary of what the message is about.
    """

    description: Optional[str] = None
    """
    A verbose explanation of the message. CommonMark syntax can be used for rich text
    representation.
    """

    tags: Optional[List[Tag]] = None
    """
    A list of tags for API documentation control. Tags can be used for logical grouping
    of operations.
    """

    externalDocs: Optional[ExternalDocumentation] = None
    """
    Additional external documentation for this operation.
    """

    bindings: Optional[Union[MessageBindings, Reference]] = None
    """
    A map where the keys describe the name of the protocol and the values describe
    protocol-specific definitions for the message.
    """

    examples: Optional[List[MessageExample]] = None
    """
    List of examples.
    """


    class Config:
        extra = "allow"
        schema_extra = {
            "examples": [
                            {
                                "schemaFormat": "application/vnd.apache.avro+json;version=1.9.0",
                                "contentType": "application/json"
                            }
                        ]
                }
