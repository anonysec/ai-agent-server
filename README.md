# 🤖 AI Agent Server

**Full remote shell & structured tool access via curl** (like SSH over HTTP + MCP for AI Agents).

**Repo:** [anonysec/ai-agent-server](https://github.com/anonysec/ai-agent-server)

## ⚡ Install (Recommended)

```bash
bash <(curl -s https://raw.githubusercontent.com/anonysec/ai-agent-server/main/install.sh) 8844
```

## 📦 Files Included

| File | Description |
|---|---|
| `install.sh` | Fully automated installer (no prompts) |
| `agent_server.py` | Unified agent server supporting both `/exec` (Raw Shell) and `/mcp` (Structured Tools) |
| `run.sh` / `start.sh` | Helper scripts |
| `agent.service` | systemd auto-start file |
| `README.md` | This file |
| `examples.md` | Comprehensive usage examples |

---

## 🚀 Two Methods Available

This server supports **two distinct architectures** depending on your workflow requirements:

### Method 1: Raw Shell Execution (`POST /exec`)
Ideal for general system administration, custom bash pipelines, or raw terminal tasks.
* **Endpoint:** `POST http://IP:8080/exec`
* **Payload:** `{"command": "whoami && uptime"}`

### Method 2: Structured MCP Tools (`POST /mcp`) — ⭐ Recommended for AI Agents
Designed specifically for LLM tool calling. Drastically reduces token usage (by up to 85% on large files), prevents shell escaping/syntax bugs, and protects the context window from output flooding.
* **Endpoint:** `POST http://IP:8080/mcp`
* **Supported Tools:**
  * `list_tools`: Get JSON schemas for all available tools.
  * `list_dir`: Clean directory listing without verbose terminal formatting.
  * `file_info`: Check file size, line counts, and timestamps before reading.
  * `read_file`: Read specific line ranges (`start_line` to `end_line`) with line numbers.
  * `edit_file`: Exact string replacement (`old_text` -> `new_text`) without bash escaping.
  * `exec_command`: Run shell commands with persistent working directory tracking and automatic stdout/stderr truncation.

---

## 📖 Quick Usage

### Check Server Status
```bash
curl -H "Authorization: Bearer 8844" http://IP:8080/status
```

### Method 1 Example: Run Bash Command
```bash
curl -X POST -H "Authorization: Bearer 8844" \
  -d 'command=whoami && uptime' http://IP:8080/exec
```

### Method 2 Example: Token-Efficient File Read
```bash
curl -X POST -H "Authorization: Bearer 8844" \
  -d '{"tool": "read_file", "args": {"path": "agent_server.py", "start_line": 1, "end_line": 25}}' \
  http://IP:8080/mcp
```
*(See [examples.md](examples.md) for more comprehensive command workflows).*

---

## 💬 Prompts for AI Agents

Copy and paste one of these system prompts into your LLM client (Claude, ChatGPT, Cursor, or custom agents) to instruct the model on how to interact with your server efficiently.

### 🎯 Prompt A: Method 2 (Structured MCP Tools — Recommended)
```text
You have access to a remote server via a structured HTTP tool API (like MCP).
Server URL: http://IP:8080/mcp
Authorization Header: "Bearer <TOKEN>"

You can execute JSON POST requests to invoke tools:
1. `list_dir(path, max_items)`: List directory contents compactly.
2. `file_info(path)`: Get bytes, line count, and modification timestamp.
3. `read_file(path, start_line, end_line, max_lines)`: Read specific line ranges with line numbers. Always use this instead of dumping full files into context.
4. `edit_file(path, old_text, new_text)`: Replace exact text in a file without shell escaping errors.
5. `exec_command(command, cwd, max_chars)`: Run shell commands. Output is automatically truncated if it exceeds max_chars.
6. `list_tools()`: List all schemas.

Rules for Execution:
• Inspect directory and check `file_info` before reading large files.
• Minimize token usage by reading only the necessary line ranges (`start_line`/`end_line`).
• Use `edit_file` for modifications instead of bash `sed` or EOF scripts.
• Never assume system state; verify changes after making them.
• Report errors exactly as returned by the API.
```

### ⚡ Prompt B: Method 1 (Raw Shell `/exec`)
```text
You have full remote shell access to a server via an HTTP POST endpoint.
Server URL: http://IP:8080/exec
Authorization Header: "Bearer <TOKEN>"

Send commands via JSON payload: `{"command": "<your_bash_command>"}` or URL-encoded body `command=<your_bash_command>`.

Rules for Execution:
• Inspect before modifying. Check file existence and system state first.
• Never assume output. Chain commands safely (e.g., using `&&`).
• Minimize stdout/stderr output to prevent flooding the context window (e.g., use `head`, `tail`, or `grep` instead of dumping full logs or large files).
• When editing files, be cautious with bash quotation and escaping rules.
• Execute directly, do not just describe the steps. Verify all changes.
```

---

## 🛑 Uninstall

```bash
bash <(curl -s https://raw.githubusercontent.com/anonysec/ai-agent-server/main/install.sh) uninstall
```
