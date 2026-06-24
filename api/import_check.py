"""Probe: how can a Vercel Python function import shared code under api/_core/?

Temporary — used to lock the import convention for the layered backend, then removed.
A top-level import is what Vercel's dependency tracer follows (so it also tests bundling);
the in-handler variants test resolution without tracing.
"""
from http.server import BaseHTTPRequestHandler
import os
import sys
import json

# Strategy A — top-level package-style import (the convention we want to lock).
try:
    from api._core.greeting import hello as _top_hello

    _TOP = _top_hello()
except Exception as exc:  # noqa: BLE001
    _TOP = f"ERR {type(exc).__name__}"


class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        report = {
            "cwd": os.getcwd(),
            "file_dir": os.path.dirname(__file__),
            "toplevel:_core.greeting": _TOP,
            "strategies": {},
        }

        # Strategy B — add this file's dir to sys.path, then import.
        try:
            sys.path.insert(0, os.path.dirname(__file__))
            from _core.greeting import hello as hello_b

            report["strategies"]["pathinsert:_core.greeting"] = hello_b()
        except Exception as exc:  # noqa: BLE001
            report["strategies"]["pathinsert:_core.greeting"] = f"ERR {type(exc).__name__}"

        # Strategy C — package-style import.
        try:
            from api._core.greeting import hello as hello_c

            report["strategies"]["api._core.greeting"] = hello_c()
        except Exception as exc:  # noqa: BLE001
            report["strategies"]["api._core.greeting"] = f"ERR {type(exc).__name__}"

        body = json.dumps(report).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(body)
