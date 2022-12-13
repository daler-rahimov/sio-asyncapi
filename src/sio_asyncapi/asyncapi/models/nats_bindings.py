from typing import Optional

from pydantic import BaseModel, Extra


class NatsChannelBinding(BaseModel):
    """
    This document defines how to describe NATS-specific information on AsyncAPI.

    This object MUST NOT contain any properties. Its name is reserved for future use.
    """


    class Config:
        extra = "allow"


class NatsMessageBinding(BaseModel):
    """
    This document defines how to describe NATS-specific information on AsyncAPI.

    This object MUST NOT contain any properties. Its name is reserved for future use.
    """


    class Config:
        extra = "allow"


class NatsOperationBinding(BaseModel):
    """
    This document defines how to describe NATS-specific information on AsyncAPI.
    """

    queue: Optional[str] = None
    """
    Defines the name of the queue to use. It MUST NOT exceed 255 characters.
    """

    bindingVersion: Optional[str] = None
    """
    The version of this binding. If omitted, "latest" MUST be assumed.
    """


    class Config:
        extra = "allow"


class NatsServerBinding(BaseModel):
    """
    This document defines how to describe NATS-specific information on AsyncAPI.

    This object MUST NOT contain any properties. Its name is reserved for future use.
    """


    class Config:
        extra = "allow"
