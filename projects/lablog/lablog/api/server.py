"""Threaded ``http.server`` wrapper exposing :class:`~lablog.api.app.LablogApp`."""

from __future__ import annotations

import json
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Optional, Tuple
from urllib.parse import urlparse

from .app import LablogApp, build_app

__all__ = ["make_server", "serve", "LablogHTTPServer"]


class LablogHTTPServer(ThreadingHTTPServer):
    """``ThreadingHTTPServer`` that carries the application instance."""

    daemon_threads = True
    allow_reuse_address = True

    def __init__(self, address: Tuple[str, int], app: LablogApp):
        self.app = app
        super().__init__(address, _LablogRequestHandler)


class _LablogRequestHandler(BaseHTTPRequestHandler):
    server_version = "lablog"
    protocol_version = "HTTP/1.1"

    # -- helpers ---------------------------------------------------------
    @property
    def app(self) -> LablogApp:
        return self.server.app  # type: ignore[attr-defined]

    def _read_body(self) -> bytes:
        length = int(self.headers.get("Content-Length") or 0)
        return self.rfile.read(length) if length > 0 else b""

    def _respond(self, response) -> None:
        self.send_response(response.status)
        self.send_header("Content-Type", response.content_type)
        self.send_header("Content-Length", str(len(response.body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, PATCH, DELETE, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        for key, value in response.headers.items():
            self.send_header(key, value)
        self.end_headers()
        if response.body:
            self.wfile.write(response.body)

    def _dispatch(self, method: str) -> None:
        target = self.path
        parsed = urlparse(target)
        try:
            body = self._read_body()
            response = self.app.handle(method, parsed.path + (f"?{parsed.query}" if parsed.query else ""), body)
        except Exception as exc:  # pragma: no cover - defensive top-level guard
            payload = json.dumps({"error": f"internal error: {exc}"}).encode("utf-8")
            self.send_response(500)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(payload)))
            self.end_headers()
            self.wfile.write(payload)
            return
        self._respond(response)

    # -- verbs -----------------------------------------------------------
    def do_GET(self) -> None:  # noqa: N802 - http.server API
        self._dispatch("GET")

    def do_POST(self) -> None:  # noqa: N802
        self._dispatch("POST")

    def do_PATCH(self) -> None:  # noqa: N802
        self._dispatch("PATCH")

    def do_DELETE(self) -> None:  # noqa: N802
        self._dispatch("DELETE")

    def do_OPTIONS(self) -> None:  # noqa: N802
        self._dispatch("OPTIONS")

    def log_message(self, fmt: str, *args) -> None:  # noqa: A003 - http.server API
        if getattr(self.server, "quiet", False):
            return
        sys.stderr.write("[lablog] %s - %s\n" % (self.address_string(), fmt % args))


def make_server(
    db_path: Path | str,
    *,
    host: str = "127.0.0.1",
    port: int = 8765,
    root: Optional[Path | str] = None,
    quiet: bool = True,
) -> LablogHTTPServer:
    app = build_app(db_path, root=root)
    server = LablogHTTPServer((host, port), app)
    server.quiet = quiet  # type: ignore[attr-defined]
    return server


def serve(
    db_path: Path | str,
    *,
    host: str = "127.0.0.1",
    port: int = 8765,
    root: Optional[Path | str] = None,
    quiet: bool = False,
) -> None:
    server = make_server(db_path, host=host, port=port, root=root, quiet=quiet)
    actual_host, actual_port = server.server_address[0], server.server_address[1]
    url = f"http://{actual_host}:{actual_port}/"
    print(f"lablog dashboard on {url}")
    print("press Ctrl+C to stop")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nstopping")
    finally:
        server.server_close()
