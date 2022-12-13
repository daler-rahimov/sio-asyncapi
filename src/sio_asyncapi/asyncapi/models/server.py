from typing import Dict, List, Optional, Union

from pydantic import BaseModel, Extra, constr

from .reference import Reference
from .server_bindings import ServerBindings
from .security_requirement import SecurityRequirement
from .server_variable import ServerVariable

ServerIdentifier = constr(regex=r'^[A-Za-z0-9_\-]+$')


class Server(BaseModel):
    """An object representing a Server."""

    url: str = ...
    """
    **REQUIRED**. A URL to the target host. This URL supports Server Variables and MAY be
    relative, to indicate that the host location is relative to the location where the AsyncAPI
    document is being served. Variable substitutions will be made when a variable is named in {braces}.
    """

    protocol: str = ...
    """
    **REQUIRED**. The protocol this URL supports for connection. Supported protocol include, but are
    not limited to: amqp, amqps, http, https, ibmmq, jms, kafka, kafka-secure, anypointmq, mqtt,
    secure-mqtt, solace, stomp, stomps, ws, wss, mercure.
    """

    protocolVersion: Optional[str] = None
    """
    The version of the protocol used for connection. For instance: AMQP 0.9.1, HTTP 2.0, Kafka 1.0.0, etc.
    """

    description: Optional[str] = None
    """
    An optional string describing the host designated by the URL. CommonMark syntax MAY be used for
    rich text representation.
    """

    variables: Optional[Dict[str, ServerVariable]] = None
    """
    A map between a variable name and its value. The value is used for substitution in the server's URL template.
    """

    security: Optional[Dict[str, SecurityRequirement]] = None
    """
    A declaration of which security mechanisms can be used with this server. The list of values includes
    alternative security requirement objects that can be used. Only one of the security requirement
    objects need to be satisfied to authorize a connection or operation.
    """

    bindings: Optional[Union[ServerBindings, Reference]] = None
    """
    A map where the keys describe the name of the protocol and the values describe protocol-specific
    definitions for the server.
    """


    class Config:
        extra = "allow"
        schema_extra = {
            "examples": [
                            {
                                "url": "development.gigantic-server.com",
                                "description": "Development server",
                                "protocol": "kafka",
                                "protocolVersion": "1.0.0"
                            }
                        ]
        }
