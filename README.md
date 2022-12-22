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


## Installation

```bash
pip install sio_asyncapi
```

## Basic Example

```py
# examples/simple.py

from flask import Flask
from sio_asyncapi import AsyncAPISocketIO, ResponseValidationError, RequestValidationError
from pydantic import BaseModel, Field, EmailStr
from typing import Optional
import logging
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
    error: Optional[str] = Field( None, description="Error message if any",
        example="Invalid request")


@socketio.on("user_sign_up", get_from_typehint=True)
def user_sign_up(request: UserSignUpRequest) -> UserSignUpResponse:
    """User sign up"""
    _ = request
    return UserSignUpResponse(success=True, error=None)

@socketio.on_error_default
def default_error_handler(e: Exception):
    """
    Default error handler. It called if no other error handler defined.
    Handles RequestValidationError and ResponseValidationError errors.
    """
    if isinstance(e, RequestValidationError):
        logger.error(f"Request validation error: {e}")
        return UserSignUpResponse(error=str(e), success=False).json()
    elif isinstance(e, ResponseValidationError):
        logger.critical(f"Response validation error: {e}")
        raise e
    else:
        logger.critical(f"Unknown error: {e}")
        raise e

if __name__ == '__main__':
    socketio.run(app, debug=True)

# import pathlib
# if __name__ == "__main__":
#     path = pathlib.Path(__file__).parent / "simple.yml"
#     doc_str = socketio.asyncapi_doc.get_yaml()
#     with open(path, "w") as f:
#         f.write(doc_str)
#     print(doc_str)

```

Here is how validation error looks like in FireCamp:
![](https://github.com/daler-rahimov/sio-asyncapi/blob/master/doc/assets/20221219000309.png?raw=true)

In order to get the AsyncAPI specification from your SocketIO server instead of running the server, you can do the following:
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

asyncapi: 2.5.0
channels:
  /:
    publish:
      message:
        oneOf:
        - $ref: '#/components/messages/User_Sign_Up'
    subscribe:
      message:
        oneOf: []
    x-handlers:
      disconnect: disconnect
components:
  messages:
    User_Sign_Up:
      description: User sign up
      name: user_sign_up
      payload:
        $ref: '#/components/schemas/UserSignUpRequest'
        deprecated: false
      x-ack:
        description: Response model for user sign up
        properties:
          error:
            description: Error message if any
            example: Invalid request
            title: Error
            type: string
          success:
            default: true
            description: Success status
            title: Success
            type: boolean
        title: UserSignUpResponse
        type: object
  schemas:
    NoSpec:
      deprecated: false
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
        error:
          description: Error message if any
          example: Invalid request
          title: Error
          type: string
        success:
          default: true
          description: Success status
          title: Success
          type: boolean
      title: UserSignUpResponse
      type: object
info:
  description: 'Demo Server

    <br/> AsyncAPI currently does not support Socket.IO binding and Web Socket like
    syntax used for now.

    In order to add support for Socket.IO ACK value, AsyncAPI is extended with with
    x-ack keyword.

    This documentation should **NOT** be used for generating code due to these limitations.

    '
  title: Demo
  version: 1.0.0
servers:
  DEMO_SIO:
    protocol: socketio
    url: http://localhost:5000

```

Rendered version of the above AsyncAPI specification:
![](https://github.com/daler-rahimov/sio-asyncapi/blob/master/doc/assets/20221219000543.png?raw=true)

## Converting from Flask-SocketIO to SIO-AsyncAPI
SIO-AsyncAPI is built on top of Flask-SocketIO and all unit tests of Flask-SocketIO are tested against SIO-AsyncAPI. If you converting your SocketIO server from Flask-SocketIO to SIO-AsyncAPI, you can be sure that your SocketIO server will work as expected. When converting your SocketIO server from Flask-SocketIO to SIO-AsyncAPI, it's as simple as changing the import statement:

```python
# instead of `from flask_socketio import SocketIO`
from sio_asyncapi import AsyncAPISocketIO as SocketIO
...
# There are additional arguments that you can pass to the constructor of AsyncAPISocketIO
socketio = SocketIO(app)
...
```

## Missing Features
SIO-AsyncAPI is still in its early stages and there are some features that are not yet implemented. If you are interested in contributing to SIO-AsyncAPI any contribution is welcome. Here is the list of missing features:

- [ ] Support of AsycnAPI documentation and validation for `emit` messages
- [ ] Support of Flask-SocketIO `namespaces` and `rooms`
- [ ] Authentication and security auto documentation
- [ ] `connect` and `disconnect` handlers auto documentation
