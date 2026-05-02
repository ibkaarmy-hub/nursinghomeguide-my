"""Tiny wrapper so the preview MCP can pass PORT via env var."""
import os, http.server, socketserver

PORT = int(os.environ.get("PORT", 3456))
Handler = http.server.SimpleHTTPRequestHandler
with socketserver.TCPServer(("", PORT), Handler) as httpd:
    print(f"Serving on port {PORT}")
    httpd.serve_forever()
