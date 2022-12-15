from flask_socketio import SocketIOTestClient

from .fixtures import client, downloader_queue

_ = client

def test_download_file(client: SocketIOTestClient):
    data ={
        "url": "https://cdn.pixabay.com/photo/2015/04/23/22/00/tree-736885__480.jpg",
        "location": "/tmp/tree.jpg",
    }
    client.emit('download_file', data)
    assert len(downloader_queue) == 1
    assert downloader_queue[0].url == "https://cdn.pixabay.com/photo/2015/04/23/22/00/tree-736885__480.jpg"
    assert downloader_queue[0].check_hash == False


def test_download_file_validation(client: SocketIOTestClient):
    data ={
        "url": "https://cdn.pixabay.com/photo/2015/04/23/22/00/tree-736885__480.jpg",
    }
    client.emit('download_file', data)
    received = client.get_received()
    err_msg = received[0]['args'][0]
    assert "1 validation error " in err_msg

