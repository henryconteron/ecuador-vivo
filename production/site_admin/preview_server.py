"""Loopback-only preview of public site files, excluding local/editor state."""
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import threading
from urllib.parse import unquote, urlsplit


def start_preview(root):
    root = Path(root).resolve()

    class Handler(SimpleHTTPRequestHandler):
        def do_GET(self):
            path = unquote(urlsplit(self.path).path).lstrip('/') or 'index.html'
            candidate = (root / path).resolve()
            parts = Path(path).parts
            if (not candidate.is_relative_to(root) or not parts or
                    any(part.startswith('.') or part in {'_local', 'production', 'node_modules'} for part in parts) or
                    not candidate.is_file()):
                self.send_error(404)
                return
            super().do_GET()

        def do_HEAD(self):
            self.send_error(405)

        def end_headers(self):
            self.send_header('Cache-Control', 'no-store')
            super().end_headers()

        def log_message(self, *_):
            pass

    server = ThreadingHTTPServer(('127.0.0.1', 0), partial(Handler, directory=str(root)))
    threading.Thread(target=server.serve_forever, daemon=True).start()
    return server
