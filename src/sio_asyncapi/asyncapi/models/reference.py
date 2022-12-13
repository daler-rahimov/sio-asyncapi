from pydantic import BaseModel, Extra, Field


class Reference(BaseModel):
    """
    A simple object to allow referencing other components in the specification,
    internally and externally.

    The Reference Object is defined by JSON Reference and follows the same structure,
    behavior and rules. A JSON Reference SHALL only be used to refer to a schema that
    is formatted in either JSON or YAML. In the case of a YAML-formatted Schema, the
    JSON Reference SHALL be applied to the JSON representation of that schema. The
    JSON representation SHALL be made by applying the conversion described here.

    For this specification, reference resolution is done as defined by the JSON
    Reference specification and not by the JSON Schema specification.

    This object cannot be extended with additional properties and any properties added
    SHALL be ignored.
    """

    ref: str = Field(alias="$ref")
    """
    Required. The reference string.
    """


    class Config:
        extra = "allow"
