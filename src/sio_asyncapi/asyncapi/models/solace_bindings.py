from typing import Optional, List

from enum import Enum

from pydantic import BaseModel, Extra


class SolaceMessageType(BaseModel):
    """
    This object MUST NOT contain any properties. Its name is reserved for future use.
    """


    class Config:
        extra = "allow"


class SolaceDestinationType(str, Enum):
    queue = 'queue'
    topic = 'topic'


class SolaceQueueAccessType(str, Enum):
    exclusive = 'exclusive'
    nonExclusive = 'nonExclusive'


class SolaceQueue(BaseModel):
    """
    Solace queue definition.
    """

    name: Optional[str] = None
    """
    The name of the queue, only applicable when destinationType is 'queue'.
    """

    topicSubscriptions: Optional[List[str]] = None
    """
    A list of topics that the queue subscribes to, only applicable when
    destinationType is 'queue'.
    """

    accessType: Optional[SolaceQueueAccessType] = None
    """
    'exclusive' or 'nonExclusive'. This is documented here. Only applicable
    when destinationType is 'queue'.
    """


    class Config:
        extra = "allow"


class SolaceDestination(BaseModel):
    """
    Each destination has the following structure. Note that bindings under a
    'subscribe' operation define the behaviour of publishers, and those under
    a 'publish' operation define how subscribers are configured.
    """

    destinationType: Optional[SolaceDestinationType] = None
    """
    'queue' or 'topic'. If the type is queue, then the subscriber can bind to
    the queue, which in turn will subscribe to the topic as represented by the
    channel name.
    """

    deliveryMode: Optional[str] = None
    """
    'direct' or 'persistent'. This determines the quality of service for publishing
    messages as documented here. Default is 'persistent'.
    """

    queue: Optional[SolaceQueue] = None
    """
    MQTT queue definition.
    """


class SolaceMessageBinding(BaseModel):
    """
    This document defines how to describe Solace-specific information with AsyncAPI.

    This object MUST NOT contain any properties. Its name is reserved for future use.
    """


    class Config:
        extra = "allow"


class SolaceChannelBinding(BaseModel):
    """
    This document defines how to describe Solace-specific information with AsyncAPI.

    This object MUST NOT contain any properties. Its name is reserved for future use.
    """


    class Config:
        extra = "allow"


class SolaceOperationBinding(BaseModel):
    """
    We need the ability to support several bindings for each operation, see the
    Example section below for details.
    """

    bindingVersion: Optional[str] = None
    """
    The current version is 0.1.0
    """

    destinations: Optional[List[SolaceDestination]] = None
    """
    Destination Objects.
    """


    class Config:
        extra = "allow"


class SolaceServerBinding(BaseModel):
    """
    This document defines how to describe Solace-specific information with AsyncAPI.
    """

    bindingVersion: Optional[str] = None
    """
    The current version is 0.1.0
    """

    msgVpn: Optional[str] = None
    """
    The Virtual Private Network name on the Solace broker.
    """


    class Config:
        extra = "allow"
