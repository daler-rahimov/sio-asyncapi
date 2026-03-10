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
    assert downloader_queue[0].url == "https://cdn.pixabay.com/photo/2015/04/23/22/00/tree-736885__480.jpg"
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
