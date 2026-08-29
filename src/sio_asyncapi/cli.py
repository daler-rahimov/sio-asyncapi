"""Command-line interface for sio-asyncapi."""
from __future__ import annotations

import argparse
import importlib
import sys
from pathlib import Path
from typing import Any, Optional, Sequence


def _load_target(target: str) -> Any:
    if ":" not in target:
        raise SystemExit("Target must be in the form module:attribute, e.g. app:socketio")
    module_name, attr_name = target.split(":", 1)
    module = importlib.import_module(module_name)
    obj: Any = module
    for part in attr_name.split("."):
        obj = getattr(obj, part)
    return obj


def _get_doc(obj: Any) -> Any:
    if hasattr(obj, "asyncapi_doc"):
        return obj.asyncapi_doc
    if hasattr(obj, "get_yaml") and hasattr(obj, "dict"):
        return obj
    raise SystemExit("Target does not look like an AsyncAPISocketIO, AsyncAPIAsyncServer, or AsyncAPIDoc")


def export_command(args: argparse.Namespace) -> int:
    obj = _load_target(args.target)
    doc = _get_doc(obj)
    if args.agent_schema:
        output = obj.get_agent_schema_json() if hasattr(obj, "get_agent_schema_json") else doc.get_agent_schema_json()
        default_name = "agent-schema.json"
    elif args.format == "json":
        output = doc.json(indent=2)
        default_name = "asyncapi.json"
    else:
        output = doc.get_yaml()
        default_name = "asyncapi.yml"

    if args.out:
        path = Path(args.out)
        path.write_text(output)
        print(f"Wrote {path}")
    else:
        sys.stdout.write(output)
        if not output.endswith("\n"):
            sys.stdout.write("\n")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="python -m sio_asyncapi",
        description="Export AsyncAPI documents from a Socket.IO application.",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    export = sub.add_parser("export", help="Export an AsyncAPI or agent schema document")
    export.add_argument("target", help="Import path, e.g. examples.simple:socketio")
    export.add_argument("--out", "-o", help="Output file path (default: stdout)")
    export.add_argument(
        "--format",
        choices=["yaml", "json"],
        default="yaml",
        help="AsyncAPI document format (ignored with --agent-schema)",
    )
    export.add_argument(
        "--agent-schema",
        action="store_true",
        help="Export the compact agent-friendly catalog as JSON",
    )
    export.set_defaults(func=export_command)
    return parser


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
