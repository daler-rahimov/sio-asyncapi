from typing import Optional
from enum import Enum
from pydantic import BaseModel, Field, Extra

from .schema import Schema


class HttpChannelBinding(BaseModel):
    """
    This document defines how to describe HTTP-specific information on AsyncAPI.

    This object MUST NOT contain any properties. Its name is reserved for future use.
    """


    class Config:
        extra = "allow"


class HttpMessageBinding(BaseModel):
    """
    This object contains information about the message representation in HTTP.
    """

    headers: Optional[Schema] = None
    """
    A Schema object containing the definitions for HTTP-specific headers. This
    schema MUST be of type object and have a properties key.
    """

    bindingVersion: Optional[str] = None
    """
    The version of this binding. If omitted, "latest" MUST be assumed.
    """

    class Config:
        extra = "allow"


class HttpServerBinding(BaseModel):
    """
    This document defines how to describe HTTP-specific information on AsyncAPI.

    This object MUST NOT contain any properties. Its name is reserved for future use.
    """

    class Config:
        extra = "allow"


class HttpOperationBindingType(str, Enum):
    request = 'request'
    response = 'response'


class HttpOperationBinding(BaseModel):
    """
    This document defines how to describe HTTP-specific information on AsyncAPI.
    """

    param_type: HttpOperationBindingType = Field(alias="type")
    """
    **REQUIRED**. Type of operation. Its value MUST be either request or response.
    """

    method: Optional[str] = None
    """
    When type is request, this is the HTTP method, otherwise it MUST be ignored.
    Its value MUST be one of GET, POST, PUT, PATCH, DELETE, HEAD, OPTIONS, CONNECT, and TRACE.
    """

    query: Optional[Schema] = None
    """
    A Schema object containing the definitions for each query parameter.
    This schema MUST be of type object and have a properties key.
    """

    bindingVersion: Optional[str] = None
    """
    The version of this binding. If omitted, "latest" MUST be assumed.
    """

    class Config:
        extra = "allow"
        schema_extra = {
            "examples": [
                {
                   "type": "request",
                   "method": "GET",
                   "query": {
                      "type": "object",
                      "required": ["companyId"],
                      "properties": {
                          "companyId": {
                              "type": "number",
                              "minimum": 1,
                              "description": "The Id of the company."
                          }
                      },
                      "additionalProperties": False
                   },
                  "bindingVersion": "0.1.0"
                }
            ]
        }
