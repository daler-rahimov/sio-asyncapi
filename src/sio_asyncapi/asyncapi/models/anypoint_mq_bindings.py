from typing import Optional
from pydantic import BaseModel, Extra

from enum import Enum

from .schema import Schema


class AnypointMqDestinationType(str, Enum):
    queue = 'queue'
    exchange = 'exchange'
    fifo = 'fifo-queue'


class AnypointMqChannelBinding(BaseModel):
    """
    The Anypoint MQ Channel Binding Object.

    Note that an Anypoint MQ exchange can only be sent to, not received from. To receive
    messages sent to an exchange, an intermediary queue must be defined and bound to the
    exchange. In this bindings specification, these intermediary queues are not exposed in
    the AsyncAPI document. Instead, it is simply assumed that whenever messages must be
    received from an exchange, such an intermediary queue is involved yet invisible in
    the AsyncAPI document.
    """

    destination: Optional[str] = None
    """
    Optional, defaults to the channel name. The destination (queue or exchange) name for this
    channel. SHOULD only be specified if the channel name differs from the actual destination
    name, such as when the channel name is not a valid destination name in Anypoint MQ.
    """

    destinationType: Optional[AnypointMqDestinationType] = None
    """
    Optional, defaults to queue. The type of destination, which MUST be either exchange or queue
    or fifo-queue. SHOULD be specified to document the messaging model (publish/subscribe,
    point-to-point, strict message ordering) supported by this channel.
    """

    bindingVersion: Optional[str] = None
    """
    Optional, defaults to latest. The version of this binding.
    """


    class Config:
        extra = "allow"


class AnypointMqMessageBinding(BaseModel):
    """
    The Anypoint MQ Message Binding Object is defined by a JSON Schema.

    Note that application headers must be specified in the headers field of the standard Message
    Object and are transmitted in the properties section of the Anypoint MQ message. In contrast,
    protocol headers such as messageId must be specified in the headers field of the message
    binding object and are transmitted in the headers section of the Anypoint MQ message.
    """

    headers: Optional[Schema] = None
    """
    A Schema object containing the definitions for Anypoint MQ-specific headers (so-called protocol
    headers). This schema MUST be of type object and have a properties key. Examples of Anypoint
    MQ protocol headers are messageId and messageGroupId.
    """

    bindingVersion: Optional[str] = None
    """
    Defaults to latest. The version of this binding.
    """


    class Config:
        extra = "allow"


class AnypointMqOperationBinding(BaseModel):
    """
    This document defines how to describe Anypoint MQ-specific information in AsyncAPI documents.

    This object MUST NOT contain any properties. Its name is reserved for future use.
    """

    class Config:
        extra = "allow"


class AnypointMqServerBinding(BaseModel):
    """
    This document defines how to describe Anypoint MQ-specific information in
    AsyncAPI documents.

    This object MUST NOT contain any properties. Its name is reserved for future use.
    """

    class Config:
        extra = "allow"

