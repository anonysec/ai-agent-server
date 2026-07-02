#!/usr/bin/env python3
"""
AI Agent Server - Full shell access via curl
Repo: anonysec/ai-agent-server
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
AUTH_TOKEN = "7722"

class AgentHandler(http.server.BaseHTTPRequestHandler):
    def _send_json(self, data, status=200):
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(data, indent=2, ensure_ascii=False).encode("utf-8"))

    def _check_auth(self):
        auth = self.headers.get("Authorization", "")
        if auth.startswith("Bearer "):
            return auth.replace("Bearer ", "").strip() == AUTH_TOKEN
        if "token=" in self.path:
            qs = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
            if qs.get("token", [""])[0] == AUTH_TOKEN:
                return True
        return False

    def do_GET(self):
        if not self._check_auth():
            self._send_json({"error": "Unauthorized"}, 401)
            return
        path = urllib.parse.urlparse(self.path).path
        if path in ("/", "/status"):
            self._send_json({
                "status": "ok",
                "message": "AI Agent Server running",
                "repo": "anonysec/ai-agent-server",
                "time": datetime.now().isoformat(),
                "cwd": os.getcwd()
            })
        elif path == "/run":
            cmd = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query).get("cmd", [""])[0]
            if cmd: self._execute(cmd)
            else: self._send_json({"error": "Missing cmd"}, 400)
        else:
            self._send_json({"error": "Not found"}, 404)

    def do_POST(self):
        if not self._check_auth():
            self._send_json({"error": "Unauthorized"}, 401)
            return
        if self.path != "/exec":
            self._send_json({"error": "Use POST /exec"}, 404)
            return
        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length).decode()
        cmd = None
        try: cmd = json.loads(body).get("command")
        except: pass
        if not cmd:
            cmd = urllib.parse.parse_qs(body).get("command", [""])[0]
        if cmd: self._execute(cmd)
        else: self._send_json({"error": "No command provided"}, 400)

    def _execute(self, command):
        try:
            r = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=45)
            self._send_json({
                "success": r.returncode == 0,
                "command": command,
                "stdout": r.stdout.strip(),
                "stderr": r.stderr.strip()
            })
        except Exception as e:
            self._send_json({"error": str(e)}, 500)

if __name__ == "__main__":
    print(f"AI Agent Server started (token: {AUTH_TOKEN})")
    socketserver.TCPServer((HOST, PORT), AgentHandler).serve_forever()
