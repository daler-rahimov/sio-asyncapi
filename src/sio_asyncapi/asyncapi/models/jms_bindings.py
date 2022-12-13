from pydantic import BaseModel, Extra


class JmsChannelBinding(BaseModel):
    """
    This document defines how to describe JMS-specific information on AsyncAPI.

    This object MUST NOT contain any properties. Its name is reserved for future use.
    """


    class Config:
        extra = "allow"


class JmsMessageBinding(BaseModel):
    """
    This document defines how to describe JMS-specific information on AsyncAPI.

    This object MUST NOT contain any properties. Its name is reserved for future use.
    """


    class Config:
        extra = "allow"


class JmsOperationBinding(BaseModel):
    """
    This document defines how to describe JMS-specific information on AsyncAPI.

    This object MUST NOT contain any properties. Its name is reserved for future use.
    """


    class Config:
        extra = "allow"


class JmsServerBinding(BaseModel):
    """
    This document defines how to describe JMS-specific information on AsyncAPI.

    This object MUST NOT contain any properties. Its name is reserved for future use.
    """


    class Config:
        extra = "allow"
