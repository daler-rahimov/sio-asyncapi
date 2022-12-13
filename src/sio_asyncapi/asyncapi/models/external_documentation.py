from typing import Optional

from pydantic import BaseModel, Extra, AnyUrl


class ExternalDocumentation(BaseModel):
    """
    Allows referencing an external resource for extended documentation.
    """

    description: Optional[str] = None
    """
    A short description of the target documentation. CommonMark syntax can be
    used for rich text representation.
    """

    url: AnyUrl = ...
    """
    Required. The URL for the target documentation. Value MUST be in the format
    of a URL.
    """


    class Config:
        extra = "allow"
        schema_extra = {
            "examples": [
                {
                    "description": "Find more info here",
                    "url": "https://example.com"
                }
            ]
        }
