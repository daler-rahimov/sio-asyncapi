"""
AsycnAPI [https://studio.asyncapi.com/] documentation auto generation.
"""
import copy
import json
import textwrap
from typing import Callable, Literal, Optional, Type, Union

import yaml
from loguru import logger
from sio_asyncapi._pydantic import BaseModel

from sio_asyncapi._compat import is_pydantic_model_type, model_dump_json, model_schema, model_validate
from sio_asyncapi.asyncapi.models.async_api_base import AsyncAPIBase
from sio_asyncapi.asyncapi.models.channel import ChannelItem
from sio_asyncapi.asyncapi.models.message import Message

from .utils import add_ref_prepath

NotProvidedType = Literal["NotProvided"]

add_description ="""
<br/> AsyncAPI currently does not support Socket.IO binding and Web Socket like syntax used for now.
In order to add support for Socket.IO ACK value, AsyncAPI is extended with with x-ack keyword.
This documentation should **NOT** be used for generating code due to these limitations.
"""

DEFAULT_CHANNELS = yaml.safe_load(
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

DEFAULT_COMPONENTS = yaml.safe_load(
"""
messages:

schemas:
  NoSpec:
    description: Specification is not provided
"""
)


class AsyncAPIDoc(AsyncAPIBase):
    """AsyncAPI documentation generator."""

    @staticmethod
    def normalize_namespace(namespace: Optional[str]) -> str:
        """Normalize Socket.IO namespace values."""
        return namespace or "/"

    @staticmethod
    def message_component_name(name: str, namespace: str, *, title_case: bool) -> str:
        """Build a namespace-safe message component name."""
        base_name = name.title() if title_case else name
        if namespace == "/":
            return base_name

        namespace_prefix = "_".join(
            part.title() for part in namespace.strip("/").split("/") if part
        )
        return f"{namespace_prefix}_{base_name}"

    @staticmethod
    def channel_template() -> ChannelItem:
        """Return a fresh channel template."""
        return model_validate(
            ChannelItem,
            yaml.safe_load(
                """
publish:
  message:
    oneOf: []

subscribe:
  message:
    oneOf: []

x-handlers:
  disconnect: disconnect
"""
            ),
        )  # type: ChannelItem

    def ensure_channel(self, namespace: Optional[str]) -> str:
        """Ensure that the namespace channel exists in the document."""
        normalized_namespace = self.normalize_namespace(namespace)
        if normalized_namespace not in self.channels:
            self.channels[normalized_namespace] = self.channel_template()
        return normalized_namespace

    @classmethod
    def default_init(
        cls,
        version: str = "1.0.0",
        title: str = "Demo Chat API",
        description: str = "Demo Chat API",
        server_url: str = "http://localhost:5000",
        server_name: str = "BACKEND",
        server_protocol: str = "socketio",
    ) -> "AsyncAPIDoc":
        """Initialize AsyncAPI documentation generator."""
        logger.info(f"{server_url=}, {server_name=}, {server_protocol=}")
        default_channels = copy.deepcopy(DEFAULT_CHANNELS)
        default_channels["/"]["subscribe"]["message"]["oneOf"] = []
        default_channels["/"]["publish"]["message"]["oneOf"] = []
        default_components = copy.deepcopy(DEFAULT_COMPONENTS)
        default_components["messages"] = {}
        initial_spec_obj = {
            "info": {
                "title": title,
                "version": version,
                "description": description + add_description,
            },
            "servers": {
                server_name: {
                    "url": server_url,
                    "protocol": server_protocol,
                }
            },
            "asyncapi": "2.5.0",
            "channels": default_channels,
            "components": default_components,
        }
        return model_validate(AsyncAPIDoc, initial_spec_obj)

    def get_yaml(self):
        """Return AsyncAPI documentation in YAML format."""
        return yaml.safe_dump(
            json.loads(
                model_dump_json(
                    self,
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
        namespace: Optional[str] = None,
    ) -> None:
        channel_name = self.ensure_channel(namespace)
        if message_name is None:
            message_name = self.message_component_name(
                name,
                channel_name,
                title_case=True,
            )

        if ack_data_model == "NotProvided":
            ack = {"$ref": "#/components/schemas/NoSpec"}
        elif is_pydantic_model_type(ack_data_model):
            ack_schema_name = ack_data_model.__name__
            ack = model_schema(ack_data_model)
            add_ref_prepath(ack, f"/components/schemas/{ack_schema_name}")
            self.components.schemas[ack_schema_name] = ack
        else:
            ack = None

        if payload_model == "NotProvided":
            payload = {"$ref": "#/components/schemas/NoSpec"}
        elif is_pydantic_model_type(payload_model):
            payload_schema_name = payload_model.__name__
            payload = {"$ref": f"#/components/schemas/{payload_schema_name}"}
            payload_schema = model_schema(payload_model)
            add_ref_prepath(payload_schema, f"/components/schemas/{payload_schema_name}")
            self.components.schemas[payload_schema_name] = payload_schema
        else:
            payload = None

        new_message = {
            "name": name,
            "description": handler.__doc__ if handler.__doc__ else "",
            "x-ack": ack,
            "payload": payload,
        }

        if new_message["description"]:
            if not new_message["description"].startswith(" "):
                new_message["description"] = " " + new_message["description"]
            new_message["description"] = textwrap.dedent(new_message["description"])

        if self.components and self.components.messages is not None:
            self.components.messages[message_name] = model_validate(Message, new_message)

        one_of = {"$ref": f"#/components/messages/{message_name}"}
        if (
            self.channels
            and self.channels[channel_name]
            and self.channels[channel_name].publish
            and self.channels[channel_name].publish.message
        ):
            self.channels[channel_name].publish.message.__dict__["oneOf"].append(one_of)

    def add_new_sender(
        self,
        event: str,
        payload_model: Optional[Union[Type[BaseModel], NotProvidedType]] = None,
        description: Optional[str] = None,
        namespace: Optional[str] = None,
    ) -> None:
        """Generate new sender documentation for AsyncAPI."""
        channel_name = self.ensure_channel(namespace)
        if payload_model == "NotProvided":
            payload = {"$ref": "#/components/schemas/NoSpec"}
        elif is_pydantic_model_type(payload_model):
            payload_schema_name = payload_model.__name__
            payload_schema = model_schema(payload_model)
            payload = {"$ref": f"#/components/schemas/{payload_schema_name}"}
            add_ref_prepath(payload_schema, f"/components/schemas/{payload_schema_name}")
            self.components.schemas[payload_schema_name] = payload_schema
        else:
            payload = None

        new_message = {
            "name": event,
            "description": description if description else "",
            "payload": payload,
        }

        message_name = self.message_component_name(
            event,
            channel_name,
            title_case=False,
        )

        if new_message["description"]:
            if not new_message["description"].startswith(" "):
                new_message["description"] = " " + new_message["description"]
            new_message["description"] = textwrap.dedent(new_message["description"])

        if self.components and self.components.messages is not None:
            self.components.messages[message_name] = model_validate(Message, new_message)

        one_of = {"$ref": f"#/components/messages/{message_name}"}
        if (
            self.channels
            and self.channels[channel_name]
            and self.channels[channel_name].subscribe
            and self.channels[channel_name].subscribe.message
        ):
            self.channels[channel_name].subscribe.message.__dict__["oneOf"].append(one_of)
