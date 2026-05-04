"""Dev server with /_config endpoint that reads .env.local for token pre-fill."""
import os, json, http.server, socketserver

PORT = int(os.environ.get("PORT", 3456))

def load_env_local():
    config = {}
    try:
        with open('.env.local') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    k, v = line.split('=', 1)
                    config[k.strip()] = v.strip().strip('"').strip("'")
    except FileNotFoundError:
        pass
    return config

class Handler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/_config':
            env = load_env_local()
            data = {
                'googleToken': env.get('GOOGLE_TOKEN', ''),
                'githubToken': env.get('GITHUB_TOKEN', ''),
            }
            body = json.dumps(data).encode()
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Content-Length', str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        else:
            super().do_GET()

    def log_message(self, fmt, *args):
        pass  # silence request logs

with socketserver.TCPServer(("", PORT), Handler) as httpd:
    print(f"Serving on port {PORT}")
    httpd.serve_forever()
