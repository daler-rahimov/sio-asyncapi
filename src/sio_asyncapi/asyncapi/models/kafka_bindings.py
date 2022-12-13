from typing import Optional
from enum import Enum
from pydantic import BaseModel, Extra

from .schema import Schema


class KafkaChannelBinding(BaseModel):
    """
    This document defines how to describe Kafka-specific information on AsyncAPI.

    This object MUST NOT contain any properties. Its name is reserved for future use.
    """


    class Config:
        extra = "allow"


class KafkaMessageBinding(BaseModel):
    """
    This object contains information about the message representation in Kafka.
    """

    key: Optional[Schema] = None
    """
    The message key. NOTE: You can also use the reference object way.
    """

    bindingVersion: Optional[str] = None
    """
    The version of this binding. If omitted, "latest" MUST be assumed.
    """


    class Config:
        extra = "allow"


class KafkaServerBinding(BaseModel):
    """
    This document defines how to describe Kafka-specific information on AsyncAPI.

    This object MUST NOT contain any properties. Its name is reserved for future use.
    """

    class Config:
        extra = "allow"


class KafkaOperationBinding(BaseModel):
    """
    This document defines how to describe Kafka-specific information on AsyncAPI.
    """

    groupId: Optional[Schema] = None
    """
    Id of the consumer group.
    """

    clientId: Optional[Schema] = None
    """
    Id of the consumer inside a consumer group.
    """

    bindingVersion: Optional[str] = None
    """
    The version of this binding. If omitted, "latest" MUST be assumed.
    """

    class Config:
        extra = "allow"

