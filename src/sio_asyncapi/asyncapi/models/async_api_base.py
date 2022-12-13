from typing import Dict, List, Optional, Union

from pydantic import BaseModel, Extra, Field

from .components import Components
from .external_documentation import ExternalDocumentation
from .info import Info
from .reference import Reference
from .security_requirement import SecurityRequirement
from .server import Server, ServerIdentifier
from .channel import ChannelItem, ChannelUri
from .tag import Tag


class AsyncAPIBase(BaseModel):
    """This is the root document object of the AsyncAPI document."""

    asyncapi: str = "2.5.0"
    """
    **REQUIRED**. The version string signifies the version of the AsyncAPI Specification that
    the document complies to. The format for this string must be major.minor.patch. The patch
    may be suffixed by a hyphen and extra alphanumeric characters.

    A major.minor shall be used to designate the AsyncAPI Specification version, and will be
    considered compatible with the AsyncAPI Specification specified by that major.minor version.
    The patch version will not be considered by tooling, making no distinction between 1.0.0 and 1.0.1.

    In subsequent versions of the AsyncAPI Specification, care will be given such that increments
    of the minor version should not interfere with operations of tooling developed to a lower minor
    version. Thus a hypothetical 1.1.0 specification should be usable with tooling designed for 1.0.0.
    """

    param_id: Optional[str] = Field(None, alias="id")
    """
    This field represents a unique universal identifier of the application the AsyncAPI document
    is defining. It must conform to the URI format, according to RFC3986.
    """

    info: Info = ...
    """
    **REQUIRED**. The object provides metadata about the API. The metadata can be used by the
    clients if needed.
    """

    servers: Optional[Dict[ServerIdentifier, Server]] = None
    """
    The Servers Object is a map of Server Objects.A Server Object is an object representing a message
    broker, a server or any other kind of computer program capable of sending and/or receiving data.
    This object is used to capture details such as URIs, protocols and security configuration.
    """

    defaultContentType: Optional[str] = None
    """
    A string representing the default content type to use when encoding/decoding a message's payload.
    The value MUST be a specific media type (e.g. application/json). This value MUST be used by schema
    parsers when the contentType property is omitted.

    In case a message can't be encoded/decoded using this value, schema parsers MUST use their default
    content type.
    """

    channels: Dict[ChannelUri, ChannelItem]
    """
    **REQUIRED**. Holds the relative paths to the individual channel and their operations. Channel paths
    are relative to servers. Channels are also known as "topics", "routing keys", "event types" or "paths".
    """

    components: Optional[Components] = None
    """
    Holds a set of reusable objects for different aspects of the AsyncAPI specification. All objects
    defined within the components object will have no effect on the API unless they are explicitly
    referenced from properties outside the components object.
    """

    tags: Optional[List[Tag]] = None
    """
    A list of tags used by the specification with additional metadata. Each tag name in the list MUST be unique.
    """

    externalDocs: Optional[ExternalDocumentation] = None
    """
    Additional external documentation.
    """

    class Config:
        extra = "allow"
