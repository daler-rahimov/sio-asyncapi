"""AsyncAPI 3.1 documentation generation for Socket.IO servers."""
import copy
import json
import logging
import re
import textwrap
from typing import Any, Callable, Dict, List, Literal, Optional, Type, Union
from urllib.parse import urlsplit

import yaml
from pydantic import BaseModel

from sio_asyncapi._compat import is_pydantic_model_type, model_schema

logger = logging.getLogger(__name__)

NotProvidedType = Literal["NotProvided"]
LIFECYCLE_EVENTS = frozenset({"connect", "disconnect"})
JSON_SCHEMA_2020_12 = "https://json-schema.org/draft/2020-12/schema"

add_description = """
<br/> This specification targets AsyncAPI 3.1. Socket.IO ACKs are modeled as operation `reply` messages, with the custom `x-ack` extension kept as an alias.
Socket.IO-specific transport details may still require application-level interpretation.
"""

DEFAULT_COMPONENTS = {
    "messages": {},
    "schemas": {
        "NoSpec": {
            "$schema": JSON_SCHEMA_2020_12,
            "description": "Specification is not provided",
        }
    },
}

DEFAULT_SOCKETIO_SECURITY_SCHEME = {
    "type": "userPassword",
    "description": (
        "Socket.IO handshake authentication. The connect event payload "
        "describes the auth object sent by the client."
    ),
}


