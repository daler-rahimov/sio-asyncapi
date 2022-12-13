from typing import Optional, Dict

from pydantic import BaseModel, Extra


class OAuthFlow(BaseModel):
    """
    Configuration details for a supported OAuth Flow.
    """

    authorizationUrl: Optional[str] = None
    """
    The authorization URL to be used for this flow. This MUST be in the form of a URL.
    """

    tokenUrl: Optional[str] = None
    """
    The token URL to be used for this flow. This MUST be in the form of a URL.
    """

    refreshUrl: Optional[str] = None
    """
    The URL to be used for obtaining refresh tokens. This MUST be in the form of a URL.
    """

    scopes: Optional[Dict[str, str]] = None
    """
    The available scopes for the OAuth2 security scheme. A map between the scope name
    and a short description for it.
    """


    class Config:
        extra = "allow"
        schema_extra = {
            "examples": [
                            {
                              "type": "oauth2",
                              "flows": {
                                "implicit": {
                                  "authorizationUrl": "https://example.com/api/oauth/dialog",
                                  "scopes": {
                                    "write:pets": "modify pets in your account",
                                    "read:pets": "read your pets"
                                  }
                                },
                                "authorizationCode": {
                                  "authorizationUrl": "https://example.com/api/oauth/dialog",
                                  "tokenUrl": "https://example.com/api/oauth/token",
                                  "scopes": {
                                    "write:pets": "modify pets in your account",
                                    "read:pets": "read your pets"
                                  }
                                }
                              }
                            }
                        ]
                    }


class OAuthFlows(BaseModel):
    """
    Allows configuration of the supported OAuth Flows.
    """

    implicit: Optional[OAuthFlow] = None
    """
    Configuration for the OAuth Implicit flow.
    """

    password: Optional[OAuthFlow] = None
    """
    Configuration for the OAuth Resource Owner Protected Credentials flow.
    """

    clientCredentials: Optional[OAuthFlow] = None
    """
    Configuration for the OAuth Client Credentials flow.
    """

    authorizationCode: Optional[OAuthFlow] = None
    """
    Configuration for the OAuth Authorization Code flow.
    """


    class Config:
        extra = "allow"
