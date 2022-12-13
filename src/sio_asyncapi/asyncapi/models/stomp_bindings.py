from pydantic import BaseModel, Extra


class StompChannelBinding(BaseModel):
    """
    This document defines how to describe STOMP-specific information on AsyncAPI.

    This object MUST NOT contain any properties. Its name is reserved for future use.
    """


    class Config:
        extra = "allow"


class StompMessageBinding(BaseModel):
    """
    This document defines how to describe STOMP-specific information on AsyncAPI.

    This object MUST NOT contain any properties. Its name is reserved for future use.
    """


    class Config:
        extra = "allow"


class StompOperationBinding(BaseModel):
    """
    This document defines how to describe STOMP-specific information on AsyncAPI.

    This object MUST NOT contain any properties. Its name is reserved for future use.
    """


    class Config:
        extra = "allow"


class StompServerBinding(BaseModel):
    """
    This document defines how to describe STOMP-specific information on AsyncAPI.

    This object MUST NOT contain any properties. Its name is reserved for future use.
    """


    class Config:
        extra = "allow"
