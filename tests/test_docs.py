import json
import pathlib
import shutil
from subprocess import check_call

from flask import Flask
from pydantic import BaseModel

from sio_asyncapi._compat import model_dump
from sio_asyncapi.asyncapi.docs import AsyncAPIDoc
from sio_asyncapi.application import AsyncAPISocketIO

from .fixtures import socketio


def get_doc_dict():
    return model_dump(socketio.asyncapi_doc, by_alias=True, exclude_none=True)


def schema_has_type(schema: dict, expected_type: str) -> bool:
    if schema.get("type") == expected_type:
        return True
    return any(option.get("type") == expected_type for option in schema.get("anyOf", []))


def test_validate_asycnapi_doc():
    if shutil.which("asyncapi") is None:
        return

    file_name = "tmp_test_doc.yml"
    path = pathlib.Path(__file__).parent / file_name
    doc_str = socketio.asyncapi_doc.get_yaml()
    doc_str = doc_str.replace("2.5.0", "2.0.0")
    with open(path, "w") as file:
        file.write(doc_str)
    check_call(["asyncapi", "validate", file_name], cwd=pathlib.Path(__file__).parent)


def test_handler_docstring_is_used_as_message_description():
    doc = get_doc_dict()

    assert doc["components"]["messages"]["Download_File"]["description"] == (
        "\n"
        "Except request to download file from URL and save to server's file system. </br>\n"
        "Requests are **not** executed immediately, but added to queue.\n"
    )


def test_payload_schema_is_generated_from_pydantic_model():
    doc = get_doc_dict()

    assert doc["components"]["messages"]["Download_File"]["payload"] == {
        "$ref": "#/components/schemas/DownloadFileRequest",
        "deprecated": False,
    }

    schema = doc["components"]["schemas"]["DownloadFileRequest"]
    assert schema["description"] == "Request model for download file"
    assert schema["title"] == "DownloadFileRequest"
    assert schema["type"] == "object"
    assert schema["required"] == ["url", "location"]

    check_hash = schema["properties"]["check_hash"]
    assert check_hash["default"] is False
    assert check_hash["title"] == "Check Hash"
    assert schema_has_type(check_hash, "boolean")

    location = schema["properties"]["location"]
    assert location["description"] == "Destination local to file system; should be an absolute path"
    assert location["example"] == "/tmp/tree.jpg"
    assert location["format"] == "path"
    assert schema_has_type(location, "string")

    url = schema["properties"]["url"]
    assert url["description"] == "URL to download"
    assert url["example"] == "https://cdn.pixabay.com/photo/2015/04/23/22/00/tree-736885__480.jpg"
    assert url["format"] == "uri"
    assert url["title"] == "Url"
    assert schema_has_type(url, "string")


def test_ack_schema_is_generated_from_pydantic_model():
    doc = get_doc_dict()

    ack_schema = doc["components"]["messages"]["Download_File"]["x-ack"]
    defs_key = "$defs" if "$defs" in ack_schema else "definitions"

    assert ack_schema["description"] == "Response model for download file"
    assert ack_schema["title"] == "DownloadAccepted"
    assert ack_schema["type"] == "object"
    assert ack_schema["required"] == ["data"]

    nested_data = ack_schema[defs_key]["Data"]
    assert nested_data["title"] == "Data"
    assert nested_data["type"] == "object"
    assert nested_data["properties"]["is_accepted"]["default"] is True
    assert nested_data["properties"]["is_accepted"]["title"] == "Is Accepted"
    assert nested_data["properties"]["is_accepted"]["type"] == "boolean"

    data_ref = ack_schema["properties"]["data"]["$ref"]
    assert data_ref == f"#/components/schemas/DownloadAccepted/{defs_key}/Data"

    error_schema = ack_schema["properties"]["error"]
    assert error_schema["description"] == "Error message if any"
    assert error_schema["example"] == "Invalid request"
    assert error_schema["title"] == "Error"
    assert schema_has_type(error_schema, "string")

    success_schema = ack_schema["properties"]["success"]
    assert success_schema["default"] is True
    assert success_schema["description"] == "Success status"
    assert success_schema["title"] == "Success"
    assert success_schema["type"] == "boolean"


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


def test_agent_schema_exposes_compact_event_catalog():
    agent_schema = socketio.get_agent_schema()

    assert agent_schema["format"] == "sio-asyncapi-agent-schema"
    assert agent_schema["version"] == "1.0"
    assert agent_schema["info"]["title"] == "Downloader API"

    by_name = {event["name"]: event for event in agent_schema["events"]}

    download_event = by_name["download_file"]
    assert download_event["namespace"] == "/"
    assert download_event["direction"] == "client_to_server"
    assert download_event["message_component"] == "Download_File"
    assert download_event["input_schema_component"] == "DownloadFileRequest"
    assert download_event["ack_schema_component"] == "DownloadAccepted"
    assert download_event["input_schema"]["title"] == "DownloadFileRequest"
    assert download_event["ack_schema"]["title"] == "DownloadAccepted"

    current_list_event = by_name["current_list"]
    assert current_list_event["direction"] == "server_to_client"
    assert current_list_event["output_schema_component"] == "DownloaderQueueEmitModel"
    assert current_list_event["output_schema"]["title"] == "DownloaderQueueEmitModel"


def test_agent_schema_resolves_internal_schema_refs():
    agent_schema = socketio.get_agent_schema()
    by_name = {event["name"]: event for event in agent_schema["events"]}

    ack_schema = by_name["download_file"]["ack_schema"]
    assert ack_schema["properties"]["data"]["title"] == "Data"
    assert ack_schema["properties"]["data"]["x-component-ref"].endswith("/Data")


def test_agent_schema_json_matches_dict_export():
    agent_schema = socketio.get_agent_schema()
    agent_schema_json = socketio.get_agent_schema_json()

    assert json.loads(agent_schema_json) == agent_schema
