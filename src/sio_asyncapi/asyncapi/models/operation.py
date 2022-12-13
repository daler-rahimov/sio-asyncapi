from typing import Dict, List, Optional, Union

from pydantic import BaseModel, Field, Extra

from .reference import Reference
from .operation_bindings import OperationBindings
from .tag import Tag
from .external_documentation import ExternalDocumentation
from .operation_bindings import OperationBindings
from .operation_trait import OperationTrait
from .message import Message


class Operation(BaseModel):
    """Describes a publish or a subscribe operation. This provides a place to document
    how and why messages are sent and received.

    For example, an operation might describe a chat application use case where a user
    sends a text message to a group. A publish operation describes messages that are
    received by the chat application, whereas a subscribe operation describes messages
    that are sent by the chat application."""

    operationId: Optional[str] = None
    """
    Unique string used to identify the operation. The id MUST be unique among all
    operations described in the API. The operationId value is case-sensitive. Tools and
    libraries MAY use the operationId to uniquely identify an operation, therefore, it
    is RECOMMENDED to follow common programming naming conventions.
    """

    summary: Optional[str] = None
    """
    A short summary of what the operation is about.
    """

    description: Optional[str] = None
    """
    A verbose explanation of the operation. CommonMark syntax can be used for rich
    text representation.
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

    bindings: Optional[Union[OperationBindings, Reference]] = None
    """
    A map where the keys describe the name of the protocol and the values describe
    protocol-specific definitions for the operation.
    """

    traits: Optional[List[Union[OperationTrait, Reference]]] = None
    """
    A list of traits to apply to the operation object. Traits MUST be merged into the
    operation object using the JSON Merge Patch algorithm in the same order they are
    defined here.
    """

    message: Optional[Union[Message, Reference]] = None
    """
    A definition of the message that will be published or received by this operation.
    Map containing a single oneOf key is allowed here to specify multiple messages.
    However, a message MUST be valid only against one of the message objects.
    """


    class Config:
        extra = "allow"
        schema_extra = {
            "examples": [
                            {
                                "operationId": "registerUser",
                                "summary": "Action to sign a user up.",
                                "description": "A longer description",
                                "tags": [
                                    { "name": "user" },
                                    { "name": "signup" },
                                    { "name": "register" }
                                    ],
                                "message": {
                                    "headers": {
                                        "type": "object",
                                        "properties": {
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
                                        }
                                    },
                                "bindings": {
                                    "amqp": {
                                        "ack": False
                                        }
                                    },
                                "traits": [
                                    { "$ref": "#/components/operationTraits/kafka" }
                                    ]
                                }
                        ]
            }
