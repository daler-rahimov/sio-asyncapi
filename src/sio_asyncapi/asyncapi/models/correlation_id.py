from typing import Optional

from pydantic import BaseModel, Extra


class CorrelationId(BaseModel):
    """
    An object that specifies an identifier at design time that can used for message tracing
    and correlation. For specifying and computing the location of a Correlation ID, a runtime
    expression is used.

    This object can be extended with Specification Extensions.
    """

    description: Optional[str] = None
    """
    An optional description of the identifier. CommonMark syntax can be used for rich text
    representation.
    """

    location: str = ...
    """
    **REQUIRED**. A runtime expression that specifies the location of the correlation ID.
    """


    class Config:
        extra = "allow"
        schema_extra = {
            "examples": [
                            {
                                "description": "Default Correlation ID",
                                "location": "$message.header#/correlationId",
                            }
                        ]
            }
