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

SIO-AsyncAPI generates [AsyncAPI](https://www.asyncapi.com/) 3.1 documentation from a Socket.IO server and validates payloads with Pydantic v2 models. Use it with Flask-SocketIO or with asyncio / ASGI via `python-socketio.AsyncServer`.

Socket.IO ACKs are modeled as AsyncAPI 3 `reply` messages. The custom `x-ack` extension is kept as an alias. Component schemas are JSON Schema 2020-12.

## Installation

```bash
pip install sio_asyncapi
```

Requires Python 3.10–3.13 and Pydantic v2.

Development with [uv](https://docs.astral.sh/uv/):

```bash
uv sync
uv run python examples/simple.py
uv run pytest tests
```

Then open http://localhost:5000/asyncapi for the HTML spec viewer.

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
    email: EmailStr = Field(..., description="User email", examples=["bob@gmail.com"])
    password: str = Field(..., description="User password", examples=["123456"])


class UserSignUpResponse(BaseModel):
    """Response model for user sign up"""
    success: bool = Field(True, description="Success status")
    error: Optional[str] = Field(
        None,
        description="Error message if any",
        examples=["Invalid request"],
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

## Serving and exporting the spec

With `generate_docs=True` (the default), the running app serves:

- `/asyncapi` — HTML (AsyncAPI React Component)
- `/asyncapi.json` / `/asyncapi.yaml` — the spec
- `/agent-schema.json` — compact event catalog for agents

Pass `serve_docs=False` to disable those routes. You can also export without starting a server:

```bash
python -m sio_asyncapi export app:socketio --out spec.yml
python -m sio_asyncapi export app:socketio --format json --out spec.json
python -m sio_asyncapi export app:socketio --agent-schema --out agent-schema.json
```

`examples/agentic_doc_example.py` writes both the AsyncAPI document and the agent catalog to disk.

Generated spec from the example above (`examples/simple.yml`):

```yaml
# examples/simple.yml

asyncapi: 3.1.0
info:
  title: Demo
  version: 1.0.0
  description: 'Demo Server

    <br/> This specification targets AsyncAPI 3.1. Socket.IO ACKs are modeled as operation
    `reply` messages, with the custom `x-ack` extension kept as an alias.

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
      User_Sign_Up_Ack:
        $ref: '#/components/messages/User_Sign_Up_Ack'
operations:
  receive_user_sign_up:
    action: receive
    channel:
      $ref: '#/channels/root'
    messages:
    - $ref: '#/channels/root/messages/User_Sign_Up'
    description: User sign up
    reply:
      channel:
        $ref: '#/channels/root'
      messages:
      - $ref: '#/channels/root/messages/User_Sign_Up_Ack'
components:
  messages:
    User_Sign_Up:
      name: user_sign_up
      description: User sign up
      payload:
        $ref: '#/components/schemas/UserSignUpRequest'
      examples:
      - name: example
        payload:
          email: bob@gmail.com
          password: '123456'
      x-ack:
        $ref: '#/components/schemas/UserSignUpResponse'
    User_Sign_Up_Ack:
      name: user_sign_up_ack
      description: Socket.IO ACK for user_sign_up
      payload:
        $ref: '#/components/schemas/UserSignUpResponse'
      examples:
      - name: example
        payload:
          error: Invalid request
  schemas:
    UserSignUpRequest:
      $schema: https://json-schema.org/draft/2020-12/schema
      description: Request model for user sign up
      properties:
        email:
          description: User email
          examples:
          - bob@gmail.com
          format: email
          title: Email
          type: string
        password:
          description: User password
          examples:
          - '123456'
          title: Password
          type: string
      required:
      - email
      - password
      title: UserSignUpRequest
      type: object
```

Rendered version of the above AsyncAPI specification:
![](https://github.com/daler-rahimov/sio-asyncapi/blob/master/doc/assets/20221219000543.png?raw=true)

## asyncio / ASGI

`AsyncAPIAsyncServer` wraps `python-socketio.AsyncServer`. Mount it in FastAPI, Starlette, or any ASGI server. The spec is served from the same docs paths when you use `asgi_app()`:

```python
from pydantic import BaseModel, Field
from sio_asyncapi import AsyncAPIAsyncServer

sio = AsyncAPIAsyncServer(validate=True, generate_docs=True)

class EchoIn(BaseModel):
    text: str = Field(..., examples=["hello"])

class EchoOut(BaseModel):
    text: str

@sio.on("echo", get_from_typehint=True)
async def echo(sid: str, request: EchoIn) -> EchoOut:
    return EchoOut(text=request.text)

app = sio.asgi_app()  # uvicorn examples.asgi_echo:app
```

See `examples/asgi_echo.py`.

## Typed Python client

`AsyncAPIClient` and `AsyncAPIAsyncClient` reuse the server's Pydantic models to validate outgoing events, ACKs, and incoming server emits:

```python
from sio_asyncapi import AsyncAPIClient

client = AsyncAPIClient.from_server(socketio, "http://localhost:5000")
client.connect()
ack = client.call("user_sign_up", {"email": "bob@gmail.com", "password": "123456"})
```

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

## 2.0 breaking changes

- Pydantic v2 only (v1 support removed).
- Python 3.10–3.13.
- ACK documentation uses AsyncAPI 3 `reply`; `x-ack` remains as an alias.
- JSON Schema 2020-12 in `components/schemas` (`examples` instead of draft-07 `example`).

See `CHANGELOG.md` for the full list.

## Acknowledgements
Most of the implementation follows research done by Dimitrios Dedoussis (https://www.asyncapi.com/blog/socketio-part2).

## Roadmap
- [x] AsyncAPI documentation and validation for `emit` messages
- [x] Flask-SocketIO `namespaces`
- [x] Authentication and security auto documentation
- [x] `connect` and `disconnect` handlers auto documentation
- [x] asyncio / ASGI backend
- [x] Serve the spec from the running app
- [x] Typed Python client from the same models
- [ ] Flask-SocketIO `rooms` metadata (runtime routing, not part of AsyncAPI)
