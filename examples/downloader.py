import abc
import logging
import pathlib
from pathlib import Path
from typing import List, Optional

from flask import Flask
from pydantic import AnyUrl, BaseModel, Field

from sio_asyncapi import (
    AsyncAPISocketIO,
    EmitValidationError,
    RequestValidationError,
    ResponseValidationError,
)
from sio_asyncapi._compat import field_schema_extra

logger = logging.getLogger(__name__)

async_mode = None
app = Flask(__name__)
app.config["SECRET_KEY"] = "secret!"

socketio = AsyncAPISocketIO(
    app,
    async_mode=async_mode,
    validate=True,
    generate_docs=True,
    version="1.0.0",
    title="Downloader API",
    description="Server downloader API",
    server_url="http://localhost:5000",
    server_name="DOWNLOADER_BACKEND",
)


class SocketBaseResponse(BaseModel, abc.ABC):
    """Base model for all responses"""
    success: bool = Field(True, description="Success status")
    error: Optional[str] = Field(
        None,
        description="Error message if any",
        **field_schema_extra(example="Invalid request"),
    )


class SocketErrorResponse(SocketBaseResponse):
    """Error response"""
    success: bool = False
    error: str = Field(
        ...,
        description="Error message if any",
        **field_schema_extra(example="Invalid request"),
    )


class DownloadAccepted(SocketBaseResponse):
    """Response model for download file"""
    class Data(BaseModel):
        is_accepted: bool = True
    data: Data


class DownloadFileRequest(BaseModel):
    """Request model for download file"""
    url: AnyUrl = Field(
        ...,
        description="URL to download",
        **field_schema_extra(
            example="https://cdn.pixabay.com/photo/2015/04/23/22/00/tree-736885__480.jpg"
        ),
    )
    location: Path = Field(
        ...,
        description="Destination local to file system; should be an absolute path",
        **field_schema_extra(example="/tmp/tree.jpg"),
    )
    check_hash: Optional[bool] = False


class DownloaderQueueEmitModel(BaseModel):
    """Emit model for current list"""
    downloader_queue: List[AnyUrl] = Field(
        ...,
        description="List of URLs to download",
        **field_schema_extra(
            example="[https://cdn.pixabay.com/photo/2015/04/23/22/00/tree-736885__480.jpg]"
        ),
    )


downloader_queue = []


@socketio.on("download_file", get_from_typehint=True)
def download_file(request: DownloadFileRequest) -> DownloadAccepted:
    """
    Accept request to download file from URL and save to server's file system. </br>
    Requests are **not** executed immediately, but added to queue.
    """
    if pathlib.Path(request.location).exists():
        return DownloadAccepted(
            success=False,
            data=DownloadAccepted.Data(is_accepted=False),
            error="File already exists",
        )
    downloader_queue.append(request)
    return DownloadAccepted(data=DownloadAccepted.Data(is_accepted=True))


@socketio.doc_emit(
    "current_list",
    DownloaderQueueEmitModel,
    "Current list of files to download",
)
@socketio.on("get_download_list", get_from_typehint=True)
def get_download_list() -> None:
    """
    Get current list of files to download
    """
    r_data = {
        "downloader_queue": [
            "https://cdn.pixabay.com/photo/2015/04/23/22/00/tree-736885__480.jpg",
            "//cdn.pixabay.com/photo/2015/04/23/22/00/tree-736885__481.jpg",
        ]
    }
    socketio.emit("current_list", r_data)


@socketio.on_error_default
def default_error_handler(e: Exception):
    """
    Default error handler. It is called if no other error handler is defined.
    Handles RequestValidationError, ResponseValidationError, and EmitValidationError.
    """
    if isinstance(e, RequestValidationError):
        logger.error("Request validation error: %s", e)
        return {"success": False, "error": str(e)}
    if isinstance(e, ResponseValidationError):
        logger.critical("Response validation error: %s", e)
        raise e
    if isinstance(e, EmitValidationError):
        logger.critical("Emit validation error: %s", e)
        raise e
    logger.critical("Unknown error: %s", e)
    raise e


if __name__ == "__main__":
    path = pathlib.Path(__file__).parent / "downloader.yml"
    path.write_text(socketio.asyncapi_doc.get_yaml())
    print(path.read_text())
    socketio.run(app, debug=True)
