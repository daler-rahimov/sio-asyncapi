import pathlib
import shutil
from subprocess import check_call

from flask import Flask
from pydantic import BaseModel

from sio_asyncapi.asyncapi.docs import AsyncAPIDoc
from sio_asyncapi.application import AsyncAPISocketIO

from .fixtures import socketio


def test_validate_asycnapi_doc():
    if shutil.which("asyncapi") is None:
        return

    FILE_NAME = "tmp_test_doc.yml"
    path = pathlib.Path(__file__).parent / FILE_NAME
    doc_str = socketio.asyncapi_doc.get_yaml()
    # replace version to 2.0.0 since asyncapi-cli doesn't support 2.5.0 yet
    doc_str = doc_str.replace("2.5.0", "2.0.0")
    with open(path, "w") as f:
        f.write(doc_str)
    # run and check external process asyncapi-cli examples/downloader.yml
    check_call(["asyncapi", "validate", FILE_NAME], cwd=pathlib.Path(__file__).parent)


def test_default_init_does_not_share_mutable_state():
    first_doc = AsyncAPIDoc.default_init(title="First")
    second_doc = AsyncAPIDoc.default_init(title="Second")

    first_doc.add_new_sender("first_event")

    assert first_doc.components.messages == {"first_event": first_doc.components.messages["first_event"]}
    assert second_doc.components.messages == {}
    assert first_doc.channels["/"].subscribe.message.__dict__["oneOf"] == [
        {"$ref": "#/components/messages/first_event"}
    ]
    assert second_doc.channels["/"].subscribe.message.__dict__["oneOf"] == []


def test_docs_are_namespace_aware_for_same_event_name():
    app = Flask(__name__)
    sio = AsyncAPISocketIO(app, validate=False, generate_docs=True)

    class StatusEmit(BaseModel):
        message: str

    @sio.on("ping")
    def ping_default():
        return None

    @sio.on("ping", namespace="/test")
    def ping_test():
        return None

    @sio.doc_emit("status", StatusEmit)
    def status_default():
        return None

    @sio.doc_emit("status", StatusEmit, namespace="/test")
    def status_test():
        return None

    assert "/" in sio.asyncapi_doc.channels
    assert "/test" in sio.asyncapi_doc.channels
    assert sio.asyncapi_doc.channels["/"].publish.message.__dict__["oneOf"] == [
        {"$ref": "#/components/messages/Ping"}
    ]
    assert sio.asyncapi_doc.channels["/test"].publish.message.__dict__["oneOf"] == [
        {"$ref": "#/components/messages/Test_Ping"}
    ]
    assert sio.asyncapi_doc.channels["/"].subscribe.message.__dict__["oneOf"] == [
        {"$ref": "#/components/messages/status"}
    ]
    assert sio.asyncapi_doc.channels["/test"].subscribe.message.__dict__["oneOf"] == [
        {"$ref": "#/components/messages/Test_status"}
    ]

# TODO:
# - [ ] check docstring used as description in AsyncAPI spec
# - [ ] check payload schema generated from pydantic models correctly
# - [ ] check x-ack schema generated from pydantic models correctly
