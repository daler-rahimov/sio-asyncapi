import logging
from typing import Optional

from flask import Flask
from pydantic import BaseModel, EmailStr, Field

from sio_asyncapi import AsyncAPISocketIO, RequestValidationError, ResponseValidationError

logger = logging.getLogger(__name__)

app = Flask(__name__)

socketio = AsyncAPISocketIO(
    app,
    validate=True,
    generate_docs=True,
    version="1.0.0",
    title="Demo",
    description="Demo Server",
    server_url="http://localhost:5000",
    server_name="DEMO_SIO",
)


class UserSignUpRequest(BaseModel):
    """Request model for user sign up"""
    email: EmailStr = Field(..., description="User email", examples=["bob@gmail.com"])
    password: str = Field(..., description="User password", examples=["123456"])


class UserSignUpResponse(BaseModel):
    """Response model for user sign up"""
    success: bool = Field(True, description="Success status")
    error: Optional[str] = Field(
        None,
        description="Error message if any",
        examples=["Invalid request"],
    )


@socketio.on("user_sign_up", get_from_typehint=True)
def user_sign_up(request: UserSignUpRequest) -> UserSignUpResponse:
    """User sign up"""
    _ = request
    return UserSignUpResponse(success=True, error=None)


@socketio.on_error_default
def default_error_handler(e: Exception):
    """
    Default error handler. It is called if no other error handler is defined.
    Handles RequestValidationError and ResponseValidationError.
    """
    if isinstance(e, RequestValidationError):
        logger.error("Request validation error: %s", e)
        return {"success": False, "error": str(e)}
    if isinstance(e, ResponseValidationError):
        logger.critical("Response validation error: %s", e)
        raise e
    logger.critical("Unknown error: %s", e)
    raise e


if __name__ == "__main__":
    socketio.run(app, debug=True)
