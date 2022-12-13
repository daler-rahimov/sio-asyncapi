from typing import Dict, List, Optional, Union

from pydantic import BaseModel, Field, Extra, constr

from .reference import Reference
from .channel_bindings import ChannelBindings
from .operation import Operation
from .parameter import Parameter, ParameterName

ChannelUri = constr(regex=r"^([^\x00-\x20\x7f\"'%<>\\^`{|}]|%[0-9A-Fa-f]{2}|{[+#./;?&=,!@|]?((\w|%[0-9A-Fa-f]{2})(\.?(\w|%[0-9A-Fa-f]{2}))*(:[1-9]\d{0,3}|\*)?)(,((\w|%[0-9A-Fa-f]{2})(\.?(\w|%[0-9A-Fa-f]{2}))*(:[1-9]\d{0,3}|\*)?))*})*$")


class ChannelItem(BaseModel):
    """Describes the operations available on a single channel."""

    ref: Optional[str] = Field(alias="$ref")
    """
    Allows for an external definition of this channel item. The referenced structure
    MUST be in the format of a Channel Item Object. If there are conflicts between the
    referenced definition and this Channel Item's definition, the behavior is undefined.

    Deprecated: Usage of the $ref property has been deprecated.
    """

    description: Optional[str] = None
    """
    An optional description of this channel item. CommonMark syntax can be used for rich
    text representation.
    """

    servers: Optional[List[str]] = None
    """
    The servers on which this channel is available, specified as an optional unordered
    list of names (string keys) of Server Objects defined in the Servers Object (a map).
    If servers is absent or empty then this channel must be available on all servers
    defined in the Servers Object.
    """

    subscribe: Optional[Operation] = None
    """
    A definition of the SUBSCRIBE operation, which defines the messages produced by the
    application and sent to the channel.
    """

    publish: Optional[Operation] = None
    """
    A definition of the PUBLISH operation, which defines the messages consumed by the
    application from the channel.
    """

    parameters: Optional[Dict[ParameterName, Union[Parameter, Reference]]] = None
    """
    A map of the parameters included in the channel name. It SHOULD be present only
    when using channels with expressions (as defined by RFC 6570 section 2.2).
    """

    bindings: Optional[Union[ChannelBindings, Reference]] = None
    """
    A map where the keys describe the name of the protocol and the values describe
    protocol-specific definitions for the channel.
    """


    class Config:
        extra = "allow"
        schema_extra = {
            "examples": [
                            {
                                "description": "This channel is used to exchange messages about users signing up",
                                "subscribe": {
                                    "summary": "A user signed up.",
                                    "message": {
                                        "description": "A longer description of the message",
                                        "payload": {
                                            "type": "object",
                                            "properties": {
                                                "user": {
                                                    "$ref": "#/components/schemas/user"
                                                },
                                                "signup": {
                                                    "$ref": "#/components/schemas/signup"
                                                }
                                            }
                                        }
                                    }
                                },
                                "bindings": {
                                    "amqp": {
                                        "is": "queue",
                                        "queue": {
                                            "exclusive": True
                                        }
                                    }
                                }
                            }
                        ]
        }
