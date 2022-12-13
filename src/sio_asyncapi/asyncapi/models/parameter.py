from typing import Optional, Union

from pydantic import BaseModel, Extra, Field, constr

from .reference import Reference
from .schema import Schema


ParameterName = constr(regex=r"^[A-Za-z0-9_\-]+$")


class Parameter(BaseModel):
    """Describes a parameter included in a channel name."""

    description: Optional[str] = None
    """
    A verbose explanation of the parameter. CommonMark syntax can be used for rich
    text representation.
    """

    param_schema: Optional[Union[Schema, Reference]] = Field(default=None, alias="schema")
    """
    Definition of the parameter.
    """

    location: Optional[str] = None
    """
    A runtime expression that specifies the location of the parameter value. Even
    when a definition for the target field exists, it MUST NOT be used to validate
    this parameter but, instead, the schema property MUST be used.
    """


    class Config:
        extra = "allow"
        schema_extra = {
            "examples": [
                            {
                                "user/{userId}/signup": {
                                    "parameters": {
                                        "userId": {
                                            "description": "Id of the user.",
                                            "schema": {
                                                "type": "string"
                                                },
                                            "location": "$message.payload#/user/id"
                                            }
                                        },
                                    "subscribe": {
                                        "message": {
                                            "$ref": "#/components/messages/userSignedUp"
                                            }
                                        }
                                    }
                                }
                        ]
        }
