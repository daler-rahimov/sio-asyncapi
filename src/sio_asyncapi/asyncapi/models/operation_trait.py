from typing import List, Optional, Union

from pydantic import BaseModel, Extra

from .operation_bindings import OperationBindings
from .external_documentation import ExternalDocumentation
from .reference import Reference
from .tag import Tag


class OperationTrait(BaseModel):
    """
    Describes a trait that MAY be applied to an Operation Object. This object MAY contain any
    property from the Operation Object, except message and traits.
    """

    operationId: Optional[str] = None
    """
    Unique string used to identify the operation. The id MUST be unique among all operations described
    in the API. The operationId value is case-sensitive. Tools and libraries MAY use the operationId to
    uniquely identify an operation, therefore, it is RECOMMENDED to follow common programming naming
    conventions.
    """

    summary: Optional[str] = None
    """
    A short summary of what the operation is about.
    """

    description: Optional[str] = None
    """
    A verbose explanation of the operation. CommonMark syntax can be used for rich text representation.
    """

    tags: Optional[List[Tag]] = None
    """
    A list of tags for API documentation control. Tags can be used for logical grouping of operations.
    """

    externalDocs: Optional[ExternalDocumentation] = None
    """
    Additional external documentation for this operation.
    """

    bindings: Optional[Union[OperationBindings, Reference]] = None
    """
    A map where the keys describe the name of the protocol and the values describe protocol-specific
    definitions for the operation.
    """


    class Config:
        extra = "allow"
        schema_extra = {
            "examples": [
                {
                   "bindings": {
                      "amqp": {
                          "ack": False
                          }
                   }
                }
            ]
        }
