"""Local dev proxy for the Ear workbench — serves the static app and forwards
/api/v1/* to the Ear API on the same origin (the production deployment shape).
Run: python dev_proxy.py [port] [api_base]
"""

from __future__ import annotations

import http.server
import os
import sys
import urllib.request

ROOT = os.path.dirname(os.path.abspath(__file__))
API_BASE = sys.argv[2] if len(sys.argv) > 2 else "http://localhost:8010"
PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 5197


class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=ROOT, **kwargs)

    def _proxy(self):
        target = API_BASE + self.path
        body = None
        if self.command in ("POST", "PUT"):
            length = int(self.headers.get("Content-Length") or 0)
            body = self.rfile.read(length) if length else None
        request = urllib.request.Request(
            target,
            data=body,
            method=self.command,
            headers={"Content-Type": self.headers.get("Content-Type", "application/json")},
        )
        try:
            with urllib.request.urlopen(request, timeout=600) as response:
                payload = response.read()
                self.send_response(response.status)
                self.send_header("Content-Type", response.headers.get("Content-Type", "application/json"))
                self.send_header("Cache-Control", "no-store")
                self.end_headers()
                self.wfile.write(payload)
        except urllib.error.HTTPError as exc:
            self.send_response(exc.code)
            self.send_header("Content-Type", "application/json")
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(exc.read())

    def do_GET(self):
        if self.path.startswith("/api/v1"):
            return self._proxy()
        return super().do_GET()

    def do_POST(self):
        return self._proxy()

    def do_PUT(self):
        return self._proxy()

    def log_message(self, *args):
        pass  # keep the dev console quiet


if __name__ == "__main__":
    http.server.ThreadingHTTPServer(("127.0.0.1", PORT), Handler).serve_forever()
