# Example Commands for the AI Agent

## Basic Usage (replace 2204 with your token)

### 1. Status
```bash
curl -H "Authorization: Bearer 2204" http://localhost:8080/status
```

### 2. Run commands
```bash
# Simple
curl -X POST -H "Authorization: Bearer 2204" -d "command=whoami" http://localhost:8080/exec

# Multiple commands
curl -X POST -H "Authorization: Bearer 2204" -d "command=ls -la && pwd" http://localhost:8080/exec

# JSON (recommended)
curl -X POST \
  -H "Authorization: Bearer 2204" \
  -H "Content-Type: application/json" \
  -d '{"command": "df -h && free -h"}' \
  http://localhost:8080/exec
```

### 3. Useful commands to give to AI

**System info**
```bash
curl -X POST -H "Authorization: Bearer 2204" -d "command=uname -a && whoami && pwd && date" http://localhost:8080/exec
```

**Install packages**
```bash
curl -X POST -H "Authorization: Bearer 2204" -d "command=sudo apt update && sudo apt install -y htop" http://localhost:8080/exec
```

**File operations**
```bash
curl -X POST -H "Authorization: Bearer 2204" -d "command=cat /etc/os-release" http://localhost:8080/exec
```

**Python execution**
```bash
curl -X POST -H "Authorization: Bearer 2204" -d 'command=python3 -c "import os; print(os.listdir(\".\"))"' http://localhost:8080/exec
```

## How to use with an AI

Tell the AI:

"You have full access to my server. Use this format every time:

curl -X POST \
  -H \"Authorization: Bearer 2204\" \
  -d \"command=YOUR_SHELL_COMMAND_HERE\" \
  http://YOUR_IP:8080/exec"
