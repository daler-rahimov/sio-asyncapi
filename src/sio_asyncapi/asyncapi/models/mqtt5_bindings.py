from pydantic import BaseModel, Extra


class Mqtt5ChannelBinding(BaseModel):
    """
    This document defines how to describe MQTT 5-specific information on AsyncAPI.

    This object MUST NOT contain any properties. Its name is reserved for future use.
    """


    class Config:
        extra = "allow"


class Mqtt5MessageBinding(BaseModel):
    """
    This document defines how to describe MQTT 5-specific information on AsyncAPI.

    This object MUST NOT contain any properties. Its name is reserved for future use.
    """


    class Config:
        extra = "allow"


class Mqtt5OperationBinding(BaseModel):
    """
    This document defines how to describe MQTT 5-specific information on AsyncAPI.

    This object MUST NOT contain any properties. Its name is reserved for future use.
    """


    class Config:
        extra = "allow"


class Mqtt5ServerBinding(BaseModel):
    """
    This document defines how to describe MQTT 5-specific information on AsyncAPI.

    This object MUST NOT contain any properties. Its name is reserved for future use.
    """


    class Config:
        extra = "allow"
