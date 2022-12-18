import pathlib
from subprocess import check_call

from .fixtures import socketio


def test_validate_asycnapi_doc():
    FILE_NAME = "tmp_test_doc.yml"
    path = pathlib.Path(__file__).parent / FILE_NAME
    doc_str = socketio.asyncapi_doc.get_yaml()
    # replace version to 2.0.0 since asyncapi-cli doesn't support 2.5.0 yet
    doc_str = doc_str.replace("2.5.0", "2.0.0")
    with open(path, "w") as f:
        f.write(doc_str)
    # run and check external process asyncapi-cli examples/downloader.yml
    check_call(["asyncapi", "validate", FILE_NAME], cwd=pathlib.Path(__file__).parent)

# TODO:
# - [ ] check docstring used as description in AsyncAPI spec
# - [ ] check payload schema generated from pydantic models correctly
# - [ ] check x-ack schema generated from pydantic models correctly
