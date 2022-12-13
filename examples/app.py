import abc

from loguru import logger

from threading import Lock
from flask import Flask, render_template, session, request, \
    copy_current_request_context
from flask_socketio import SocketIO, emit, join_room, leave_room, \
    close_room, rooms, disconnect

from sio_asyncapi import AsyncAPISocketIO, ResponseValidationError, RequestValidationError

# Set this variable to "threading", "eventlet" or "gevent" to test the
# different async modes, or leave it set to None for the application to choose
# the best option based on installed packages.
async_mode = None


DOC_TEMPLATE_YML = """
info:
  title: Demo Chat API
  version: 1.0.0
  description: |
    This is Socket.IO API for Chat application.
    <br/> AsyncAPI currently does not support Socket.IO binding and Web Socket like syntax used for now.
    In order to add support for Socket.IO ACK value, AsyncAPI is extended with with x-ack keyword.
    This documentation should **NOT** be used for generating code due to these limitations.

servers:
  GUI:
    url: http://localhost:5000
    protocol: socketio
"""

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = AsyncAPISocketIO(
    app,
    async_mode=async_mode,
    logger=logger,
    validation=True,
    generate_doc=True,
    doc_template=DOC_TEMPLATE_YML,
)
# socketio = SocketIO(app, async_mode=async_mode)
thread = None
thread_lock = Lock()

from engineio.payload import Payload
Payload.max_decode_packets = 16

def background_thread():
    """Example of how to send server generated events to clients."""
    count = 0
    while True:
        socketio.sleep(10)
        count += 1
        socketio.emit('my_response',
                      {'data': 'Server generated event', 'count': count})


@app.route('/')
def index():
    return render_template('index.html', async_mode=socketio.async_mode)


# @socketio.event
# def my_event(message):
#     session['receive_count'] = session.get('receive_count', 0) + 1
#     emit('my_response',
#          {'data': message['data'], 'count': session['receive_count']})


# @socketio.event
# def my_broadcast_event(message):
#     session['receive_count'] = session.get('receive_count', 0) + 1
#     emit('my_response',
#          {'data': message['data'], 'count': session['receive_count']},
#          broadcast=True)

from pydantic import BaseModel, Field, AnyUrl
from pydantic import BaseModel, Field, AnyUrl
from typing import Optional
from pathlib import Path

class AnyModel(BaseModel):
    pass

class SocketSuccess(BaseModel, abc.ABC):
    """Base model for all responses"""
    success: bool = Field(True, const=True)

class SocketError(BaseModel, abc.ABC):
    """Base model for all errors"""
    success: bool = Field(False, const=True)
    error: str = Field(..., description="Error message", example="Invalid request")

class SocketErrorResponse(SocketError):
    error: str = Field(..., description="Error message", example="Invalid request")

class AnySuccessModel(SocketSuccess):
    pass

class CloseRoomResponse(SocketSuccess):
    class Data(BaseModel):
        room: str = Field(...,
            description="Room to close",
            example="room1")
    data: Data

class DownloadFileRequest(BaseModel):
    url: AnyUrl = Field(...,
        description="URL to download",
        example="https://cdn.pixabay.com/photo/2015/04/23/22/00/tree-736885__480.jpg")
    location: Path = Field(...,
        description="Destination local to file system; should be an absolute path",
        example="/tmp/tree.jpg")
    is_advertisement: Optional[bool] = Field(False,
        description="Use when requesting an ad to be downloaded")
    ad_source: Optional[str] = Field(None,
        description="use when downloading ads, should be \"vistar\" or \"grocery_tv\" for reporting purposes",
        example = "grocery_tv")

    check_hash: Optional[bool] = False

class DownloadeAccepted(SocketSuccess):
    class Data(BaseModel):
        is_accepted: bool = True
    data: Data

@socketio.event
def error(data):
    raise RuntimeError()

@socketio.on_error_default(model=SocketError)
def default_error_handler(e):
    if isinstance(e, RequestValidationError):
        logger.error(f"Request validation error: {e}")
        return SocketErrorResponse(error=str(e)).json()
    elif isinstance(e, ResponseValidationError):
        logger.critical(f"Response validation error: {e}")
        raise e
    else:
        logger.critical(f"Unknown error: {e}")
        raise e

@socketio.on('test', get_from_typehint=True)
def test(message: DownloadFileRequest) -> DownloadeAccepted:
    return DownloadeAccepted(data=DownloadeAccepted.Data(is_accepted=True))

# @socketio.event(request_model=AnyModel, response_model=AnyModel)
# def join(message):
#     join_room(message['room'])
#     session['receive_count'] = session.get('receive_count', 0) + 1
#     emit('my_response',
#          {'data': 'In rooms: ' + ', '.join(rooms()),
#           'count': session['receive_count']})

# @socketio.event(get_from_typehint=True)
# def download_file(message: DownloadFileRequest) -> AnyModel:
#     return AnyModel(**{"data": "test"})

# @socketio.event
# def leave(message):
#     leave_room(message['room'])
#     session['receive_count'] = session.get('receive_count', 0) + 1
#     emit('my_response',
#          {'data': 'In rooms: ' + ', '.join(rooms()),
#           'count': session['receive_count']})


# @socketio.on('close_room')
# def on_close_room(message):
#     session['receive_count'] = session.get('receive_count', 0) + 1
#     emit('my_response', {'data': 'Room ' + message['room'] + ' is closing.',
#                          'count': session['receive_count']},
#          to=message['room'])
#     close_room(message['room'])


# @socketio.event
# def my_room_event(message):
#     session['receive_count'] = session.get('receive_count', 0) + 1
#     emit('my_response',
#          {'data': message['data'], 'count': session['receive_count']},
#          to=message['room'])


# @socketio.event
# def disconnect_request():
#     @copy_current_request_context
#     def can_disconnect():
#         disconnect()

#     session['receive_count'] = session.get('receive_count', 0) + 1
#     # for this emit we use a callback function
#     # when the callback function is invoked we know that the message has been
#     # received and it is safe to disconnect
#     emit('my_response',
#          {'data': 'Disconnected!', 'count': session['receive_count']},
#          callback=can_disconnect)


# # @socketio.event
# # def my_ping():
# #     emit('my_pong')


# @socketio.event
# def connect():
#     global thread
#     # with thread_lock:
#     #     if thread is None:
#     #         thread = socketio.start_background_task(background_thread)
#     emit('my_response', {'data': 'Connected', 'count': 0})


# @socketio.on('disconnect')
# def test_disconnect():
#     print('Client disconnected', request.sid)


# if __name__ == '__main__':
#     socketio.run(app, debug=True)


"""
Generate and save AsycnAPI [https://studio.asyncapi.com/] specification in ./asyncapi_2.5.0.yml
Usage: python asycnapi_save_doc
"""
import pathlib

FILE_NAME = "asyncapi_2.5.0.yml"

if __name__ == "__main__":
    path = pathlib.Path(__file__).parent / FILE_NAME
    doc_str = socketio.asyncapi_doc.get_yaml()
    with open(path, "w") as f:
        # doc_str = spec.get_json_str_doc()
        f.write(doc_str)
    print(doc_str)
