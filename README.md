# 🤖 AI Agent Server

**Full remote shell access via curl** (like SSH over HTTP).

**Repo:** [anonysec/ai-agent-server](https://github.com/anonysec/ai-agent-server)

## Install (Recommended)

```bash
bash <(curl -s https://raw.githubusercontent.com/anonysec/ai-agent-server/main/install.sh) 8844
```

## Files Included

| File | Description |
|------|-------------|
| `install.sh` | Fully automated installer (no prompts) |
| `agent_server.py` | The main agent |
| `run.sh` / `start.sh` | Helper scripts |
| `agent.service` | systemd auto-start file |
| `README.md` | This file |
| `examples.md` | More examples |

## Usage After Install

```bash
curl -H "Authorization: Bearer 8844" http://IP:8080/status

curl -X POST -H "Authorization: Bearer 8844" \
  -d 'command=whoami && uptime' http://IP:8080/exec
```

## Uninstall

```bash
bash <(curl -s https://raw.githubusercontent.com/anonysec/ai-agent-server/main/install.sh) uninstall
```

## Prompt

```bash
Use the AI Agent Server for any task requiring shell, files, or system access.

Rules:
• Inspect first.
• Never assume.
• Execute, don't describe.
• Minimize reads/writes.
• Verify changes.
• Never invent output.
• Report errors exactly.
• Avoid destructive actions.

Server/Token:

```
