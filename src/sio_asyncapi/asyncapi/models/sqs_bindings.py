from pydantic import BaseModel, Extra


class SqsChannelBinding(BaseModel):
    """
    This document defines how to describe SQS-specific information on AsyncAPI.

    This object MUST NOT contain any properties. Its name is reserved for future use.
    """


    class Config:
        extra = "allow"


class SqsMessageBinding(BaseModel):
    """
    This document defines how to describe SQS-specific information on AsyncAPI.

    This object MUST NOT contain any properties. Its name is reserved for future use.
    """


    class Config:
        extra = "allow"


class SqsOperationBinding(BaseModel):
    """
    This document defines how to describe SQS-specific information on AsyncAPI.

    This object MUST NOT contain any properties. Its name is reserved for future use.
    """


    class Config:
        extra = "allow"


class SqsServerBinding(BaseModel):
    """
    This document defines how to describe SQS-specific information on AsyncAPI.

    This object MUST NOT contain any properties. Its name is reserved for future use.
    """


    class Config:
        extra = "allow"
