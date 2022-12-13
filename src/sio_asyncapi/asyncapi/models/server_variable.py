from typing import List, Optional

from pydantic import BaseModel, Extra


class ServerVariable(BaseModel):
    """An object representing a Server Variable for server URL template substitution."""

    enum: Optional[List[str]] = None
    """
    An enumeration of string values to be used if the substitution options are from a limited set.
    """

    default: Optional[str] = None
    """
    The default value to use for substitution, and to send, if an alternate value is not supplied.
    """

    description: Optional[str] = None
    """
    An optional description for the server variable. CommonMark syntax MAY be used for rich text
    representation.
    """

    examples: Optional[List[str]] = None
    """
    An array of examples of the server variable.
    """

    class Config:
        extra = "allow"
