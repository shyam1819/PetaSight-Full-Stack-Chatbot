"""Tiny request/response helpers shared by the thin serverless handlers."""
from __future__ import annotations

import json
from http.server import BaseHTTPRequestHandler


def read_json(handler: BaseHTTPRequestHandler) -> dict:
    """Parse a JSON request body into a dict; returns {} for empty/invalid bodies."""
    length = int(handler.headers.get("Content-Length") or 0)
    raw = handler.rfile.read(length) if length else b""
    try:
        data = json.loads(raw or b"{}")
    except (ValueError, TypeError):
        return {}
    return data if isinstance(data, dict) else {}


def send_json(
    handler: BaseHTTPRequestHandler,
    status: int,
    payload: dict,
    extra_headers: dict | None = None,
) -> None:
    body = json.dumps(payload).encode("utf-8")
    handler.send_response(status)
    handler.send_header("Content-Type", "application/json")
    for key, value in (extra_headers or {}).items():
        handler.send_header(key, value)
    handler.end_headers()
    handler.wfile.write(body)
