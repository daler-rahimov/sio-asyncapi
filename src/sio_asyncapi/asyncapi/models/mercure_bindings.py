from pydantic import BaseModel, Extra


class MercureChannelBinding(BaseModel):
    """
    This document defines how to describe Mercure-specific information on AsyncAPI.

    This object MUST NOT contain any properties. Its name is reserved for future use.
    """


    class Config:
        extra = "allow"


class MercureMessageBinding(BaseModel):
    """
    This document defines how to describe Mercure-specific information on AsyncAPI.

    This object MUST NOT contain any properties. Its name is reserved for future use.
    """


    class Config:
        extra = "allow"


class MercureOperationBinding(BaseModel):
    """
    This document defines how to describe Mercure-specific information on AsyncAPI.

    This object MUST NOT contain any properties. Its name is reserved for future use.
    """


    class Config:
        extra = "allow"


class MercureServerBinding(BaseModel):
    """
    This document defines how to describe Mercure-specific information on AsyncAPI.

    This object MUST NOT contain any properties. Its name is reserved for future use.
    """


    class Config:
        extra = "allow"
