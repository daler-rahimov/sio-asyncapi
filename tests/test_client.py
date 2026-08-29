import pytest
from flask import Flask
from pydantic import BaseModel, Field

from sio_asyncapi import (
    AsyncAPIAsyncClient,
    AsyncAPIClient,
    AsyncAPISocketIO,
    EmitValidationError,
    RequestValidationError,
    ResponseValidationError,
)


class AskRequest(BaseModel):
    prompt: str = Field(..., json_schema_extra={"example": "hi"})


class AskAck(BaseModel):
    accepted: bool = True


class Reply(BaseModel):
    message: str


def _server():
    app = Flask(__name__)
    sio = AsyncAPISocketIO(app, validate=True, generate_docs=True, serve_docs=False)

    @sio.doc_emit("assistant_reply", Reply)
    @sio.on("ask_assistant", get_from_typehint=True)
    def ask_assistant(request: AskRequest) -> AskAck:
        return AskAck(accepted=True)

    return sio


def test_client_from_server_validates_outgoing_payload():
    sio = _server()
    client = AsyncAPIClient.from_server(sio, "http://localhost:5000")

    with pytest.raises(RequestValidationError):
        client.prepare_emit("ask_assistant", {})

    data = client.prepare_emit("ask_assistant", AskRequest(prompt="hi"))
    assert data == {"prompt": "hi"}

    ack = client.prepare_ack("ask_assistant", {"accepted": True})
    assert ack == {"accepted": True}

    with pytest.raises(ResponseValidationError):
        client.prepare_ack("ask_assistant", {"accepted": "nope"})


def test_client_validates_incoming_server_emits():
    sio = _server()
    client = AsyncAPIClient.from_server(sio, "http://localhost:5000")
    incoming = client.prepare_incoming("assistant_reply", {"message": "done"})
    assert incoming.message == "done"
    with pytest.raises(EmitValidationError):
        client.prepare_incoming("assistant_reply", {})


def test_async_client_from_server_shares_models():
    sio = _server()
    client = AsyncAPIAsyncClient.from_server(sio, "http://localhost:5000")
    assert ("ask_assistant", "/") in client.receive_models
    assert ("assistant_reply", "/") in client.emit_models
