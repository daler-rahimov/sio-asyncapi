"""
AsycnAPI [https://studio.asyncapi.com/] documentation auto generation.
"""
import json
import textwrap
from typing import Callable, Optional, Type
import yaml
import copy
from pydantic import BaseModel

asyncapi_doc: dict = {}

INIT_DOC_TEMPLATE_YML = """
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

REST_DOC_TEMPLATE_YML="""
asyncapi: "2.5.0"
channels:
  /:
    publish:
      message:
        oneOf:

    subscribe:
      message:
        oneOf:

    x-handlers:
      disconnect: disconnect

components:
  messages:

  schemas:
    NoSpec:
      description: Specification is not provided
"""

ACK =\
{
    "data": {
        "$ref": "#/components/schemas/NoSpec"
    },
    "success":{
        "type": "boolean",
    },
    "errors":{
        "type": "[array, 'null']",
        "items":{
            "type": "string"
        }
    }
}


def load_spec_template(doc_template: Optional[str]) -> None:
    if doc_template is None:
        doc_template = INIT_DOC_TEMPLATE_YML
    global asyncapi_doc
    spec = yaml.safe_load(doc_template)
    rest_doc = yaml.safe_load(REST_DOC_TEMPLATE_YML)
    spec = {**spec, **rest_doc}
    spec["components"]["messages"] = {}
    spec["channels"]["/"]["subscribe"]["message"]["oneOf"] = []
    spec["channels"]["/"]["publish"]["message"]["oneOf"] = []
    asyncapi_doc = spec


def add_new_receiver(
        handler: Callable,
        name: str,
        message_name=None,
        ack_data_model: Optional[Type[BaseModel]] = None,
        payload_model: Optional[Type[BaseModel]] = None,
        use_std_serialize: bool = True
    ) -> None:
    global asyncapi_doc
    if message_name is None:
        message_name = name.title()

    # TODO: make sure schema name is unique
    if ack_data_model is not None:
        ack_schema_name = ack_data_model.__name__
        ack = copy.deepcopy(ACK)
        ack["data"]["$ref"] = f"#/components/schemas/{ack_schema_name}"
        asyncapi_doc["components"]["schemas"][ack_schema_name] = ack_data_model.schema()

    if payload_model is not None:
        payload_schema_name = payload_model.__name__
        payload = {"$ref": f"#/components/schemas/{payload_schema_name}"}
        asyncapi_doc["components"]["schemas"][payload_schema_name] = payload_model.schema()

    # create new message
    new_message = {
        "name": name,
        "description": handler.__doc__ if  handler.__doc__ else "",
    }

    # remove multiple spaces so yaml dump does not try to escape them
    if new_message["description"]:
        # add single indent at the beginning if not present
        if not new_message["description"].startswith(" "):
            new_message["description"] = " " + new_message["description"]
        new_message["description"] = textwrap.dedent(new_message["description"])

    if ack_data_model is not None:
        new_message["x-ack"] = ack
    elif use_std_serialize:
        new_message["x-ack"] = ACK
    if payload_model is not None:
        new_message["payload"] = payload

    # add message to spec
    asyncapi_doc["components"]["messages"][message_name] = new_message

    # add to sub
    one_of = {"$ref": f"#/components/messages/{message_name}"}
    asyncapi_doc["channels"]["/"]["publish"]["message"]["oneOf"].append(one_of)


def add_new_sender(handler: Callable,
                name: str,
                message_name = None,
                payload_model: Optional[Type[BaseModel]] = None) -> None:
    global asyncapi_doc
    if message_name is None:
        message_name = name.title()

    # TODO: make sure schema name is unique
    if payload_model is not None:
        payload_schema_name = payload_model.__name__
        payload = {"payload": {"$ref": f"#/components/schemas/{payload_schema_name}"}}
        asyncapi_doc["components"]["schemas"][payload_schema_name] = payload_model.schema()

    # create new message
    new_message = {
        "name": name,
        "description": handler.__doc__,
    }

    if payload_model is not None:
        new_message["payload"] = payload

    # add message to spec
    asyncapi_doc["components"]["messages"][message_name] = new_message

    # add to sub
    one_of = {"$ref": f"#/components/messages/{message_name}"}
    asyncapi_doc["channels"]["/"]["subscribe"]["message"]["oneOf"].append(one_of)


def get_json_str_doc() -> str:
    global asyncapi_doc
    return json.dumps(asyncapi_doc)

def get_yaml_str_doc() -> str:
    global asyncapi_doc
    return yaml.safe_dump(asyncapi_doc)
