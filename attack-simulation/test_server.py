"""
Simple DVWA-like Test HTTP Server

Endpoints:
- GET /                 : Home page
- GET /health           : Health check (200 OK)
- GET /search?q=...     : Simulate a search endpoint (for SQLi testing)
- GET /item?id=...      : Simulate item lookup by id (for SQLi testing)
- POST /login           : Simulate login endpoint (for brute-force testing)

Notes:
- This server is intentionally simple and should only be used locally.
- It prints minimal logs to the console for visibility during attacks.

Run:
  python attack-simulation/test_server.py --host 127.0.0.1 --port 8000
"""

from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import argparse
import json
import sys


VALID_USERS = {
    "admin": "password",
    "user": "123456",
}


class DVWAHandler(BaseHTTPRequestHandler):
    server_version = "DVWATestServer/0.1"

    def _set_headers(self, status=200, content_type="text/html"):
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Connection", "close")
        self.end_headers()

    def safe_write(self, data: bytes):
        try:
            self.wfile.write(data)
        except (BrokenPipeError, ConnectionAbortedError):
            # Client closed connection early (common during stress/slowloris)
            pass

    def log_message(self, format, *args):
        # Minimal console logging
        print(f"[{self.address_string()}] {self.command} {self.path} - " + (format % args))

    def log_error(self, format, *args):
        # Avoid noisy tracebacks for client aborts
        msg = format % args
        if "Broken pipe" in msg or "aborted" in msg.lower():
            print(f"[WARN] Suppressed error: {msg}")
        else:
            super().log_error(format, *args)

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path
        qs = parse_qs(parsed.query)

        if path == "/" or path == "":
            self._set_headers(200)
            self.safe_write(b"<h1>DVWA Test Server</h1><p>Endpoints: /health, /search?q=, /item?id=, POST /login</p>")
            return

        if path == "/health":
            self._set_headers(200, "application/json")
            self.safe_write(json.dumps({"status": "ok"}).encode())
            return

        if path == "/search":
            q = qs.get("q", [""])[0]
            # Simulate naive echo of query (no real SQL)
            self._set_headers(200)
            self.safe_write(f"<p>Search results for: {q}</p>".encode())
            return

        if path == "/item":
            item_id = qs.get("id", [""])[0]
            self._set_headers(200)
            self.safe_write(f"<p>Item details for id={item_id}</p>".encode())
            return

        # Fallback 404
        self._set_headers(404)
        self.safe_write(b"Not Found")

    def do_POST(self):
        parsed = urlparse(self.path)
        path = parsed.path

        if path == "/login":
            length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(length).decode("utf-8") if length else ""
            params = parse_qs(body)
            username = params.get("username", [""])[0]
            password = params.get("password", [""])[0]

            if VALID_USERS.get(username) == password:
                self._set_headers(200, "application/json")
                self.safe_write(json.dumps({"login": "success"}).encode())
            else:
                # Intentionally 401 to simulate brute force failures
                self._set_headers(401, "application/json")
                self.safe_write(json.dumps({"login": "failure"}).encode())
            return

        # Fallback 404
        self._set_headers(404)
        self.safe_write(b"Not Found")


def main():
    parser = argparse.ArgumentParser(description="Run a simple DVWA-like local HTTP server")
    parser.add_argument("--host", default="127.0.0.1", help="Host to bind (default: 127.0.0.1)")
    parser.add_argument("--port", type=int, default=8000, help="Port to bind (default: 8000)")
    args = parser.parse_args()

    httpd = HTTPServer((args.host, args.port), DVWAHandler)
    print(f"DVWA Test Server running at http://{args.host}:{args.port}")
    print("Press Ctrl+C to stop.")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down server...")
    finally:
        httpd.server_close()


if __name__ == "__main__":
    main()
