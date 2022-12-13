from typing import Dict, List


SecurityRequirement = Dict[str, List[str]]
"""
Lists the required security schemes to execute this operation. The name used for each property MUST correspond
to a security scheme declared in the Security Schemes under the Components Object.

When a list of Security Requirement Objects is defined on a Server object, only one of the Security Requirement
Objects in the list needs to be satisfied to authorize the connection.
"""

"""Patterned Fields"""

# {name}: List[str]
"""
Each name MUST correspond to a security scheme which is declared in the Security Schemes under the Components Object.
If the security scheme is of type "oauth2" or "openIdConnect", then the value is a list of scope names. Provide
scopes that are required to establish successful connection with the server. If scopes are not needed, the list
can be empty. For other security scheme types, the array MUST be empty.
"""
