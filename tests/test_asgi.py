import pytest
from flask import Flask
from pydantic import BaseModel, Field

from sio_asyncapi import (
    AsyncAPIAsyncServer,
    AsyncAPISocketIO,
    EmitValidationError,
    RequestValidationError,
)
from sio_asyncapi.http import (
    ASYNCAPI_REACT_COMPONENT_VERSION,
    DOC_PATHS,
    docs_body_and_type,
)


class EchoIn(BaseModel):
    text: str = Field(..., json_schema_extra={"example": "hello"})


class EchoOut(BaseModel):
    text: str


@pytest.mark.asyncio
async def test_async_server_validates_and_returns_dict_ack():
    sio = AsyncAPIAsyncServer(validate=True, generate_docs=True, serve_docs=False)

    @sio.on("echo", get_from_typehint=True)
    async def echo(sid, request: EchoIn) -> EchoOut:
        return EchoOut(text=request.text)

    assert await echo("sid-1", {"text": "hello"}) == {"text": "hello"}
    with pytest.raises(RequestValidationError):
        await echo("sid-1", {})

    doc = sio.asyncapi_doc.dict()
    assert "receive_echo" in doc["operations"]
    assert doc["operations"]["receive_echo"]["reply"]["messages"][0]["$ref"].endswith(
        "/Echo_Ack"
    )


@pytest.mark.asyncio
async def test_async_server_emit_validation():
    sio = AsyncAPIAsyncServer(validate=True, generate_docs=False, serve_docs=False)

    class Status(BaseModel):
        ok: bool

    @sio.doc_emit("status", Status)
    async def _register():
        return None

    with pytest.raises(EmitValidationError):
        await sio.emit("status", {"nope": True})


def test_flask_serves_asyncapi_routes():
    app = Flask(__name__)
    sio = AsyncAPISocketIO(app, validate=False, generate_docs=True, title="Docs App")

    @sio.on("ping")
    def ping():
        return None

    client = app.test_client()
    json_resp = client.get("/asyncapi.json")
    assert json_resp.status_code == 200
    payload = json_resp.get_json()
    assert payload["asyncapi"] == "3.1.0"
    assert payload["info"]["title"] == "Docs App"

    yaml_resp = client.get("/asyncapi.yaml")
    assert yaml_resp.status_code == 200
    assert b"asyncapi: 3.1.0" in yaml_resp.data

    html_resp = client.get("/asyncapi")
    assert html_resp.status_code == 200
    assert b"AsyncApiStandalone" in html_resp.data
    assert ASYNCAPI_REACT_COMPONENT_VERSION.encode() in html_resp.data
    assert b"@asyncapi/react-component@2." not in html_resp.data

    agent_resp = client.get("/agent-schema.json")
    assert agent_resp.status_code == 200
    assert agent_resp.get_json()["format"] == "sio-asyncapi-agent-schema"


@pytest.mark.asyncio
async def test_asgi_docs_wrapper_serves_json():
    sio = AsyncAPIAsyncServer(validate=False, generate_docs=True, title="ASGI Docs")

    @sio.on("ping")
    async def ping(sid):
        return None

    app = sio.asgi_app()

    sent = []

    async def receive():
        return {"type": "http.request"}

    async def send(message):
        sent.append(message)

    await app({"type": "http", "path": "/asyncapi.json", "method": "GET"}, receive, send)
    assert sent[0]["status"] == 200
    body = sent[1]["body"].decode()
    assert '"asyncapi": "3.1.0"' in body or '"asyncapi":"3.1.0"' in body
    assert "ASGI Docs" in body


def test_docs_path_table_covers_common_routes():
    assert DOC_PATHS == {
        "/asyncapi": "html",
        "/asyncapi.json": "json",
        "/asyncapi.yaml": "yaml",
        "/asyncapi.yml": "yaml",
        "/agent-schema.json": "agent",
    }
    assert callable(docs_body_and_type)
