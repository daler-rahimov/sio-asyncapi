from typing import Optional

from pydantic import AnyUrl, BaseModel, Extra

from .contact import Contact
from .license import License


class Info(BaseModel):
    """
    The object provides metadata about the API. The metadata can be used by the clients if needed.
    """

    title: str = ...
    """
    **REQUIRED**. The title of the application.
    """

    version: str = ...
    """
    **REQUIRED**. Provides the version of the application API (not to be confused with the specification
    version).
    """

    description: Optional[str] = None
    """
    A short description of the application. CommonMark syntax can be used for rich text representation.
    """

    termsOfService: Optional[AnyUrl] = None
    """
    A URL to the Terms of Service for the API. MUST be in the format of a URL.
    """

    contact: Optional[Contact] = None
    """
    The contact information for the exposed API.
    """

    license: Optional[License] = None
    """
    The license information for the exposed API.
    """

    class Config:
        extra = "allow"
        schema_extra = {
            "examples": [
                {
                   "title": "AsyncAPI Sample App",
                   "description": "This is a sample server.",
                   "termsOfService": "https://asyncapi.org/terms/",
                   "contact": {
                      "name": "API Support",
                      "url": "https://www.asyncapi.org/support",
                      "email": "support@asyncapi.org"
                   },
                  "license": {
                      "name": "Apache 2.0",
                      "url": "https://www.apache.org/licenses/LICENSE-2.0.html"
                  },
                  "version": "1.0.1"
                }
            ]
        }
