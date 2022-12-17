"""
AsycnAPI [https://studio.asyncapi.com/] documentation auto generation.
"""
import json
import textwrap
from typing import Callable, Literal, Optional, Type, Union

import yaml
from loguru import logger
from pydantic import BaseModel

from sio_asyncapi.asyncapi.models.async_api_base import AsyncAPIBase
from sio_asyncapi.asyncapi.models.message import Message

from .utils import add_ref_prepath

NotProvidedType = Literal["NotProvided"]

add_description ="""
<br/> AsyncAPI currently does not support Socket.IO binding and Web Socket like syntax used for now.
In order to add support for Socket.IO ACK value, AsyncAPI is extended with with x-ack keyword.
This documentation should **NOT** be used for generating code due to these limitations.
"""

default_channels = yaml.safe_load(
"""
/:
  publish:
    message:
      oneOf:

  subscribe:
    message:
      oneOf:

  x-handlers:
    disconnect: disconnect
"""
)

default_components = yaml.safe_load(
"""
messages:

schemas:
  NoSpec:
    description: Specification is not provided
"""
)


class AsyncAPIDoc(AsyncAPIBase):
    """AsyncAPI documentation generator."""

    @classmethod
    def default_init(cls,
        version: str = "1.0.0",
        title: str = "Demo Chat API",
        description: str = "Demo Chat API",
        server_url: str = "http://localhost:5000",
        server_name: str = "BACKEND",
        server_protocol: str = "socketio",
    ) -> "AsyncAPIDoc":
        """Initialize AsyncAPI documentation generator."""
        logger.info(f"{server_url=}, {server_name=}, {server_protocol=}")
        default_channels["/"]["subscribe"]["message"]["oneOf"] = []
        default_channels["/"]["publish"]["message"]["oneOf"] = []
        default_components["messages"] = {}
        initial_spec_obj = {
            "info": {
                "title": title,
                "version": version,
                "description": description +
                add_description},
            "servers": {
                server_name: {
                    "url": server_url,
                    "protocol": server_protocol}},
            "asyncapi": "2.5.0",
            "channels": default_channels,
            "components": default_components,
        }
        return AsyncAPIDoc.parse_obj(initial_spec_obj)

    def get_yaml(self):
        """Return AsyncAPI documentation in YAML format."""
        return yaml.safe_dump(
            json.loads(
                self.json(
                    by_alias=True,
                    exclude_none=True,
                )
            )
        )

    def add_new_receiver(
            self,
            handler: Callable,
            name: str,
            message_name=None,
            ack_data_model: Optional[Union[Type[BaseModel], NotProvidedType]] = None,
            payload_model: Optional[Union[Type[BaseModel], NotProvidedType]] = None,
        ) -> None:
        # global asyncapi_doc
        if message_name is None:
            message_name = name.title()

        # TODO: make sure schema name is unique
        if ack_data_model == "NotProvided":
            ack = {"$ref": "#/components/schemas/NoSpec"}
        elif isinstance(ack_data_model, type(BaseModel)):
            ack_schema_name = ack_data_model.__name__ # type: ignore
            ack = ack_data_model.schema() # type: ignore
            add_ref_prepath(ack, f"/components/schemas/{ack_schema_name}")
            self.components.schemas[ack_schema_name] = ack # type: ignore
        else:
            ack = None

        if payload_model == "NotProvided":
            payload = {"$ref": "#/components/schemas/NoSpec"}
        elif isinstance(payload_model, type(BaseModel)):
            payload_schema_name = payload_model.__name__ # type: ignore
            payload = {"$ref": f"#/components/schemas/{payload_schema_name}"}
            payload_schema = payload_model.schema() # type: ignore
            add_ref_prepath(payload_schema, f"/components/schemas/{payload_schema_name}")
            self.components.schemas[payload_schema_name] = payload_schema # type: ignore
        else:
            payload = None

        # create new message
        new_message = {
            "name": name,
            "description": handler.__doc__ if  handler.__doc__ else "",
            "x-ack": None,
        }

        # remove multiple spaces so yaml dump does not try to escape them
        if new_message["description"]:
            # add single indent at the beginning if not present
            if not new_message["description"].startswith(" "):
                new_message["description"] = " " + new_message["description"]
            new_message["description"] = textwrap.dedent(new_message["description"])

        new_message["x-ack"] = ack
        new_message["payload"] = payload

        # add message to spec
        if self.components and self.components.messages is not None:
            self.components.messages[message_name] = Message.parse_obj(new_message)

        # add to sub
        one_of = {"$ref": f"#/components/messages/{message_name}"}
        if self.channels and self.channels["/"] and self.channels["/"].publish and self.channels["/"].publish.message:
            self.channels["/"].publish.message.__dict__["oneOf"].append(one_of)


# def add_new_sender(handler: Callable,
#                 name: str,
#                 message_name = None,
#                 payload_model: Optional[Type[BaseModel]] = None) -> None:
#     global asyncapi_doc
#     if message_name is None:
#         message_name = name.title()

#     # TODO: make sure schema name is unique
#     if payload_model is not None:
#         payload_schema_name = payload_model.__name__
#         payload = {"payload": {"$ref": f"#/components/schemas/{payload_schema_name}"}}
#         asyncapi_doc["components"]["schemas"][payload_schema_name] = payload_model.schema()

#     # create new message
#     new_message = {
#         "name": name,
#         "description": handler.__doc__,
#     }

#     if payload_model is not None:
#         new_message["payload"] = payload

#     # add message to spec
#     asyncapi_doc["components"]["messages"][message_name] = new_message

#     # add to sub
#     one_of = {"$ref": f"#/components/messages/{message_name}"}
#     asyncapi_doc["channels"]["/"]["subscribe"]["message"]["oneOf"].append(one_of)


# def get_json_str_doc() -> str:
#     global asyncapi_doc
#     return json.dumps(asyncapi_doc)

# def get_yaml_str_doc() -> str:
#     global asyncapi_doc
#     return yaml.safe_dump(asyncapi_doc)
