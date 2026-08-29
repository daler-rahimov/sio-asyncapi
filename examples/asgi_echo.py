"""Minimal asyncio / ASGI Socket.IO server with AsyncAPI docs.

Run with any ASGI server, for example::

    uvicorn examples.asgi_echo:app --reload

The spec is served from the running app at ``/asyncapi``, ``/asyncapi.json``,
and ``/asyncapi.yaml``. Export it without starting a server::

    python -m sio_asyncapi export examples.asgi_echo:sio --out spec.yml
"""
from pydantic import BaseModel, Field

from sio_asyncapi import AsyncAPIAsyncServer

sio = AsyncAPIAsyncServer(
    async_mode="asgi",
    validate=True,
    generate_docs=True,
    version="1.0.0",
    title="ASGI Echo API",
    description="Minimal asyncio Socket.IO server",
    server_url="http://localhost:8000",
    server_name="ASGI_ECHO",
)


class EchoIn(BaseModel):
    text: str = Field(..., description="Text to echo", examples=["hello"])


class EchoOut(BaseModel):
    text: str = Field(..., description="Echoed text", examples=["hello"])


@sio.on("echo", get_from_typehint=True)
async def echo(sid: str, request: EchoIn) -> EchoOut:
    """Echo the payload back as a Socket.IO ACK."""
    return EchoOut(text=request.text)


app = sio.asgi_app()
