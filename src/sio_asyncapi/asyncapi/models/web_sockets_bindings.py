from typing import Optional
from enum import Enum
from pydantic import BaseModel, Extra

from .schema import Schema


class WebSocketsMethod(str, Enum):
    get = 'GET'
    post = 'POST'


class WebSocketsChannelBinding(BaseModel):
    """
    When using WebSockets, the channel represents the connection. Unlike other
    protocols that support multiple virtual channels (topics, routing keys, etc.)
    per connection, WebSockets doesn't support virtual channels or, put it another
    way, there's only one channel and its characteristics are strongly related to
    the protocol used for the handshake, i.e., HTTP.
    """

    method: Optional[WebSocketsMethod] = None
    """
    The HTTP method to use when establishing the connection. Its value MUST be
    either GET or POST.
    """

    query: Optional[Schema] = None
    """
    A Schema object containing the definitions for each query parameter. This
    schema MUST be of type object and have a properties key.
    """

    headers: Optional[Schema] = None
    """
    A Schema object containing the definitions of the HTTP headers to use when
    establishing the connection. This schema MUST be of type object and have a
    properties key.
    """

    bindingVersion: Optional[str] = None
    """
    The version of this binding. If omitted, "latest" MUST be assumed.
    """


class WebSocketsMessageBinding(BaseModel):
    """
    This document defines how to describe WebSockets-specific information on AsyncAPI.

    This object MUST NOT contain any properties. Its name is reserved for future use.
    """

    class Config:
        extra = "allow"


class WebSocketsOperationBinding(BaseModel):
    """
    This document defines how to describe WebSockets-specific information on AsyncAPI.

    This object MUST NOT contain any properties. Its name is reserved for future use.
    """

    class Config:
        extra = "allow"


class WebSocketsServerBinding(BaseModel):
    """
    This document defines how to describe WebSockets-specific information on AsyncAPI.

    This object MUST NOT contain any properties. Its name is reserved for future use.
    """

    class Config:
        extra = "allow"


class WebSocketsChannelBinding(BaseModel):
    """
    This document defines how to describe WebSockets-specific information on AsyncAPI.

    When using WebSockets, the channel represents the connection. Unlike other protocols
    that support multiple virtual channels (topics, routing keys, etc.) per connection,
    WebSockets doesn't support virtual channels or, put it another way, there's only one
    channel and its characteristics are strongly related to the protocol used for the
    handshake, i.e., HTTP.
    """

    method: Optional[WebSocketsMethod] = None
    """
    The HTTP method to use when establishing the connection.
    Its value MUST be either GET or POST.
    """

    query: Optional[Schema] = None
    """
    A Schema object containing the definitions for each query parameter.
    This schema MUST be of type object and have a properties key.
    """

    headers: Optional[Schema] = None
    """
    A Schema object containing the definitions of the HTTP headers to use
    when establishing the connection. This schema MUST be of type object
    and have a properties key.
    """

    bindingVersion: Optional[str] = None
    """
    The version of this binding. If omitted, "latest" MUST be assumed.
    """

    class Config:
        extra = "allow"

