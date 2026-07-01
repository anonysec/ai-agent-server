#!/usr/bin/env python3
"""
Full Access AI Agent Server (SSH-like via curl)
Protected with 4-digit token.

Repo: anoneysec/ai-agent-server
"""

import http.server
import socketserver
import json
import subprocess
import os
import urllib.parse
from datetime import datetime

PORT = 8080
HOST = "0.0.0.0"

# ====================== CONFIG ======================
AUTH_TOKEN = "7722"   # ← CHANGE THIS!
# ====================================================

class AgentHandler(http.server.BaseHTTPRequestHandler):
    def _send_json(self, data, status=200):
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(data, indent=2, ensure_ascii=False).encode("utf-8"))

    def _check_auth(self):
        auth_header = self.headers.get("Authorization", "")
        if auth_header.startswith("Bearer "):
            token = auth_header.replace("Bearer ", "").strip()
            return token == AUTH_TOKEN
        if "token=" in self.path:
            parsed = urllib.parse.urlparse(self.path)
            qs = urllib.parse.parse_qs(parsed.query)
            if qs.get("token", [""])[0] == AUTH_TOKEN:
                return True
        return False

    def do_GET(self):
        if not self._check_auth():
            self._send_json({"error": "Unauthorized - Invalid or missing token"}, 401)
            return

        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path

        if path in ("/", "/status"):
            self._send_json({
                "status": "ok",
                "message": "Full Access AI Agent Server is running",
                "version": "1.0",
                "repo": "anoneysec/ai-agent-server",
                "time": datetime.now().isoformat(),
                "cwd": os.getcwd(),
                "user": os.getenv("USER", "unknown"),
                "token_required": True,
                "endpoints": {
                    "GET /status": "Check server status",
                    "POST /exec": "Run shell command",
                    "GET /run?cmd=...": "Quick command execution"
                }
            })
        elif path == "/run":
            query = urllib.parse.parse_qs(parsed.query)
            cmd = query.get("cmd", [""])[0]
            if cmd:
                self._execute_command(cmd)
            else:
                self._send_json({"error": "Missing cmd parameter"}, 400)
        else:
            self._send_json({"error": "Endpoint not found"}, 404)

    def do_POST(self):
        if not self._check_auth():
            self._send_json({"error": "Unauthorized - Invalid or missing token"}, 401)
            return

        if self.path == "/exec":
            content_length = int(self.headers.get("Content-Length", 0))
            post_data = self.rfile.read(content_length).decode("utf-8")

            command = None
            try:
                body = json.loads(post_data)
                command = body.get("command")
            except:
                pass

            if not command:
                parsed = urllib.parse.parse_qs(post_data)
                command = parsed.get("command", [""])[0]

            if command:
                self._execute_command(command)
            else:
                self._send_json({
                    "error": "No command provided",
                    "usage": {
                        "json": '{"command": "ls -la"}',
                        "form": "command=ls -la"
                    }
                }, 400)
        else:
            self._send_json({"error": "Only POST /exec is supported"}, 404)

    def _execute_command(self, command):
        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=45,
                cwd=os.getcwd()
            )
            response = {
                "success": result.returncode == 0,
                "command": command,
                "returncode": result.returncode,
                "stdout": result.stdout.strip(),
                "stderr": result.stderr.strip(),
                "timestamp": datetime.now().isoformat(),
                "cwd": os.getcwd()
            }
            self._send_json(response)
        except subprocess.TimeoutExpired:
            self._send_json({"error": "Command timed out after 45 seconds", "command": command}, 408)
        except Exception as e:
            self._send_json({"error": str(e), "command": command}, 500)

    def log_message(self, format, *args):
        print(f"[{datetime.now().strftime('%H:%M:%S')}] {self.client_address[0]} {format % args}")

if __name__ == "__main__":
    print("=" * 55)
    print("🤖 FULL ACCESS AI AGENT SERVER")
    print(f"   Repo: anoneysec/ai-agent-server")
    print(f"   Token: {AUTH_TOKEN}")
    print(f"   Running on: http://{HOST}:{PORT}")
    print("=" * 55)
    print("Examples:")
    print(f'  curl -H "Authorization: Bearer {AUTH_TOKEN}" http://localhost:{PORT}/status')
    print(f'  curl -X POST -H "Authorization: Bearer {AUTH_TOKEN}" -d "command=whoami" http://localhost:{PORT}/exec')
    print("=" * 55)

    with socketserver.TCPServer((HOST, PORT), AgentHandler) as httpd:
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nServer stopped.")
