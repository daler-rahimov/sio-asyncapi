"""Shared HTTP helpers for serving AsyncAPI docs from a running app."""
from __future__ import annotations

import json
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from sio_asyncapi.contract import AsyncAPIContract

DOC_PATHS = {
    "/asyncapi": "html",
    "/asyncapi.json": "json",
    "/asyncapi.yaml": "yaml",
    "/asyncapi.yml": "yaml",
    "/agent-schema.json": "agent",
}


def html_page(contract: "AsyncAPIContract") -> str:
    """Return a standalone HTML page that renders the AsyncAPI document."""
    spec_json = json.dumps(contract.asyncapi_doc.dict())
    title = contract.asyncapi_doc.info.get("title", "AsyncAPI")
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1"/>
  <title>{title} — AsyncAPI</title>
  <link rel="stylesheet" href="https://unpkg.com/@asyncapi/react-component@2.6.3/styles/default.min.css">
</head>
<body>
  <div id="asyncapi"></div>
  <script src="https://unpkg.com/@asyncapi/react-component@2.6.3/browser/standalone/index.js"></script>
  <script>
    AsyncApiStandalone.render({{
      schema: {spec_json},
      config: {{ show: {{ sidebar: true }} }}
    }}, document.getElementById('asyncapi'));
  </script>
</body>
</html>
"""


def docs_body_and_type(contract: "AsyncAPIContract", kind: str) -> tuple[bytes, str]:
    """Return (body, content-type) for a docs route kind."""
    if kind == "json":
        return contract.asyncapi_doc.json(indent=2).encode("utf-8"), "application/json"
    if kind == "yaml":
        return contract.asyncapi_doc.get_yaml().encode("utf-8"), "text/yaml; charset=utf-8"
    if kind == "agent":
        return contract.get_agent_schema_json().encode("utf-8"), "application/json"
    return html_page(contract).encode("utf-8"), "text/html; charset=utf-8"


def register_flask_docs(app: Any, contract: "AsyncAPIContract") -> None:
    """Register Flask routes that serve the AsyncAPI document."""
    from flask import Response

    def _response(kind: str) -> Response:
        body, content_type = docs_body_and_type(contract, kind)
        return Response(body, mimetype=content_type)

    endpoint_prefix = f"sio_asyncapi_docs_{id(contract)}"
    app.add_url_rule(
        "/asyncapi",
        endpoint=f"{endpoint_prefix}_html",
        view_func=lambda: _response("html"),
        methods=["GET"],
    )
    app.add_url_rule(
        "/asyncapi.json",
        endpoint=f"{endpoint_prefix}_json",
        view_func=lambda: _response("json"),
        methods=["GET"],
    )
    app.add_url_rule(
        "/asyncapi.yaml",
        endpoint=f"{endpoint_prefix}_yaml",
        view_func=lambda: _response("yaml"),
        methods=["GET"],
    )
    app.add_url_rule(
        "/asyncapi.yml",
        endpoint=f"{endpoint_prefix}_yml",
        view_func=lambda: _response("yaml"),
        methods=["GET"],
    )
    app.add_url_rule(
        "/agent-schema.json",
        endpoint=f"{endpoint_prefix}_agent",
        view_func=lambda: _response("agent"),
        methods=["GET"],
    )


class DocsASGIApp:
    """ASGI wrapper that serves docs routes and delegates everything else."""

    def __init__(self, contract: "AsyncAPIContract", inner: Any) -> None:
        self.contract = contract
        self.inner = inner

    async def __call__(self, scope: dict, receive: Any, send: Any) -> None:
        if scope.get("type") == "http":
            path = scope.get("path", "")
            kind = DOC_PATHS.get(path)
            if kind is not None:
                await self._send_docs(kind, send)
                return
        await self.inner(scope, receive, send)

    async def _send_docs(self, kind: str, send: Any) -> None:
        body, content_type = docs_body_and_type(self.contract, kind)
        await send({
            "type": "http.response.start",
            "status": 200,
            "headers": [
                (b"content-type", content_type.encode("ascii")),
                (b"content-length", str(len(body)).encode("ascii")),
            ],
        })
        await send({"type": "http.response.body", "body": body})
