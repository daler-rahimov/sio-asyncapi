# Changelog

## 2.0.0

Breaking major version: Pydantic v2 only, asyncio/ASGI backend, and AsyncAPI 3 `reply` for Socket.IO ACKs.

### Breaking

- Require Python 3.10–3.13 and Pydantic v2. Pydantic v1 is no longer supported.
- Socket.IO ACKs are modeled as AsyncAPI 3 operation `reply` messages. The previous `x-ack` field remains as a compatibility alias on the request message.
- Component schemas are JSON Schema 2020-12 (`$schema` plus `examples` instead of draft-07 `example`).
- Removed the unused AsyncAPI 2.x Pydantic model tree under `sio_asyncapi.asyncapi.models`.

### Added

- `AsyncAPIAsyncServer` for `python-socketio.AsyncServer` / ASGI apps, with the same validation and docs contract as Flask.
- Spec served from the running app at `/asyncapi`, `/asyncapi.json`, `/asyncapi.yaml`, and `/agent-schema.json`.
- Typed `AsyncAPIClient` and `AsyncAPIAsyncClient` built from the same server models.
- CLI: `python -m sio_asyncapi export app:socketio --out spec.yml`.
- Message `examples` in the generated spec, derived from Pydantic field examples.

### Changed

- Flask and asyncio servers share documentation and validation through `AsyncAPIContract`.
- ACK payloads continue to be returned as JSON-compatible dicts, not JSON strings.
- The `/asyncapi` HTML viewer uses `@asyncapi/react-component` 3.1.x so AsyncAPI 3.1 documents render.
- Packaging uses uv (`uv.lock`, PEP 621) instead of Poetry.
