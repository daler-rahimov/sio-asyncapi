from flask import Flask
from flask_socketio import SocketIOTestClient
import pytest
from pydantic import BaseModel

from sio_asyncapi import EmitValidationError, RequestValidationError, ResponseValidationError
from sio_asyncapi.application import AsyncAPISocketIO

from .fixtures import client, downloader_queue

_ = client

def test_request_validation(client: SocketIOTestClient):
    data ={
        "url": "https://cdn.pixabay.com/photo/2015/04/23/22/00/tree-736885__480.jpg",
        "location": "/tmp/tree.jpg",
    }
    client.emit('download_file', data)
    assert len(downloader_queue) == 1
    assert str(downloader_queue[0].url) == "https://cdn.pixabay.com/photo/2015/04/23/22/00/tree-736885__480.jpg"
    assert downloader_queue[0].check_hash == False


def test_request_validation_fail(client: SocketIOTestClient):
    data ={
        "url": "https://cdn.pixabay.com/photo/2015/04/23/22/00/tree-736885__480.jpg",
    }
    client.emit('download_file', data)
    received = client.get_received()
    err_msg = received[0]['args'][0]
    assert "1 validation error " in err_msg

def test_emit_validation(client: SocketIOTestClient):
    client.emit('get_download_list')
    received = client.get_received()
    assert len(received) == 1

def test_emit_validation_fail(client: SocketIOTestClient):
    client.emit('get_download_list_fail')
    received = client.get_received()
    err_msg = received[0]['args'][0]
    assert "1 validation error " in err_msg


def test_request_validation_runs_for_empty_dict_payload():
    app = Flask(__name__)
    socketio = AsyncAPISocketIO(app, validate=True, generate_docs=False)

    class EmptyDictRequest(BaseModel):
        required_field: str

    @socketio.on("empty_request", request_model=EmptyDictRequest)
    def handle_empty_request(request):
        return request

    with pytest.raises(RequestValidationError):
        handle_empty_request({})


def test_response_validation_runs_for_empty_dict_response():
    app = Flask(__name__)
    socketio = AsyncAPISocketIO(app, validate=True, generate_docs=False)

    class EmptyDictResponse(BaseModel):
        required_field: str

    @socketio.on("empty_response", response_model=EmptyDictResponse)
    def handle_empty_response():
        return {}

    with pytest.raises(ResponseValidationError):
        handle_empty_response()


def test_emit_validation_runs_when_payload_missing():
    app = Flask(__name__)
    socketio = AsyncAPISocketIO(app, validate=True, generate_docs=False)

    class EmitPayload(BaseModel):
        required_field: str

    @socketio.doc_emit("needs_payload", EmitPayload)
    def register_emit():
        return None

    with pytest.raises(EmitValidationError):
        socketio.emit("needs_payload")


def test_emit_validation_is_namespace_aware():
    app = Flask(__name__)
    socketio = AsyncAPISocketIO(app, validate=True, generate_docs=False)

    class DefaultNamespaceEmit(BaseModel):
        flag: bool

    class TestNamespaceEmit(BaseModel):
        count: int

    @socketio.doc_emit("status", DefaultNamespaceEmit)
    def register_default_emit():
        return None

    @socketio.doc_emit("status", TestNamespaceEmit, namespace="/test")
    def register_test_emit():
        return None

    with pytest.raises(EmitValidationError):
        socketio.emit("status", {"flag": True}, namespace="/test")

    with pytest.raises(EmitValidationError):
        socketio.emit("status", {"count": 1})


def test_ack_is_returned_as_dict():
    app = Flask(__name__)
    socketio = AsyncAPISocketIO(app, validate=True, generate_docs=False)

    class PingAck(BaseModel):
        ok: bool = True

    @socketio.on("ping", get_from_typehint=True)
    def ping() -> PingAck:
        return PingAck()

    result = ping()
    assert result == {"ok": True}
    assert isinstance(result, dict)


def test_event_decorator_uses_on_path_for_docs_and_validation():
    app = Flask(__name__)
    socketio = AsyncAPISocketIO(app, validate=True, generate_docs=True)

    class EchoRequest(BaseModel):
        text: str

    class EchoResponse(BaseModel):
        text: str

    @socketio.event(get_from_typehint=True)
    def echo(request: EchoRequest) -> EchoResponse:
        return EchoResponse(text=request.text)

    doc = socketio.asyncapi_doc.dict()
    assert "receive_echo" in doc["operations"]
    assert doc["components"]["messages"]["Echo"]["payload"] == {
        "$ref": "#/components/schemas/EchoRequest"
    }

    with pytest.raises(RequestValidationError):
        echo({})

    assert echo({"text": "hi"}) == {"text": "hi"}


def test_typehint_skips_self_and_sid():
    app = Flask(__name__)
    socketio = AsyncAPISocketIO(app, validate=True, generate_docs=True)

    class Payload(BaseModel):
        value: int

    class Ack(BaseModel):
        value: int

    @socketio.on("with_self", get_from_typehint=True)
    def handle_with_self(self, request: Payload) -> Ack:
        return Ack(value=request.value)

    @socketio.on("with_sid", get_from_typehint=True)
    def handle_with_sid(sid, request: Payload) -> Ack:
        return Ack(value=request.value)

    doc = socketio.asyncapi_doc.dict()
    assert doc["components"]["messages"]["With_Self"]["payload"] == {
        "$ref": "#/components/schemas/Payload"
    }
    assert doc["components"]["messages"]["With_Sid"]["payload"] == {
        "$ref": "#/components/schemas/Payload"
    }


def test_module_level_emit_is_validated():
    app = Flask(__name__)
    socketio = AsyncAPISocketIO(app, validate=True, generate_docs=False)
    caught = {}

    class StatusEmit(BaseModel):
        message: str

    @socketio.doc_emit("status", StatusEmit)
    @socketio.on("trigger")
    def trigger():
        from flask_socketio import emit as flask_emit
        flask_emit("status", {"bad": True})

    @socketio.on_error_default
    def handle_error(error):
        caught["error"] = error

    client = socketio.test_client(app)
    client.emit("trigger")
    client.disconnect()
    assert isinstance(caught.get("error"), EmitValidationError)
