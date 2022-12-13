from pydantic import BaseModel, Extra


class Amqp1ChannelBinding(BaseModel):
    """
    This document defines how to describe AMQP 1.0-specific information on AsyncAPI.

    This object MUST NOT contain any properties. Its name is reserved for future use.
    """

    class Config:
        extra = "allow"


class Amqp1MessageBinding(BaseModel):
    """
    This document defines how to describe AMQP 1.0-specific information on AsyncAPI.

    This object MUST NOT contain any properties. Its name is reserved for future use.
    """

    class Config:
        extra = "allow"


class Amqp1OperationBinding(BaseModel):
    """
    This document defines how to describe AMQP 1.0-specific information on AsyncAPI.

    This object MUST NOT contain any properties. Its name is reserved for future use.
    """

    class Config:
        extra = "allow"


class Amqp1ServerBinding(BaseModel):
    """
    This document defines how to describe AMQP 1.0-specific information on AsyncAPI.

    This object MUST NOT contain any properties. Its name is reserved for future use.
    """

    class Config:
        extra = "allow"

