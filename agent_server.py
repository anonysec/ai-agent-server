#!/usr/bin/env python3
"""
AI Agent Server - Full shell access via curl + MCP Structured Tools
Repo: anonysec/ai-agent-server
"""
import http.server
import socketserver
import json
import subprocess
import os
import urllib.parse
from datetime import datetime
import glob

PORT = 8080
HOST = "0.0.0.0"
AUTH_TOKEN = "8855"

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
                "message": "AI Agent Server running (with MCP capability)",
                "repo": "anonysec/ai-agent-server",
                "time": datetime.now().isoformat(),
                "cwd": os.getcwd(),
                "endpoints": ["/status", "/run", "/exec", "/mcp"]
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
        
        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length).decode("utf-8") if length > 0 else ""

        if self.path == "/exec":
            cmd = None
            try: cmd = json.loads(body).get("command")
            except: pass
            if not cmd:
                cmd = urllib.parse.parse_qs(body).get("command", [""])[0]
            if cmd: self._execute(cmd)
            else: self._send_json({"error": "No command provided"}, 400)
            return

        elif self.path == "/mcp":
            try:
                payload = json.loads(body)
            except Exception as e:
                self._send_json({"error": f"Invalid JSON: {str(e)}"}, 400)
                return
            
            # Support MCP JSON-RPC style or simple tool calling
            method = payload.get("method")
            tool_name = payload.get("tool")
            args = payload.get("args") or payload.get("arguments") or {}

            if method == "tools/list" or tool_name == "list_tools":
                self._send_json(self._get_tool_definitions())
                return
            elif method == "tools/call":
                params = payload.get("params", {})
                tool_name = params.get("name")
                args = params.get("arguments", {})

            if not tool_name:
                self._send_json({"error": "Missing tool name or method"}, 400)
                return

            result = self._handle_mcp_tool(tool_name, args)
            self._send_json(result)
            return

        else:
            self._send_json({"error": "Endpoint not found. Use POST /exec or POST /mcp"}, 404)

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

    def _get_tool_definitions(self):
        return {
            "tools": [
                {
                    "name": "list_dir",
                    "description": "List files and directories compactly without terminal formatting noise.",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "path": {"type": "string", "default": "."},
                            "max_items": {"type": "integer", "default": 50}
                        }
                    }
                },
                {
                    "name": "read_file",
                    "description": "Read specific line ranges of a file with line numbers, avoiding full file dumps into context.",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "path": {"type": "string"},
                            "start_line": {"type": "integer", "default": 1},
                            "end_line": {"type": "integer", "default": 100},
                            "max_lines": {"type": "integer", "default": 100}
                        },
                        "required": ["path"]
                    }
                },
                {
                    "name": "edit_file",
                    "description": "Precisely replace old_text with new_text in a file without shell escaping errors.",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "path": {"type": "string"},
                            "old_text": {"type": "string"},
                            "new_text": {"type": "string"}
                        },
                        "required": ["path", "old_text", "new_text"]
                    }
                },
                {
                    "name": "file_info",
                    "description": "Get metadata (bytes, lines, mtime) before reading a file.",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "path": {"type": "string"}
                        },
                        "required": ["path"]
                    }
                },
                {
                    "name": "exec_command",
                    "description": "Run shell command with optional working directory and output truncation to save tokens.",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "command": {"type": "string"},
                            "cwd": {"type": "string"},
                            "max_chars": {"type": "integer", "default": 1500}
                        },
                        "required": ["command"]
                    }
                }
            ]
        }

    def _handle_mcp_tool(self, name, args):
        try:
            if name == "list_dir":
                path = args.get("path", ".")
                max_items = args.get("max_items", 50)
                if not os.path.exists(path):
                    return {"success": False, "error": f"Path not found: {path}"}
                items = []
                for entry in os.scandir(path):
                    items.append({
                        "name": entry.name,
                        "type": "dir" if entry.is_dir() else "file",
                        "size": entry.stat().st_size if entry.is_file() else 0
                    })
                    if len(items) >= max_items:
                        break
                items.sort(key=lambda x: (x["type"] != "dir", x["name"]))
                return {"success": True, "path": path, "count": len(items), "items": items}

            elif name == "read_file":
                path = args.get("path")
                start = max(1, int(args.get("start_line", 1)))
                end = int(args.get("end_line", 100))
                max_lines = int(args.get("max_lines", 100))
                if not os.path.exists(path):
                    return {"success": False, "error": f"File not found: {path}"}
                with open(path, "r", errors="replace") as f:
                    lines = f.readlines()
                total_lines = len(lines)
                end = min(total_lines, end, start + max_lines - 1)
                selected = lines[start-1:end]
                content = "".join([f"{start + i} | {line}" for i, line in enumerate(selected)])
                truncated = end < total_lines
                return {
                    "success": True,
                    "path": path,
                    "total_lines": total_lines,
                    "range": f"{start}-{end}",
                    "truncated": truncated,
                    "content": content
                }

            elif name == "edit_file":
                path = args.get("path")
                old_text = args.get("old_text", "")
                new_text = args.get("new_text", "")
                if not os.path.exists(path):
                    return {"success": False, "error": f"File not found: {path}"}
                with open(path, "r", errors="replace") as f:
                    content = f.read()
                if old_text not in content:
                    return {"success": False, "error": "old_text not found in file."}
                new_content = content.replace(old_text, new_text, 1)
                with open(path, "w") as f:
                    f.write(new_content)
                return {"success": True, "path": path, "message": "File edited successfully."}

            elif name == "file_info":
                path = args.get("path")
                if not os.path.exists(path):
                    return {"success": False, "error": f"Path not found: {path}"}
                stat = os.stat(path)
                lines = 0
                if os.path.isfile(path):
                    with open(path, "rb") as f:
                        lines = sum(1 for _ in f)
                return {
                    "success": True,
                    "path": path,
                    "is_file": os.path.isfile(path),
                    "size_bytes": stat.st_size,
                    "lines": lines,
                    "modified": datetime.fromtimestamp(stat.st_mtime).isoformat()
                }

            elif name == "exec_command":
                command = args.get("command")
                cwd = args.get("cwd") or os.getcwd()
                max_chars = int(args.get("max_chars", 1500))
                r = subprocess.run(command, shell=True, capture_output=True, text=True, cwd=cwd, timeout=45)
                stdout = r.stdout.strip()
                stderr = r.stderr.strip()
                stdout_trunc = False
                stderr_trunc = False
                if len(stdout) > max_chars:
                    stdout = stdout[:max_chars] + f"\n... [Truncated {len(stdout)-max_chars} bytes]"
                    stdout_trunc = True
                if len(stderr) > max_chars:
                    stderr = stderr[:max_chars] + f"\n... [Truncated {len(stderr)-max_chars} bytes]"
                    stderr_trunc = True
                return {
                    "success": r.returncode == 0,
                    "exit_code": r.returncode,
                    "cwd": cwd,
                    "command": command,
                    "stdout": stdout,
                    "stderr": stderr,
                    "stdout_truncated": stdout_trunc,
                    "stderr_truncated": stderr_trunc
                }

            else:
                return {"success": False, "error": f"Unknown tool: {name}"}

        except Exception as e:
            return {"success": False, "error": str(e)}

if __name__ == "__main__":
    print(f"AI Agent Server started (token: {AUTH_TOKEN})")
    socketserver.TCPServer((HOST, PORT), AgentHandler).serve_forever()
