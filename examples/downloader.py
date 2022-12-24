import abc
import pathlib
from pathlib import Path
from typing import Optional, List

from flask import Flask
from loguru import logger
from pydantic import AnyUrl, BaseModel, Field

from sio_asyncapi import (AsyncAPISocketIO, EmitValidationError,
                          RequestValidationError, ResponseValidationError)

async_mode = None
app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'

# socketio = SocketIO(app, async_mode=async_mode)
socketio = AsyncAPISocketIO(
    app,
    async_mode=async_mode,
    logger=logger,
    validate=True,
    generate_docs=True,
    version="1.0.0",
    title="Downloader API",
    description="Server downloader API",
    server_url="http://localhost:5000",
    server_name="DOWNLOADER_BACKEND",
)

# Pydantic models
class SocketBaseResponse(BaseModel, abc.ABC):
    """Base model for all responses"""
    success: bool = Field(True, description="Success status")
    error: Optional[str] = Field(
        None,
        description="Error message if any",
        example="Invalid request")


class SocketErrorResponse(SocketBaseResponse):
    """Error response"""
    success: bool = False
    error: str = Field(..., description="Error message if any", example="Invalid request")


class DownloadAccepted(SocketBaseResponse):
    """Response model for download file"""
    class Data(BaseModel):
        is_accepted: bool = True
    data: Data


class DownloadFileRequest(BaseModel):
    """Request model for download file"""
    url: AnyUrl = Field(..., description="URL to download",
                        example="https://cdn.pixabay.com/photo/2015/04/23/22/00/tree-736885__480.jpg")
    location: Path = Field(...,
                           description="Destination local to file system; should be an absolute path",
                           example="/tmp/tree.jpg")
    check_hash: Optional[bool] = False

class DownloaderQueueEmitModel(BaseModel):
    """Emit model for current list"""
    downloader_queue: List[AnyUrl] = Field(..., description="List of URLs to download",
                        example="[https://cdn.pixabay.com/photo/2015/04/23/22/00/tree-736885__480.jpg]")

downloader_queue = []

# Handlers
@socketio.on('download_file', get_from_typehint=True)
def download_file(request: DownloadFileRequest) -> DownloadAccepted:
    """
    Except request to download file from URL and save to server's file system. </br>
    Requests are **not** executed immediately, but added to queue.
    """
    # check if file exists
    request = DownloadFileRequest.parse_obj(request)
    if pathlib.Path(request.location).exists():
        return DownloadAccepted(
            success=False,
            data=DownloadAccepted.Data(
                is_accepted=False),
            error="File already exists")
    else:
        # add to queue
        downloader_queue.append(request)
        return DownloadAccepted(data=DownloadAccepted.Data(is_accepted=True))


@socketio.doc_emit('current_list', DownloaderQueueEmitModel,
                   "Current list of files to download")
@socketio.on('get_download_list', get_from_typehint=True)
def get_download_list() -> None:
    """
    Get current list of files to download
    """
    r_data = {"downloader_queue": [
        "https://cdn.pixabay.com/photo/2015/04/23/22/00/tree-736885__480.jpg",
        "//cdn.pixabay.com/photo/2015/04/23/22/00/tree-736885__481.jpg", ]}
    socketio.emit('current_list', r_data)


@socketio.on_error_default
def default_error_handler(e: Exception):
    """
    Default error handler. It called if no other error handler defined.
    Handles RequestValidationError and ResponseValidationError errors.
    """
    if isinstance(e, RequestValidationError):
        logger.error(f"Request validation error: {e}")
        return SocketErrorResponse(error=str(e)).json()
    elif isinstance(e, ResponseValidationError):
        logger.critical(f"Response validation error: {e}")
        raise e
    if isinstance(e, EmitValidationError):
        logger.critical(f"Emit validation error: {e}")
        raise e
    else:
        logger.critical(f"Unknown error: {e}")
        raise e


if __name__ == '__main__':
    socketio.run(app, debug=True)


# Generate and save AsycnAPI [https://studio.asyncapi.com/] specification in ./asyncapi_2.5.0.yml
# Usage: python asycnapi_save_doc
FILE_NAME = "downloader.yml"

if __name__ == "__main__":
    path = pathlib.Path(__file__).parent / FILE_NAME
    doc_str = socketio.asyncapi_doc.get_yaml()
    with open(path, "w") as f:
        # doc_str = spec.get_json_str_doc()
        f.write(doc_str)
    print(doc_str)
