import json
import pathlib
from typing import Optional

from flask import Flask
from pydantic import BaseModel, Field

from sio_asyncapi import AsyncAPISocketIO, RequestValidationError, ResponseValidationError

app = Flask(__name__)

socketio = AsyncAPISocketIO(
    app,
    validate=True,
    generate_docs=True,
    version="1.0.0",
    title="Agent Export Demo",
    description="Demo server that exports both AsyncAPI and agent-friendly schemas.",
    server_url="http://localhost:5000",
    server_name="AGENT_EXPORT_DEMO",
)


class AskAssistantRequest(BaseModel):
    """Request model for sending a user prompt to the assistant."""
    prompt: str = Field(..., description="Natural-language prompt from the user")
    conversation_id: Optional[str] = Field(
        None,
        description="Conversation identifier for multi-turn chats",
        example="chat-123",
    )


class AskAssistantResponse(BaseModel):
    """Ack model returned immediately after a prompt is accepted."""
    accepted: bool = Field(True, description="Whether the prompt was accepted")
    request_id: str = Field(..., description="Server-generated request identifier")


class AssistantReply(BaseModel):
    """Server push event containing the assistant's generated reply."""
    request_id: str = Field(..., description="Identifier of the related request")
    message: str = Field(..., description="Generated reply text")


@socketio.doc_emit(
    "assistant_reply",
    AssistantReply,
    "Server push event sent when the assistant has produced a reply.",
)
@socketio.on("ask_assistant", get_from_typehint=True)
def ask_assistant(request: AskAssistantRequest) -> AskAssistantResponse:
    """Accept a user prompt and start asynchronous assistant processing."""
    _ = request
    return AskAssistantResponse(accepted=True, request_id="req-001")


@socketio.on_error_default
def default_error_handler(error: Exception):
    if isinstance(error, RequestValidationError):
        return {"accepted": False, "error": str(error)}
    if isinstance(error, ResponseValidationError):
        raise error
    raise error


if __name__ == "__main__":
    base_path = pathlib.Path(__file__).parent

    asyncapi_path = base_path / "agentic_doc_asyncapi.yml"
    asyncapi_path.write_text(socketio.asyncapi_doc.get_yaml())

    agent_schema_path = base_path / "agentic_doc_schema.json"
    agent_schema_path.write_text(socketio.get_agent_schema_json())

    print(f"Wrote AsyncAPI spec to {asyncapi_path}")
    print(f"Wrote agent schema to {agent_schema_path}")
    print(json.dumps(socketio.get_agent_schema(), indent=2))
