from typing import Dict, Optional, Union

from pydantic import BaseModel, Extra, constr

from .parameter import Parameter
from .reference import Reference
from .schema import Schema
from .server import Server
from .channel import ChannelItem
from .message import Message
from .security_scheme import SecurityScheme
from .correlation_id import CorrelationId
from .operation_trait import OperationTrait
from .message_trait import MessageTrait
from .server_bindings import ServerBindings
from .channel_bindings import ChannelBindings
from .operation_bindings import OperationBindings
from .message_bindings import MessageBindings


ComponentKey = constr(regex=r"^[A-Za-z0-9_\-]+$")


class Components(BaseModel):
    """
    Holds a set of reusable objects for different aspects of the AsyncAPI specification. All
    objects defined within the components object will have no effect on the API unless they
    are explicitly referenced from properties outside the components object.
    """

    schemas: Optional[Dict[ComponentKey, Union[Schema, Reference]]] = None
    """
    An object to hold reusable Schema Objects.
    """

    servers: Optional[Dict[ComponentKey, Union[Server, Reference]]] = None
    """
    An object to hold reusable Server Objects.
    """

    channels: Optional[Dict[ComponentKey, ChannelItem]] = None
    """
    An object to hold reusable Channel Item Objects.
    """

    messages: Optional[Dict[ComponentKey, Union[Message, Reference]]] = None
    """
    An object to hold reusable Message Objects.
    """

    securitySchemes: Optional[Dict[ComponentKey, Union[SecurityScheme, Reference]]] = None
    """
    An object to hold reusable Security Scheme Objects.
    """

    parameters: Optional[Dict[ComponentKey, Union[Parameter, Reference]]] = None
    """
    An object to hold reusable Parameter Objects.
    """

    correlationIds: Optional[Dict[ComponentKey, Union[CorrelationId, Reference]]] = None
    """
    An object to hold reusable Correlation ID Objects.
    """

    operationTraits: Optional[Dict[ComponentKey, Union[OperationTrait, Reference]]] = None
    """
    An object to hold reusable Operation Trait Objects.
    """

    messageTraits: Optional[Dict[ComponentKey, Union[MessageTrait, Reference]]] = None
    """
    An object to hold reusable Message Trait Objects.
    """

    serverBindings: Optional[Dict[ComponentKey, Union[ServerBindings, Reference]]] = None
    """
    An object to hold reusable Server Bindings Objects.
    """

    channelBindings: Optional[Dict[ComponentKey, Union[ChannelBindings, Reference]]] = None
    """
    An object to hold reusable Channel Bindings Objects.
    """

    operationBindings: Optional[Dict[ComponentKey, Union[OperationBindings, Reference]]] = None
    """
    An object to hold reusable Operation Bindings Objects.
    """

    messageBindings: Optional[Dict[str, Union[MessageBindings, Reference]]] = None
    """
    An object to hold reusable Message Bindings Objects.
    """


    class Config:
        extra = "allow"
        schema_extra = {
            "examples": [
                            {
                            "components": {
                                "schemas": {
                                "Category": {
                                    "type": "object",
                                    "properties": {
                                    "id": {
                                        "type": "integer",
                                        "format": "int64"
                                    },
                                    "name": {
                                        "type": "string"
                                    }
                                    }
                                },
                                "Tag": {
                                    "type": "object",
                                    "properties": {
                                    "id": {
                                        "type": "integer",
                                        "format": "int64"
                                    },
                                    "name": {
                                        "type": "string"
                                    }
                                    }
                                }
                                },
                                "servers": {
                                "development": {
                                    "url": "development.gigantic-server.com",
                                    "description": "Development server",
                                    "protocol": "amqp",
                                    "protocolVersion": "0.9.1"
                                }
                                },
                                "channels": {
                                "user/signedup": {
                                    "subscribe": {
                                    "message": {
                                        "$ref": "#/components/messages/userSignUp"
                                    }
                                    }
                                }
                                },
                                "messages": {
                                "userSignUp": {
                                    "summary": "Action to sign a user up.",
                                    "description": "Multiline description of what this action does.\nHere you have another line.\n",
                                    "tags": [
                                    {
                                        "name": "user"
                                    },
                                    {
                                        "name": "signup"
                                    }
                                    ],
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
                                }
                                },
                                "parameters": {
                                "userId": {
                                    "description": "Id of the user.",
                                    "schema": {
                                    "type": "string"
                                    }
                                }
                                },
                                "correlationIds": {
                                "default": {
                                    "description": "Default Correlation ID",
                                    "location": "$message.header#/correlationId"
                                }
                                },
                                "messageTraits": {
                                "commonHeaders": {
                                    "headers": {
                                    "type": "object",
                                    "properties": {
                                        "my-app-header": {
                                        "type": "integer",
                                        "minimum": 0,
                                        "maximum": 100
                                        }
                                    }
                                    }
                                }
                                }
                            }
                        }
            ]
        }
