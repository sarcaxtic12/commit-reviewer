"""Local web server module for commit-reviewer.

Hosts the report locally.
"""

import http.server
import socketserver
import webbrowser
import os
import threading

def serve(report_path: str, port: int = 3546):
    """Run a simple HTTP server to serve the report."""
    directory  = os.path.dirname(report_path)
    filename   = os.path.basename(report_path)
    url        = f"http://localhost:{port}/{filename}"

    if directory:
        os.chdir(directory)

    handler = http.server.SimpleHTTPRequestHandler

    # Silence the default request logs — they're noisy and not useful here
    class QuietHandler(handler):
        def log_message(self, format, *args):
            pass

    try:
        with socketserver.TCPServer(("", port), QuietHandler) as httpd:
            threading.Timer(1.0, lambda: webbrowser.open(url)).start()
            print(f"  Report served at {url}")
            print(f"  Press Ctrl+C to stop.\n")
            httpd.serve_forever()
    except OSError as e:
        if e.errno == 98 or e.errno == 10048:
            print(f"Port {port} is already in use. Open {report_path} manually.")
        else:
            raise
