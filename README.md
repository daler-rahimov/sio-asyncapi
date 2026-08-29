SIO-AsyncAPI
============

[![PyPI Version][pypi-image]][pypi-url]
[![Build Status][build-image]][build-url]
[![Code Coverage][coverage-image]][coverage-url]
[![][versions-image]][versions-url]

<!-- Badges: -->

[pypi-image]: https://img.shields.io/pypi/v/sio_asyncapi
[pypi-url]: https://pypi.org/project/sio_asyncapi/
[build-image]: https://github.com/daler-rahimov/sio-asyncapi/actions/workflows/python-package.yml/badge.svg
[build-url]: https://github.com/daler-rahimov/sio-asyncapi/actions/workflows/python-package.yml
[coverage-image]: https://codecov.io/gh/daler-rahimov/sio-asyncapi/branch/develop/graph/badge.svg
[coverage-url]: https://app.codecov.io/gh/daler-rahimov/sio-asyncapi
[versions-image]: https://img.shields.io/pypi/pyversions/sio_asyncapi/
[versions-url]: https://pypi.org/project/sio_asyncapi/


SIO-AsyncAPI is a Python library built on the top of [Flask-SocketIO](https://flask-socketio.readthedocs.io/) and driven by [AsyncAPI](https://www.asyncapi.com/). It allows you to generate an AsyncAPI specification from your SocketIO server and validate messages against it.

Similar to FastAPI, SIO-AsyncAPI allows you to define your SocketIO server using Python type annotations and Pydantic models. It also provides a way to generate an AsyncAPI specification from your SocketIO server.

SIO-AsyncAPI now supports both Pydantic 1.10+ and 2.x, emits AsyncAPI 3.1, and keeps Socket.IO ACKs in the custom `x-ack` extension.

## Installation

```bash
pip install sio_asyncapi
```

## Basic Example

```py
# examples/simple.py

import logging
from typing import Optional

from flask import Flask
from pydantic import BaseModel, EmailStr, Field

from sio_asyncapi import AsyncAPISocketIO, RequestValidationError, ResponseValidationError

logger = logging.getLogger(__name__)

app = Flask(__name__)

socketio = AsyncAPISocketIO(
    app,
    validate=True,
    generate_docs=True,
    version="1.0.0",
    title="Demo",
    description="Demo Server",
    server_url="http://localhost:5000",
    server_name="DEMO_SIO",
)


class UserSignUpRequest(BaseModel):
    """Request model for user sign up"""
    email: EmailStr = Field(..., description="User email", example="bob@gmail.com")
    password: str = Field(..., description="User password", example="123456")


class UserSignUpResponse(BaseModel):
    """Response model for user sign up"""
    success: bool = Field(True, description="Success status")
    error: Optional[str] = Field(
        None,
        description="Error message if any",
        example="Invalid request",
    )


@socketio.on("user_sign_up", get_from_typehint=True)
def user_sign_up(request: UserSignUpRequest) -> UserSignUpResponse:
    """User sign up"""
    _ = request
    return UserSignUpResponse(success=True, error=None)


@socketio.on_error_default
def default_error_handler(e: Exception):
    """
    Default error handler. It is called if no other error handler is defined.
    Handles RequestValidationError and ResponseValidationError.
    """
    if isinstance(e, RequestValidationError):
        logger.error("Request validation error: %s", e)
        return {"success": False, "error": str(e)}
    if isinstance(e, ResponseValidationError):
        logger.critical("Response validation error: %s", e)
        raise e
    logger.critical("Unknown error: %s", e)
    raise e


if __name__ == "__main__":
    socketio.run(app, debug=True)
```

Here is how validation error looks like in FireCamp:
![](https://github.com/daler-rahimov/sio-asyncapi/blob/master/doc/assets/20221219000309.png?raw=true)

In order to get the AsyncAPI specification from your SocketIO server instead of running the server, you can do the following:
You can also get a compact agent-friendly event catalog with `socketio.get_agent_schema()` or `socketio.get_agent_schema_json()`.
See `examples/agentic_doc_example.py` for a complete example that writes both exports to disk.
```python
import pathlib
if __name__ == "__main__":
    path = pathlib.Path(__file__).parent / "simple.yml"
    doc_str = socketio.asyncapi_doc.get_yaml()
    with open(path, "w") as f:
        f.write(doc_str)
    print(doc_str)

```
Example of the AsyncAPI specification generated from the above example:
```yaml
# examples/simple.yml

asyncapi: 3.1.0
info:
  title: Demo
  version: 1.0.0
  description: 'Demo Server

    <br/> This specification targets AsyncAPI 3.1 and keeps Socket.IO ACK values in
    the custom `x-ack` message extension.

    Socket.IO-specific transport details may still require application-level interpretation.

    '
servers:
  DEMO_SIO:
    host: localhost:5000
    protocol: socketio
channels:
  root:
    address: /
    messages:
      User_Sign_Up:
        $ref: '#/components/messages/User_Sign_Up'
operations:
  receive_user_sign_up:
    action: receive
    channel:
      $ref: '#/channels/root'
    messages:
    - $ref: '#/channels/root/messages/User_Sign_Up'
    description: User sign up
components:
  messages:
    User_Sign_Up:
      name: user_sign_up
      description: User sign up
      payload:
        $ref: '#/components/schemas/UserSignUpRequest'
      x-ack:
        $ref: '#/components/schemas/UserSignUpResponse'
  schemas:
    NoSpec:
      description: Specification is not provided
    UserSignUpRequest:
      description: Request model for user sign up
      properties:
        email:
          description: User email
          example: bob@gmail.com
          format: email
          title: Email
          type: string
        password:
          description: User password
          example: '123456'
          title: Password
          type: string
      required:
      - email
      - password
      title: UserSignUpRequest
      type: object
    UserSignUpResponse:
      description: Response model for user sign up
      properties:
        success:
          default: true
          description: Success status
          title: Success
          type: boolean
        error:
          anyOf:
          - type: string
          - type: 'null'
          default: null
          description: Error message if any
          example: Invalid request
          title: Error
      title: UserSignUpResponse
      type: object
```

Rendered version of the above AsyncAPI specification:
![](https://github.com/daler-rahimov/sio-asyncapi/blob/master/doc/assets/20221219000543.png?raw=true)

## Converting from Flask-SocketIO to SIO-AsyncAPI
SIO-AsyncAPI is built on top of Flask-SocketIO and all unit tests of Flask-SocketIO are tested against SIO-AsyncAPI. If you converting your SocketIO server from Flask-SocketIO to SIO-AsyncAPI, you can be sure that your SocketIO server will work as expected. When converting your SocketIO server from Flask-SocketIO to SIO-AsyncAPI, it's as simple as changing the import statement:

```python
# instead of `from flask_socketio import SocketIO`
from sio_asyncapi import AsyncAPISocketIO as SocketIO
from sio_asyncapi import emit  # optional; still validates documented emit events
...
# There are additional arguments that you can pass to the constructor of AsyncAPISocketIO
socketio = SocketIO(app)
...
```

`flask_socketio.emit` looks up this Socket.IO instance from the Flask extension map, so emit validation still applies. Prefer `from sio_asyncapi import emit` so the import path matches the validated API.

Handshake auth can be documented with `auth_model=` (and optionally `security_scheme=`) on `AsyncAPISocketIO`, or by decorating `@socketio.on("connect", get_from_typehint=True)`.

## Acknowledgements
Most of the implementation follows research done by Dimitrios Dedoussis (https://www.asyncapi.com/blog/socketio-part2).

## Roadmap
- [x] AsyncAPI documentation and validation for `emit` messages
- [x] Flask-SocketIO `namespaces`
- [x] Authentication and security auto documentation
- [x] `connect` and `disconnect` handlers auto documentation
- [ ] Flask-SocketIO `rooms` metadata (runtime routing, not part of AsyncAPI)
