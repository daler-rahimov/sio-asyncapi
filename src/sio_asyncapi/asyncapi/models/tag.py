from typing import Optional

from pydantic import BaseModel, Extra

from .external_documentation import ExternalDocumentation


class Tag(BaseModel):
    """Allows adding meta data to a single tag."""

    name: str = ...
    """
    **REQUIRED**. The name of the tag.
    """

    description: Optional[str] = None
    """
    A short description for the tag. CommonMark syntax can be used for
    rich text representation.
    """

    externalDocs: Optional[ExternalDocumentation] = None
    """
    Additional external documentation.
    """


    class Config:
        extra = "allow"
