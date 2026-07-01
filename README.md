# 🤖 AI Agent Server

**Full SSH-like remote control for your server using simple `curl` commands.**

> **Repo:** [anonysec/ai-agent-server](https://github.com/anonysec/ai-agent-server)

The AI (or you) can execute **any shell command** on the machine — just like SSH, but via HTTP + 4-digit token.

---

## ✨ Features

- Full shell access via HTTP (`curl`)
- 4-digit token authentication
- Auto-start on boot (systemd)
- One-command installer + uninstall
- Works great with AI agents (Claude, GPT, etc.)
- JSON + form support
- Pure Python (no dependencies)

---

## 🚀 One-Line Installation

```bash
# Default token (7722)
curl -fsSL https://raw.githubusercontent.com/anonysec/ai-agent-server/main/install.sh | bash

# With your own 4-digit token
curl -fsSL https://raw.githubusercontent.com/anonysec/ai-agent-server/main/install.sh | bash -s -- 8847
```

**Local install (from zip):**
```bash
bash install.sh 7722
```

---

## 🛠️ Usage

### Check status
```bash
curl -H "Authorization: Bearer 7722" http://YOUR_IP:8080/status
```

### Run any command (like SSH)
```bash
curl -X POST \
  -H "Authorization: Bearer 7722" \
  -d 'command=whoami && pwd && uptime && ls -la' \
  http://YOUR_IP:8080/exec
```

### JSON style (recommended)
```bash
curl -X POST \
  -H "Authorization: Bearer 7722" \
  -H "Content-Type: application/json" \
  -d '{"command": "df -h && free -h"}' \
  http://YOUR_IP:8080/exec
```

---

## 🔄 Auto-Start (Enabled by Default)

The installer automatically:
- Creates a systemd service
- Enables it to start on boot
- Starts the agent immediately

**Check service status:**
```bash
sudo systemctl status ai-agent-server
```

**View logs:**
```bash
tail -f ~/ai-agent-server/agent.log
```

---

## 🗑️ Uninstall + Revoke Token

Completely removes the agent and stops auto-start:

```bash
# Using curl
curl -fsSL https://raw.githubusercontent.com/anonysec/ai-agent-server/main/install.sh | bash -s -- uninstall

# Or locally
bash install.sh uninstall
```

This will:
- Stop the service
- Disable auto-start
- Delete all files
- Revoke the current token

---

## 📦 Manual Installation

1. Download the latest release or clone the repo
2. Run the installer:
   ```bash
   bash install.sh 7722
   ```

---

## 🔐 Security

- **Token is required** for every request (`Authorization: Bearer XXXX`)
- Only use on trusted networks or behind a VPN
- Change the token immediately after installation
- Consider firewall rules (only allow your IP)

To change token manually:
```bash
cd ~/ai-agent-server
sed -i 's/AUTH_TOKEN = "[0-9]*"/AUTH_TOKEN = "NEW_TOKEN"/' agent_server.py
sudo systemctl restart ai-agent-server
```

---

## 📁 Project Structure

```
ai-agent-server/
├── agent_server.py     # Main agent
├── install.sh          # One-line installer + uninstaller
├── run.sh              # Helper start script
├── agent.service       # systemd service file
├── README.md
└── examples.md
```

---

## 🪟 Windows / WSL

The server works on Linux. For Windows, use WSL2 or run the Python script directly.

---

## 📌 Give to an AI

Copy this to any AI:

> You have full SSH-like access to my server.
> 
> Base URL: `http://YOUR_IP:8080`
> Token: `7722`
> 
> Always send this header:
> `Authorization: Bearer 7722`
> 
> Run commands like this:
> ```bash
> curl -X POST -H "Authorization: Bearer 7722" \
>   -d 'command=YOUR_COMMAND_HERE' \
>   http://YOUR_IP:8080/exec
> ```

---

## 📄 License

MIT

---

**Made for AI agents and power users who want simple remote shell access via curl.**
