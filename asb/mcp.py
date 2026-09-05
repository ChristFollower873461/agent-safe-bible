"""Stdio MCP server that wraps local lookup only."""

from __future__ import annotations

import json
import sys
from typing import Any

from . import __version__
from .allowlist import allowlist
from .jsonutil import dumps
from .lookup import LookupFailure, get

PROTOCOL = "2024-11-05"

TOOLS = [
    {
        "name": "get_passage",
        "description": (
            "Look up a public-domain Bible verse or range from the local hashed corpus. "
            "Default translation is BSB. Refused translations and unknown refs fail closed. "
            "Never use this tool to fetch NIV, ESV, NASB, NLT, CSB, or NKJV."
        ),
        "inputSchema": {
            "type": "object",
            "additionalProperties": False,
            "required": ["ref"],
            "properties": {
                "ref": {
                    "type": "string",
                    "description": 'Human reference such as "John 3:16" or "Psalm 23:1-4".',
                },
                "translation": {
                    "type": "string",
                    "description": "Allowed id: BSB, WEB, or KJV. Defaults to BSB.",
                },
            },
        },
    },
    {
        "name": "list_translations",
        "description": "List allowed and refused translations for this corpus.",
        "inputSchema": {"type": "object", "additionalProperties": False, "properties": {}},
    },
]


def _send(message: dict[str, Any]) -> None:
    # MCP stdio is one UTF-8 JSON-RPC message per line, without LSP headers.
    body = json.dumps(message, ensure_ascii=False).encode("utf-8")
    sys.stdout.buffer.write(body + b"\n")
    sys.stdout.buffer.flush()


def _read() -> dict[str, Any] | None:
    line = sys.stdin.buffer.readline()
    if not line:
        return None
    return json.loads(line.decode("utf-8"))


def _result(request_id: Any, payload: Any, is_error: bool = False) -> dict[str, Any]:
    text = payload if isinstance(payload, str) else dumps(payload)
    return {
        "jsonrpc": "2.0",
        "id": request_id,
        "result": {
            "content": [{"type": "text", "text": text}],
            "isError": is_error,
        },
    }


def _call_tool(name: str, arguments: dict[str, Any]) -> tuple[Any, bool]:
    if name == "list_translations":
        data = allowlist()
        return {
            "default": data["default_translation"],
            "allowed": [row["id"] for row in data["translations"] if row["status"] == "allowed"],
            "refused": [row["id"] for row in data["refused"]],
        }, False
    if name == "get_passage":
        ref = arguments.get("ref")
        if not ref:
            return {"ok": False, "error": "missing_ref", "message": "ref is required"}, True
        try:
            return get(str(ref), arguments.get("translation")), False
        except LookupFailure as exc:
            return exc.as_dict(), True
    return {"ok": False, "error": "unknown_tool", "message": name}, True


def handle(message: dict[str, Any]) -> dict[str, Any] | None:
    method = message.get("method")
    request_id = message.get("id")
    if method == "initialize":
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {
                "protocolVersion": PROTOCOL,
                "capabilities": {"tools": {}},
                "serverInfo": {"name": "agent-safe-bible", "version": __version__},
            },
        }
    if method == "notifications/initialized":
        return None
    if method == "tools/list":
        return {"jsonrpc": "2.0", "id": request_id, "result": {"tools": TOOLS}}
    if method == "tools/call":
        params = message.get("params") or {}
        payload, is_error = _call_tool(params.get("name"), params.get("arguments") or {})
        return _result(request_id, payload, is_error)
    if method == "ping":
        return {"jsonrpc": "2.0", "id": request_id, "result": {}}
    if request_id is None:
        return None
    return {
        "jsonrpc": "2.0",
        "id": request_id,
        "error": {"code": -32601, "message": f"Unknown method {method}"},
    }


def serve() -> None:
    while True:
        message = _read()
        if message is None:
            return
        reply = handle(message)
        if reply is not None:
            _send(reply)
