# 🤖 AI Agent Server - Examples

## Install
```bash
bash <(curl -s https://raw.githubusercontent.com/anonysec/ai-agent-server/main/install.sh) 8844
```

## Check Server Status
```bash
curl -H "Authorization: Bearer 8844" http://IP:8080/status
```

---

## Method 1: Raw Shell Execution (`POST /exec`)
Use this for unbounded terminal command execution, custom piping, or system administration tasks.

### Run a bash command
```bash
curl -X POST -H "Authorization: Bearer 8844" \
  -d 'command=ls -la /var/log && uptime' \
  http://IP:8080/exec
```

### Check git status in a directory
```bash
curl -X POST -H "Authorization: Bearer 8844" \
  -d 'command=cd /root/project && git status' \
  http://IP:8080/exec
```

---

## Method 2: Structured MCP Tools (`POST /mcp`)
Use this for **token-efficient, high-reliability** AI agent workflows. Reduces context consumption by up to 85% on large files and prevents syntax escaping errors.

### List available tools & JSON schemas
```bash
curl -X POST -H "Authorization: Bearer 8844" \
  -d '{"tool": "list_tools"}' \
  http://IP:8080/mcp
```

### 1. List directory cleanly (without terminal noise)
```bash
curl -X POST -H "Authorization: Bearer 8844" \
  -d '{"tool": "list_dir", "args": {"path": ".", "max_items": 30}}' \
  http://IP:8080/mcp
```

### 2. Get file info (size, line count, modified timestamp)
```bash
curl -X POST -H "Authorization: Bearer 8844" \
  -d '{"tool": "file_info", "args": {"path": "agent_server.py"}}' \
  http://IP:8080/mcp
```

### 3. Read specific line ranges (saves 80-95% tokens on large files)
```bash
curl -X POST -H "Authorization: Bearer 8844" \
  -d '{"tool": "read_file", "args": {"path": "agent_server.py", "start_line": 10, "end_line": 30}}' \
  http://IP:8080/mcp
```

### 4. Edit a file precisely (no bash sed/awk escaping required)
```bash
curl -X POST -H "Authorization: Bearer 8844" \
  -d '{"tool": "edit_file", "args": {"path": "agent_server.py", "old_text": "PORT = 8080", "new_text": "PORT = 9090"}}' \
  http://IP:8080/mcp
```

### 5. Execute command with automatic output truncation (prevents log flooding)
```bash
curl -X POST -H "Authorization: Bearer 8844" \
  -d '{"tool": "exec_command", "args": {"command": "find / -name \"*.log\"", "max_chars": 1000}}' \
  http://IP:8080/mcp
```

---

## Uninstall
```bash
bash <(curl -s https://raw.githubusercontent.com/anonysec/ai-agent-server/main/install.sh) uninstall
```
