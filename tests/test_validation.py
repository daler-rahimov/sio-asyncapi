from flask_socketio import SocketIOTestClient

from .fixtures import client, downloader_queue

_ = client

def test_request_validation(client: SocketIOTestClient):
    data ={
        "url": "https://cdn.pixabay.com/photo/2015/04/23/22/00/tree-736885__480.jpg",
        "location": "/tmp/tree.jpg",
    }
    client.emit('download_file', data)
    assert len(downloader_queue) == 1
    assert downloader_queue[0].url == "https://cdn.pixabay.com/photo/2015/04/23/22/00/tree-736885__480.jpg"
    assert downloader_queue[0].check_hash == False


def test_request_validation_fail(client: SocketIOTestClient):
    data ={
        "url": "https://cdn.pixabay.com/photo/2015/04/23/22/00/tree-736885__480.jpg",
    }
    client.emit('download_file', data)
    received = client.get_received()
    err_msg = received[0]['args'][0]
    assert "1 validation error " in err_msg

def test_emit_validation(client: SocketIOTestClient):
    client.emit('get_download_list')
    received = client.get_received()
    assert len(received) == 1

def test_emit_validation_fail(client: SocketIOTestClient):
    client.emit('get_download_list_fail')
    received = client.get_received()
    err_msg = received[0]['args'][0]
    assert "1 validation error " in err_msg
