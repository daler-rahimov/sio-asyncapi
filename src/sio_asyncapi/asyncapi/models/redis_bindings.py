from pydantic import BaseModel, Extra


class RedisChannelBinding(BaseModel):
    """
    This document defines how to describe Redis-specific information on AsyncAPI.

    This object MUST NOT contain any properties. Its name is reserved for future use.
    """


    class Config:
        extra = "allow"


class RedisMessageBinding(BaseModel):
    """
    This document defines how to describe Redis-specific information on AsyncAPI.

    This object MUST NOT contain any properties. Its name is reserved for future use.
    """


    class Config:
        extra = "allow"


class RedisOperationBinding(BaseModel):
    """
    This document defines how to describe Redis-specific information on AsyncAPI.

    This object MUST NOT contain any properties. Its name is reserved for future use.
    """


    class Config:
        extra = "allow"


class RedisServerBinding(BaseModel):
    """
    This document defines how to describe Redis-specific information on AsyncAPI.

    This object MUST NOT contain any properties. Its name is reserved for future use.
    """


    class Config:
        extra = "allow"