class SchemaNameCollisionError(ValueError):
    """Raised when two different Pydantic models share an AsyncAPI schema name."""


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
        security_scheme: Optional[Dict[str, Any]] = None,
        security_scheme_name: str = "socketioAuth",
        auth_model: Optional[Type[BaseModel]] = None,
    ) -> "AsyncAPIDoc":
        """Initialize AsyncAPI documentation generator."""
        logger.debug(
            "Initializing AsyncAPI docs: server_url=%s server_name=%s protocol=%s",
            server_url,
            server_name,
            server_protocol,
        )
        parsed_server = urlsplit(server_url)
        server_host = parsed_server.netloc or parsed_server.path or server_url
        server: Dict[str, Any] = {
            "host": server_host,
            "protocol": server_protocol,
        }
        if parsed_server.path and parsed_server.netloc and parsed_server.path != "/":
            server["pathname"] = parsed_server.path

        components = copy.deepcopy(DEFAULT_COMPONENTS)
        if security_scheme is None and auth_model is not None:
            security_scheme = copy.deepcopy(DEFAULT_SOCKETIO_SECURITY_SCHEME)
        if security_scheme is not None:
            components["securitySchemes"] = {security_scheme_name: security_scheme}
            server["security"] = [
                {"$ref": f"#/components/securitySchemes/{security_scheme_name}"}
            ]

        doc = cls(
            asyncapi="3.1.0",
            info={
                "title": title,
                "version": version,
                "description": description + add_description,
            },
            servers={server_name: server},
            channels={},
            operations={},
            components=components,
        )
        if auth_model is not None:
            doc.add_new_receiver(
                None,
                "connect",
                payload_model=auth_model,
                ack_data_model=None,
            )
        return doc

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
        json_kwargs = {
            key: value
            for key, value in kwargs.items()
            if key not in {"by_alias", "exclude_none"}
        }
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

    def _example_to_examples(self, node: Any) -> Any:
        """Rewrite deprecated JSON Schema `example` keys to 2020-12 `examples`."""
        if isinstance(node, list):
            return [self._example_to_examples(item) for item in node]
        if not isinstance(node, dict):
            return node
        converted = {
            key: self._example_to_examples(value)
            for key, value in node.items()
            if key != "example"
        }
        if "example" in node and "examples" not in converted:
            converted["examples"] = [self._example_to_examples(node["example"])]
        return converted

    def _normalize_json_schema(self, schema: Dict[str, Any]) -> Dict[str, Any]:
        """Mark a component schema as JSON Schema 2020-12."""
        schema = self._example_to_examples(schema)
        schema.pop("$schema", None)
        return {"$schema": JSON_SCHEMA_2020_12, **schema}

    def _example_from_schema(self, schema: Optional[Dict[str, Any]]) -> Any:
        """Build a sample payload from JSON Schema examples."""
        if not isinstance(schema, dict):
            return None
        if schema.get("examples"):
            return schema["examples"][0]
        if schema.get("example") is not None:
            return schema["example"]
        properties = schema.get("properties")
        if not isinstance(properties, dict) or not properties:
            return None
        sample: Dict[str, Any] = {}
        for name, prop in properties.items():
            if not isinstance(prop, dict):
                continue
            if "$ref" in prop:
                target = self._lookup_ref(prop["$ref"], {
                    "components": self.components,
                })
                nested = self._example_from_schema(target)
                if nested is not None:
                    sample[name] = nested
                continue
            nested = self._example_from_schema(prop)
            if nested is not None:
                sample[name] = nested
        return sample or None

    def _message_examples(
        self,
        model: Optional[Union[Type[BaseModel], NotProvidedType]],
    ) -> Optional[List[Dict[str, Any]]]:
        """Return AsyncAPI message examples derived from a Pydantic model."""
        if not is_pydantic_model_type(model):
            return None
        raw_schema = self._example_to_examples(model_schema(model))
        payload = self._example_from_schema(raw_schema)
        if payload is None:
            return None
        return [{"name": "example", "payload": payload}]

    def _choose_schema_name(
        self,
        preferred: str,
        schema: Dict[str, Any],
        parent_name: Optional[str] = None,
    ) -> str:
        """Return a unique components/schemas name, prefixing on collision."""
        existing = self.components["schemas"].get(preferred)
        if existing is None or existing == schema:
            return preferred
        if parent_name:
            prefixed = f"{parent_name}_{preferred}"
            prefixed_existing = self.components["schemas"].get(prefixed)
            if prefixed_existing is None or prefixed_existing == schema:
                return prefixed
            raise SchemaNameCollisionError(
                f"AsyncAPI schema name {prefixed!r} is already used by a different model. "
                "Rename one of the Pydantic models to avoid the collision."
            )
        raise SchemaNameCollisionError(
            f"AsyncAPI schema name {preferred!r} is already used by a different model. "
            "Rename one of the Pydantic models to avoid the collision."
        )

    def _put_schema(self, name: str, schema: Dict[str, Any]) -> str:
        """Store a schema component, reusing equal schemas and rejecting collisions."""
        schema = self._normalize_json_schema(schema)
        chosen = self._choose_schema_name(name, schema)
        self.components["schemas"][chosen] = schema
        return chosen

    def _rewrite_defs_refs(self, node: Any, mapping: Dict[str, str]) -> Any:
        """Rewrite local $defs/definitions refs to components/schemas refs."""
        if isinstance(node, list):
            for index, item in enumerate(node):
                node[index] = self._rewrite_defs_refs(item, mapping)
            return node
        if not isinstance(node, dict):
            return node

        ref = node.get("$ref")
        if isinstance(ref, str):
            for prefix in ("#/$defs/", "#/definitions/"):
                if ref.startswith(prefix):
                    def_name = ref[len(prefix):]
                    if def_name in mapping:
                        node["$ref"] = f"#/components/schemas/{mapping[def_name]}"
                    break
        for key, value in list(node.items()):
            if key != "$ref":
                node[key] = self._rewrite_defs_refs(value, mapping)
        return node

    def _hoist_nested_schemas(
        self,
        schema: Dict[str, Any],
        parent_name: str,
    ) -> Dict[str, Any]:
        """Promote nested JSON Schema $defs into components/schemas."""
        schema = copy.deepcopy(schema)
        defs: Dict[str, Any] = {}
        if "$defs" in schema:
            defs.update(schema.pop("$defs") or {})
        if "definitions" in schema:
            defs.update(schema.pop("definitions") or {})
        if not defs:
            return schema

        name_map: Dict[str, str] = {}
        flattened_defs: Dict[str, Dict[str, Any]] = {}
        for def_name, def_schema in defs.items():
            if not isinstance(def_schema, dict):
                continue
            flattened = self._hoist_nested_schemas(def_schema, def_name)
            component_name = self._choose_schema_name(
                def_name,
                self._normalize_json_schema(copy.deepcopy(flattened)),
                parent_name=parent_name,
            )
            name_map[def_name] = component_name
            flattened_defs[def_name] = flattened

        for def_name, flattened in flattened_defs.items():
            self._rewrite_defs_refs(flattened, name_map)
            self._put_schema(name_map[def_name], flattened)

        self._rewrite_defs_refs(schema, name_map)
        return schema

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
        schema = self._hoist_nested_schemas(model_schema(model), schema_name)
        stored_name = self._put_schema(schema_name, schema)
        return {"$ref": f"#/components/schemas/{stored_name}"}

    def _store_message(
        self,
        *,
        channel_name: str,
        message_component: str,
        event_name: str,
        description: str,
        payload: Optional[Dict[str, str]],
        examples: Optional[List[Dict[str, Any]]] = None,
    ) -> str:
        """Store a reusable message component and attach it to a channel."""
        message: Dict[str, Any] = {
            "name": event_name,
            "description": description,
        }
        if payload is not None:
            message["payload"] = payload
        if examples:
            message["examples"] = examples

        self.components["messages"][message_component] = message
        self.channels[channel_name]["messages"][message_component] = {
            "$ref": f"#/components/messages/{message_component}"
        }
        return f"#/channels/{channel_name}/messages/{message_component}"

    def add_new_receiver(
        self,
        handler: Optional[Callable],
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
        description = self._clean_description(
            getattr(handler, "__doc__", None) if handler is not None else None
        )
        payload_ref = self._schema_ref(payload_model)
        message: Dict[str, Any] = {
            "name": name,
            "description": description,
        }
        if payload_ref is not None:
            message["payload"] = payload_ref
        examples = self._message_examples(payload_model)
        if examples:
            message["examples"] = examples

        is_lifecycle = name in LIFECYCLE_EVENTS
        if is_lifecycle:
            message["x-lifecycle"] = True

        self.components["messages"][message_component] = message
        self.channels[channel_name]["messages"][message_component] = {
            "$ref": f"#/components/messages/{message_component}"
        }

        operation_name = self.operation_component_name(
            "receive",
            name,
            normalized_namespace,
        )
        operation: Dict[str, Any] = {
            "action": "receive",
            "channel": {"$ref": f"#/channels/{channel_name}"},
            "messages": [
                {"$ref": f"#/channels/{channel_name}/messages/{message_component}"}
            ],
        }
        if description:
            operation["description"] = description
        if is_lifecycle:
            operation["x-lifecycle"] = name
        elif ack_data_model is not None:
            ack_ref = self._schema_ref(ack_data_model)
            if ack_ref is not None:
                message["x-ack"] = copy.deepcopy(ack_ref)
                ack_component = f"{message_component}_Ack"
                ack_message: Dict[str, Any] = {
                    "name": f"{name}_ack",
                    "description": f"Socket.IO ACK for {name}",
                    "payload": copy.deepcopy(ack_ref),
                }
                ack_examples = self._message_examples(ack_data_model)
                if ack_examples:
                    ack_message["examples"] = ack_examples
                self.components["messages"][ack_component] = ack_message
                self.channels[channel_name]["messages"][ack_component] = {
                    "$ref": f"#/components/messages/{ack_component}"
                }
                operation["reply"] = {
                    "channel": {"$ref": f"#/channels/{channel_name}"},
                    "messages": [{
                        "$ref": f"#/channels/{channel_name}/messages/{ack_component}"
                    }],
                }

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
            examples=self._message_examples(payload_model),
        )

        operation_name = self.operation_component_name(
            "send",
            event,
            normalized_namespace,
        )
        operation: Dict[str, Any] = {
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
        seen: Optional[set] = None,
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
        events: List[Dict[str, Any]] = []

        for operation_id in sorted(doc_dict["operations"]):
            operation = doc_dict["operations"][operation_id]
            channel = self._resolve_refs(operation["channel"], doc_dict)
            namespace = channel.get("address", "/")
            direction = (
                "client_to_server"
                if operation["action"] == "receive"
                else "server_to_client"
            )
            message_ref = operation["messages"][0]["$ref"]
            message_component = message_ref.rsplit("/", 1)[-1]
            message = self._resolve_refs({"$ref": message_ref}, doc_dict)

            event: Dict[str, Any] = {
                "name": message.get("name", message_component),
                "namespace": namespace,
                "direction": direction,
                "operation_id": operation_id,
                "message_component": message_component,
                "description": message.get("description")
                or operation.get("description", ""),
            }
            if message.get("x-lifecycle") or operation.get("x-lifecycle"):
                event["lifecycle"] = operation.get("x-lifecycle") or message.get("name")
            if message.get("examples"):
                event["examples"] = message["examples"]

            payload = message.get("payload")
            if payload is not None:
                schema_key = (
                    "input_schema" if direction == "client_to_server" else "output_schema"
                )
                event[schema_key] = self._resolve_refs(payload, doc_dict)
                if isinstance(payload, dict) and payload.get("x-component-ref"):
                    event[f"{schema_key}_component"] = payload["x-component-ref"].rsplit(
                        "/", 1
                    )[-1]
                elif isinstance(payload, dict) and payload.get("$ref"):
                    event[f"{schema_key}_component"] = payload["$ref"].rsplit("/", 1)[-1]

            if direction == "client_to_server":
                ack_schema = message.get("x-ack")
                if ack_schema is None:
                    reply = operation.get("reply") or {}
                    reply_messages = reply.get("messages") or []
                    if reply_messages:
                        ack_message = self._resolve_refs(reply_messages[0], doc_dict)
                        ack_schema = ack_message.get("payload") if isinstance(ack_message, dict) else None
                if ack_schema is not None:
                    event["ack_schema"] = self._resolve_refs(ack_schema, doc_dict)
                    if isinstance(event["ack_schema"], dict) and event["ack_schema"].get(
                        "x-component-ref"
                    ):
                        event["ack_schema_component"] = event["ack_schema"][
                            "x-component-ref"
                        ].rsplit("/", 1)[-1]

            events.append(event)

        result: Dict[str, Any] = {
            "format": "sio-asyncapi-agent-schema",
            "version": "1.0",
            "asyncapi_version": doc_dict["asyncapi"],
            "info": doc_dict["info"],
            "servers": doc_dict["servers"],
            "events": events,
        }
        security_schemes = doc_dict["components"].get("securitySchemes")
        if security_schemes:
            result["security_schemes"] = security_schemes
        return result

    def get_agent_schema_json(self) -> str:
        """Return the compact agent-friendly event catalog as JSON."""
        return json.dumps(self.get_agent_schema(), indent=2, sort_keys=True)
