"""
AsycnAPI [https://studio.asyncapi.com/] documentation auto generation.
"""
import copy
import json
import textwrap
from typing import Any, Callable, Literal, Optional, Type, Union

import yaml
from loguru import logger
from sio_asyncapi._pydantic import BaseModel

from sio_asyncapi._compat import (
    is_pydantic_model_type,
    model_dump_json,
    model_schema,
    model_validate,
)
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

    def _get_doc_dict(self) -> dict[str, Any]:
        """Return the AsyncAPI document as a plain dict."""
        return json.loads(
            model_dump_json(
                self,
                by_alias=True,
                exclude_none=True,
            )
        )

    def _lookup_ref(self, ref: str, doc_dict: dict[str, Any]) -> Any:
        """Resolve a local AsyncAPI ref against the document dict."""
        if not ref.startswith("#/"):
            return None

        current: Any = doc_dict
        for part in ref[2:].split("/"):
            if not isinstance(current, dict) or part not in current:
                return None
            current = current[part]
        return copy.deepcopy(current)

    def _resolve_refs(
        self,
        node: Any,
        doc_dict: dict[str, Any],
        *,
        seen: Optional[set[str]] = None,
    ) -> Any:
        """Resolve local refs inside a schema/message payload recursively."""
        if seen is None:
            seen = set()

        if isinstance(node, list):
            return [self._resolve_refs(item, doc_dict, seen=seen.copy()) for item in node]

        if not isinstance(node, dict):
            return node

        if "$ref" in node and isinstance(node["$ref"], str):
            ref = node["$ref"]
            resolved_target = self._lookup_ref(ref, doc_dict)
            extra_fields = {
                key: self._resolve_refs(value, doc_dict, seen=seen.copy())
                for key, value in node.items()
                if key != "$ref"
            }
            if resolved_target is None or ref in seen:
                return {"$ref": ref, **extra_fields}

            resolved_node = self._resolve_refs(
                resolved_target,
                doc_dict,
                seen=seen | {ref},
            )
            if isinstance(resolved_node, dict):
                merged = {
                    **resolved_node,
                    **extra_fields,
                }
                merged.setdefault("x-component-ref", ref)
                return merged
            return {"$ref": ref, **extra_fields}

        return {
            key: self._resolve_refs(value, doc_dict, seen=seen.copy())
            for key, value in node.items()
        }

    def _build_agent_events(
        self,
        channel_name: str,
        message_refs: list[dict[str, Any]],
        direction: str,
        doc_dict: dict[str, Any],
    ) -> list[dict[str, Any]]:
        """Build agent-friendly event entries from AsyncAPI refs."""
        events: list[dict[str, Any]] = []

        for ref_entry in message_refs:
            message_ref = ref_entry.get("$ref")
            if not message_ref:
                continue

            message_component = message_ref.rsplit("/", 1)[-1]
            raw_message = self._lookup_ref(message_ref, doc_dict)
            if not isinstance(raw_message, dict):
                continue

            event = {
                "name": raw_message.get("name", message_component),
                "namespace": channel_name,
                "direction": direction,
                "message_component": message_component,
                "description": raw_message.get("description", ""),
            }

            payload = raw_message.get("payload")
            if payload is not None:
                payload_ref = payload.get("$ref") if isinstance(payload, dict) else None
                payload_key = "input_schema" if direction == "client_to_server" else "output_schema"
                event[payload_key] = self._resolve_refs(payload, doc_dict)
                if payload_ref:
                    event[f"{payload_key}_component"] = payload_ref.rsplit("/", 1)[-1]

            if direction == "client_to_server":
                ack = raw_message.get("x-ack")
                if ack is not None:
                    event["ack_schema"] = self._resolve_refs(ack, doc_dict)
                    if isinstance(ack, dict) and ack.get("title"):
                        event["ack_schema_component"] = ack["title"]

            events.append(event)

        return events

    def get_agent_schema(self) -> dict[str, Any]:
        """Return a compact agent-friendly event catalog derived from AsyncAPI."""
        doc_dict = self._get_doc_dict()
        channels = doc_dict.get("channels", {})
        events: list[dict[str, Any]] = []

        for channel_name in sorted(channels):
            channel = channels[channel_name]
            publish_one_of = (
                channel.get("publish", {})
                .get("message", {})
                .get("oneOf", [])
            )
            subscribe_one_of = (
                channel.get("subscribe", {})
                .get("message", {})
                .get("oneOf", [])
            )
            events.extend(
                self._build_agent_events(
                    channel_name,
                    publish_one_of,
                    "client_to_server",
                    doc_dict,
                )
            )
            events.extend(
                self._build_agent_events(
                    channel_name,
                    subscribe_one_of,
                    "server_to_client",
                    doc_dict,
                )
            )

        events.sort(key=lambda item: (item["namespace"], item["direction"], item["name"]))

        return {
            "format": "sio-asyncapi-agent-schema",
            "version": "1.0",
            "asyncapi_version": doc_dict.get("asyncapi"),
            "info": doc_dict.get("info", {}),
            "servers": doc_dict.get("servers", {}),
            "events": events,
        }

    def get_agent_schema_json(self) -> str:
        """Return the compact agent-friendly event catalog as JSON."""
        return json.dumps(self.get_agent_schema(), indent=2, sort_keys=True)

    def get_yaml(self):
        """Return AsyncAPI documentation in YAML format."""
        return yaml.safe_dump(self._get_doc_dict())

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
