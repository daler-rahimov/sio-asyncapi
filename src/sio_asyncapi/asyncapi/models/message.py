from typing import List, Optional, Union

from pydantic import BaseModel, Field, Extra

from .reference import Reference
from .tag import Tag
from .external_documentation import ExternalDocumentation
from .schema import Schema
from .message_bindings import MessageBindings
from .message_trait import MessageTrait
from .message_example import MessageExample
from .correlation_id import CorrelationId


class Message(BaseModel):
    """
    Describes a message received on a given channel and operation.
    """

    headers: Optional[Union[Schema, Reference]] = None
    """
    Schema definition of the application headers. Schema MUST be of type "object".
    It MUST NOT define the protocol headers.
    """

    payload: Optional[Schema] = None
    """
    Definition of the message payload. It can be of any type but defaults to Schema
    object. It must match the schema format, including encoding type - e.g Avro should
    be inlined as either a YAML or JSON object NOT a string to be parsed as YAML or JSON.
    """

    correlationId: Optional[Union[CorrelationId, Reference]] = None
    """
    Definition of the correlation ID used for message tracing or matching.
    """

    schemaFormat: Optional[str] = None
    """
    A string containing the name of the schema format used to define the message payload.
    If omitted, implementations should parse the payload as a Schema object. When the payload
    is defined using a $ref to a remote file, it is RECOMMENDED the schema format includes
    the file encoding type to allow implementations to parse the file correctly.
    E.g., adding +yaml if content type is application/vnd.apache.avro results in
    application/vnd.apache.avro+yaml.

    Check out the supported schema formats table for more information. Custom values are
    allowed but their implementation is OPTIONAL. A custom value MUST NOT refer to one of the
    schema formats listed in the table.
    """

    contentType: Optional[str] = None
    """
    The content type to use when encoding/decoding a message's payload. The value MUST be a
    specific media type (e.g. application/json). When omitted, the value MUST be the one
    specified on the defaultContentType field.
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

    traits: Optional[List[Union[MessageTrait, Reference]]] = None
    """
    A list of traits to apply to the message object. Traits MUST be merged into the
    message object using the JSON Merge Patch algorithm in the same order they are defined
    here. The resulting object MUST be a valid Message Object.
    """


    class Config:
        extra = "allow"
        schema_extra = {
            "examples": [
                            {
                                "name": "UserSignup",
                                "title": "User signup",
                                "summary": "Action to sign a user up.",
                                "description": "A longer description",
                                "contentType": "application/json",
                                "tags": [
                                    { "name": "user" },
                                    { "name": "signup" },
                                    { "name": "register" }
                                ],
                                "headers": {
                                    "type": "object",
                                    "properties": {
                                        "correlationId": {
                                            "description": "Correlation ID set by application",
                                            "type": "string"
                                        },
                                        "applicationInstanceId": {
                                            "description": "Unique identifier for a given instance of the publishing application",
                                            "type": "string"
                                        }
                                    }
                                },
                                "payload": {
                                    "type": "object",
                                    "properties": {
                                        "user": {
                                            "$ref": "#/components/schemas/userCreate"
                                        },
                                        "signup": {
                                            "$ref": "#/components/schemas/signup"
                                        }
                                    }
                                },
                                "correlationId": {
                                    "description": "Default Correlation ID",
                                    "location": "$message.header#/correlationId"
                                },
                                "traits": [
                                    { "$ref": "#/components/messageTraits/commonHeaders" }
                                ],
                                "examples": [
                                    {
                                        "name": "SimpleSignup",
                                        "summary": "A simple UserSignup example message",
                                        "headers": {
                                            "correlationId": "my-correlation-id",
                                            "applicationInstanceId": "myInstanceId"
                                        },
                                        "payload": {
                                            "user": {
                                                "someUserKey": "someUserValue"
                                            },
                                            "signup": {
                                                "someSignupKey": "someSignupValue"
                                            }
                                        }
                                    }
                                ]
                            }
                        ]
                }
