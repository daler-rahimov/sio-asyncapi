"""
Generate and save AsycnAPI [https://studio.asyncapi.com/] specification in ./asyncapi_2.5.0.yml
Usage: python asycnapi_save_doc
"""
from .app import app
from sio_asyncapi.asycnapi import spec
import pathlib

FILE_NAME = "asyncapi_2.5.0.yml"

if __name__ == "__main__":
    path = pathlib.Path(__file__).parent / FILE_NAME
    doc_str = spec.get_yaml_str_doc()
    with open(path, "w") as f:
        # doc_str = spec.get_json_str_doc()
        f.write(doc_str)
    print(doc_str)
