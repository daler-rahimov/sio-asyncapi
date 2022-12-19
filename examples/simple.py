from flask import Flask
from sio_asyncapi import AsyncAPISocketIO, ResponseValidationError, RequestValidationError
from pydantic import BaseModel, Field, EmailStr
from typing import Optional
import logging
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
    email: EmailStr = Field(..., description="User email", example="bob@gmail.com")
    password: str = Field(..., description="User password", example="123456")


class UserSignUpResponse(BaseModel):
    """Response model for user sign up"""
    success: bool = Field(True, description="Success status")
    error: Optional[str] = Field( None, description="Error message if any",
        example="Invalid request")


@socketio.on("user_sign_up", get_from_typehint=True)
def user_sign_up(request: UserSignUpRequest) -> UserSignUpResponse:
    """User sign up"""
    _ = request
    return UserSignUpResponse(success=True, error=None)

@socketio.on_error_default
def default_error_handler(e: Exception):
    """
    Default error handler. It called if no other error handler defined.
    Handles RequestValidationError and ResponseValidationError errors.
    """
    if isinstance(e, RequestValidationError):
        logger.error(f"Request validation error: {e}")
        return UserSignUpResponse(error=str(e), success=False).json()
    elif isinstance(e, ResponseValidationError):
        logger.critical(f"Response validation error: {e}")
        raise e
    else:
        logger.critical(f"Unknown error: {e}")
        raise e

if __name__ == '__main__':
    socketio.run(app, debug=True)

# import pathlib
# if __name__ == "__main__":
#     path = pathlib.Path(__file__).parent / "simple.yml"
#     doc_str = socketio.asyncapi_doc.get_yaml()
#     with open(path, "w") as f:
#         f.write(doc_str)
#     print(doc_str)
