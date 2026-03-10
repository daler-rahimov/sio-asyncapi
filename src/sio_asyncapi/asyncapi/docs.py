"""AsyncAPI 3.1 documentation generation for Socket.IO servers."""
import copy
import json
import re
import textwrap
from urllib.parse import urlsplit
from typing import Any, Callable, Dict, Literal, Optional, Type, Union

import yaml
from loguru import logger
from sio_asyncapi._pydantic import BaseModel

from sio_asyncapi._compat import is_pydantic_model_type, model_schema

from .utils import add_ref_prepath

NotProvidedType = Literal["NotProvided"]

add_description = """
<br/> This specification targets AsyncAPI 3.1 and keeps Socket.IO ACK values in the custom `x-ack` message extension.
Socket.IO-specific transport details may still require application-level interpretation.
"""

DEFAULT_COMPONENTS = {
    "messages": {},
    "schemas": {
        "NoSpec": {
            "description": "Specification is not provided",
        }
    },
}


class AsyncAPIDoc:
    """AsyncAPI 3.1 documentation generator."""

    def __init__(
        self,
        *,
        asyncapi: str,
        info: Dict[str, Any],
        servers: Dict[str, Any],
        channels: Dict[str, Any],
        operations: Dict[str, Any],
        components: Dict[str, Any],
    ) -> None:
        self.asyncapi = asyncapi
        self.info = info
        self.servers = servers
        self.channels = channels
        self.operations = operations
        self.components = components

    @staticmethod
    def normalize_namespace(namespace: Optional[str]) -> str:
        """Normalize Socket.IO namespace values."""
        return namespace or "/"

    @staticmethod
    def _clean_description(description: Optional[str]) -> str:
        """Normalize multiline descriptions for stable output."""
        if not description:
            return ""
        if not description.startswith(" "):
            description = " " + description
        return textwrap.dedent(description)

    @staticmethod
    def _slugify(value: str) -> str:
        """Convert a free-form value into a stable AsyncAPI identifier."""
        slug = re.sub(r"[^a-zA-Z0-9]+", "_", value).strip("_")
        return slug.lower() or "root"

    @classmethod
    def namespace_component_name(cls, namespace: Optional[str]) -> str:
        """Return a stable channel identifier for the namespace."""
        normalized_namespace = cls.normalize_namespace(namespace)
        if normalized_namespace == "/":
            return "root"
        return cls._slugify(normalized_namespace.strip("/"))

    @classmethod
    def message_component_name(
        cls,
        name: str,
        namespace: Optional[str],
        *,
        title_case: bool,
    ) -> str:
        """Build a namespace-safe message component name."""
        base_name = name.title() if title_case else name
        namespace_component = cls.namespace_component_name(namespace)
        if namespace_component == "root":
            return base_name
        namespace_prefix = "_".join(
            part.title()
            for part in cls.normalize_namespace(namespace).strip("/").split("/")
            if part
        )
        return f"{namespace_prefix}_{base_name}"


    @classmethod
    def operation_component_name(
        cls,
        action: str,
        name: str,
        namespace: Optional[str],
    ) -> str:
        """Build a namespace-safe operation identifier."""
        namespace_component = cls.namespace_component_name(namespace)
        name_component = cls._slugify(name)
        if namespace_component == "root":
            return f"{action}_{name_component}"
        return f"{namespace_component}_{action}_{name_component}"

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
        parsed_server = urlsplit(server_url)
        server_host = parsed_server.netloc or parsed_server.path or server_url
        server = {
            "host": server_host,
            "protocol": server_protocol,
        }
        if parsed_server.path and parsed_server.netloc and parsed_server.path != "/":
            server["pathname"] = parsed_server.path

        return cls(
            asyncapi="3.1.0",
            info={
                "title": title,
                "version": version,
                "description": description + add_description,
            },
            servers={server_name: server},
            channels={},
            operations={},
            components=copy.deepcopy(DEFAULT_COMPONENTS),
        )

    def dict(self, **_: Any) -> Dict[str, Any]:
        """Return the AsyncAPI document as a plain dict."""
        return {
            "asyncapi": self.asyncapi,
            "info": copy.deepcopy(self.info),
            "servers": copy.deepcopy(self.servers),
            "channels": copy.deepcopy(self.channels),
            "operations": copy.deepcopy(self.operations),
            "components": copy.deepcopy(self.components),
        }

    def json(self, **kwargs: Any) -> str:
        """Return the AsyncAPI document as JSON."""
        json_kwargs = {key: value for key, value in kwargs.items() if key not in {"by_alias", "exclude_none"}}
        return json.dumps(self.dict(), **json_kwargs)

    def get_yaml(self) -> str:
        """Return AsyncAPI documentation in YAML format."""
        return yaml.safe_dump(self.dict(), sort_keys=False)

    def ensure_channel(self, namespace: Optional[str]) -> str:
        """Ensure the namespace channel exists and return its identifier."""
        normalized_namespace = self.normalize_namespace(namespace)
        channel_name = self.namespace_component_name(normalized_namespace)
        if channel_name not in self.channels:
            self.channels[channel_name] = {
                "address": normalized_namespace,
                "messages": {},
            }
        return channel_name

    def _schema_ref(
        self,
        model: Optional[Union[Type[BaseModel], NotProvidedType]],
    ) -> Optional[Dict[str, str]]:
        """Create or fetch a schema reference for a payload or reply."""
        if model == "NotProvided":
            return {"$ref": "#/components/schemas/NoSpec"}
        if not is_pydantic_model_type(model):
            return None

        schema_name = model.__name__
        schema = model_schema(model)
        add_ref_prepath(schema, f"/components/schemas/{schema_name}")
        self.components["schemas"][schema_name] = schema
        return {"$ref": f"#/components/schemas/{schema_name}"}

    def _store_message(
        self,
        *,
        channel_name: str,
        message_component: str,
        event_name: str,
        description: str,
        payload: Optional[Dict[str, str]],
    ) -> str:
        """Store a reusable message component and attach it to a channel."""
        message = {
            "name": event_name,
            "description": description,
        }
        if payload is not None:
            message["payload"] = payload

        self.components["messages"][message_component] = message
        self.channels[channel_name]["messages"][message_component] = {
            "$ref": f"#/components/messages/{message_component}"
        }
        return f"#/channels/{channel_name}/messages/{message_component}"

    def add_new_receiver(
        self,
        handler: Callable,
        name: str,
        message_name: Optional[str] = None,
        ack_data_model: Optional[Union[Type[BaseModel], NotProvidedType]] = None,
        payload_model: Optional[Union[Type[BaseModel], NotProvidedType]] = None,
        namespace: Optional[str] = None,
    ) -> None:
        """Register a client-to-server Socket.IO event as an AsyncAPI receive operation."""
        normalized_namespace = self.normalize_namespace(namespace)
        channel_name = self.ensure_channel(normalized_namespace)
        message_component = message_name or self.message_component_name(
            name,
            normalized_namespace,
            title_case=True,
        )
        description = self._clean_description(handler.__doc__)
        payload_ref = self._schema_ref(payload_model)
        message = {
            "name": name,
            "description": description,
        }
        if payload_ref is not None:
            message["payload"] = payload_ref

        ack_ref = self._schema_ref(ack_data_model)
        if ack_ref is not None:
            message["x-ack"] = ack_ref

        self.components["messages"][message_component] = message
        self.channels[channel_name]["messages"][message_component] = {
            "$ref": f"#/components/messages/{message_component}"
        }

        operation_name = self.operation_component_name(
            "receive",
            name,
            normalized_namespace,
        )
        operation = {
            "action": "receive",
            "channel": {"$ref": f"#/channels/{channel_name}"},
            "messages": [{"$ref": f"#/channels/{channel_name}/messages/{message_component}"}],
        }
        if description:
            operation["description"] = description

        self.operations[operation_name] = operation

    def add_new_sender(
        self,
        event: str,
        payload_model: Optional[Union[Type[BaseModel], NotProvidedType]] = None,
        description: Optional[str] = None,
        namespace: Optional[str] = None,
    ) -> None:
        """Register a server-to-client Socket.IO emit as an AsyncAPI send operation."""
        normalized_namespace = self.normalize_namespace(namespace)
        channel_name = self.ensure_channel(normalized_namespace)
        message_component = self.message_component_name(
            event,
            normalized_namespace,
            title_case=False,
        )
        clean_description = self._clean_description(description)
        payload_ref = self._schema_ref(payload_model)
        message_ref = self._store_message(
            channel_name=channel_name,
            message_component=message_component,
            event_name=event,
            description=clean_description,
            payload=payload_ref,
        )

        operation_name = self.operation_component_name(
            "send",
            event,
            normalized_namespace,
        )
        operation = {
            "action": "send",
            "channel": {"$ref": f"#/channels/{channel_name}"},
            "messages": [{"$ref": message_ref}],
        }
        if clean_description:
            operation["description"] = clean_description

        self.operations[operation_name] = operation

    def _lookup_ref(self, ref: str, doc_dict: Dict[str, Any]) -> Any:
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
        doc_dict: Dict[str, Any],
        *,
        seen: Optional[set[str]] = None,
    ) -> Any:
        """Resolve local refs inside a schema or AsyncAPI node recursively."""
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
                merged = {**resolved_node, **extra_fields}
                merged.setdefault("x-component-ref", ref)
                return merged
            return {"$ref": ref, **extra_fields}

        return {
            key: self._resolve_refs(value, doc_dict, seen=seen.copy())
            for key, value in node.items()
        }

    def get_agent_schema(self) -> Dict[str, Any]:
        """Return a compact agent-friendly event catalog derived from AsyncAPI 3.1."""
        doc_dict = self.dict()
        events: list[Dict[str, Any]] = []

        for operation_id in sorted(doc_dict["operations"]):
            operation = doc_dict["operations"][operation_id]
            channel = self._resolve_refs(operation["channel"], doc_dict)
            namespace = channel.get("address", "/")
            direction = "client_to_server" if operation["action"] == "receive" else "server_to_client"
            message_ref = operation["messages"][0]["$ref"]
            message_component = message_ref.rsplit("/", 1)[-1]
            message = self._resolve_refs({"$ref": message_ref}, doc_dict)

            event = {
                "name": message.get("name", message_component),
                "namespace": namespace,
                "direction": direction,
                "operation_id": operation_id,
                "message_component": message_component,
                "description": message.get("description") or operation.get("description", ""),
            }

            payload = message.get("payload")
            if payload is not None:
                schema_key = "input_schema" if direction == "client_to_server" else "output_schema"
                event[schema_key] = self._resolve_refs(payload, doc_dict)
                if isinstance(payload, dict) and payload.get("x-component-ref"):
                    event[f"{schema_key}_component"] = payload["x-component-ref"].rsplit("/", 1)[-1]

            if direction == "client_to_server":
                ack_schema = message.get("x-ack")
                if ack_schema is not None:
                    event["ack_schema"] = self._resolve_refs(ack_schema, doc_dict)
                    if isinstance(event["ack_schema"], dict) and event["ack_schema"].get("x-component-ref"):
                        event["ack_schema_component"] = event["ack_schema"]["x-component-ref"].rsplit("/", 1)[-1]

            events.append(event)

        return {
            "format": "sio-asyncapi-agent-schema",
            "version": "1.0",
            "asyncapi_version": doc_dict["asyncapi"],
            "info": doc_dict["info"],
            "servers": doc_dict["servers"],
            "events": events,
        }

    def get_agent_schema_json(self) -> str:
        """Return the compact agent-friendly event catalog as JSON."""
        return json.dumps(self.get_agent_schema(), indent=2, sort_keys=True)
