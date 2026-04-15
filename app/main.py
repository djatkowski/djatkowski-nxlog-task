import json
import os
from http.server import BaseHTTPRequestHandler, HTTPServer


class Handler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):  # noqa: A002
        print(f"{self.address_string()} - {format % args}")

    def do_GET(self):
        if self.path == "/healthz":
            self._respond(200, b"ok\n")
            return

        if self.path != "/":
            self._respond(404, b"not found\n")
            return

        body = json.dumps(dict(os.environ), indent=2, sort_keys=True).encode()
        self._respond(200, body, content_type="application/json")

    def _respond(self, status: int, body: bytes, content_type: str = "text/plain") -> None:
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(("0.0.0.0", port), Handler)
    print(f"Server listening on :{port}")
    server.serve_forever()
