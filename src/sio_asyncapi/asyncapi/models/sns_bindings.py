from pydantic import BaseModel, Extra


class SnsChannelBinding(BaseModel):
    """
    This document defines how to describe SNS-specific information on AsyncAPI.

    This object MUST NOT contain any properties. Its name is reserved for future use.
    """


    class Config:
        extra = "allow"


class SnsMessageBinding(BaseModel):
    """
    This document defines how to describe SNS-specific information on AsyncAPI.

    This object MUST NOT contain any properties. Its name is reserved for future use.
    """


    class Config:
        extra = "allow"


class SnsOperationBinding(BaseModel):
    """
    This document defines how to describe SNS-specific information on AsyncAPI.

    This object MUST NOT contain any properties. Its name is reserved for future use.
    """


    class Config:
        extra = "allow"


class SnsServerBinding(BaseModel):
    """
    This document defines how to describe SNS-specific information on AsyncAPI.

    This object MUST NOT contain any properties. Its name is reserved for future use.
    """


    class Config:
        extra = "allow"
