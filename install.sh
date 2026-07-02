#!/bin/bash
#
# AI Agent Server - Fully Automated Installer
# Repo: anonysec/ai-agent-server
#
# Exact usage:
#   bash <(curl -s https://raw.githubusercontent.com/anonysec/ai-agent-server/main/install.sh) 8844
#
# Uninstall:
#   bash <(curl -s https://raw.githubusercontent.com/anonysec/ai-agent-server/main/install.sh) uninstall
#

set -e

REPO="anonysec/ai-agent-server"
INSTALL_DIR="$HOME/ai-agent-server"
SERVICE_NAME="ai-agent-server"
DEFAULT_TOKEN="7722"

TOKEN="$DEFAULT_TOKEN"
ACTION="install"

if [[ "$1" == "uninstall" ]]; then
    ACTION="uninstall"
elif [[ "$1" =~ ^[0-9]{4}$ ]]; then
    TOKEN="$1"
elif [ -n "$1" ]; then
    echo "❌ Invalid argument: $1"
    echo "Usage: bash <(curl -s .../install.sh) 8844"
    exit 1
fi

if [ "$ACTION" = "uninstall" ]; then
    echo "🛑 Uninstalling..."
    if command -v systemctl &>/dev/null; then
        sudo systemctl stop "$SERVICE_NAME" 2>/dev/null || true
        sudo systemctl disable "$SERVICE_NAME" 2>/dev/null || true
        sudo rm -f /etc/systemd/system/"$SERVICE_NAME".service
        sudo systemctl daemon-reload 2>/dev/null || true
    fi
    pkill -f "agent_server.py" 2>/dev/null || true
    rm -rf "$INSTALL_DIR"
    echo "✅ Uninstalled. Token revoked."
    exit 0
fi

echo "=============================================="
echo "🤖 AI Agent Server - Automated Installer"
echo "   Repo: $REPO"
echo "   Token: $TOKEN"
echo "=============================================="

mkdir -p "$INSTALL_DIR"
cd "$INSTALL_DIR"

GITHUB_RAW="https://raw.githubusercontent.com/$REPO/main"
GOT_FILES=false

if curl -fsSL "$GITHUB_RAW/agent_server.py" -o agent_server.py 2>/dev/null; then
    curl -fsSL "$GITHUB_RAW/README.md" -o README.md 2>/dev/null || true
    GOT_FILES=true
    echo "✅ Downloaded from GitHub"
fi

if [ "$GOT_FILES" = false ]; then
    echo "📦 Using embedded version..."
    cat > agent_server.py << 'PYEOF'
#!/usr/bin/env python3
import http.server, socketserver, json, subprocess, os, urllib.parse
from datetime import datetime
PORT=8080; HOST="0.0.0.0"; AUTH_TOKEN="7722"
class H(http.server.BaseHTTPRequestHandler):
    def _j(self,d,s=200): self.send_response(s);self.send_header("Content-Type","application/json");self.end_headers();self.wfile.write(json.dumps(d,indent=2).encode())
    def _auth(self):
        a=self.headers.get("Authorization","")
        if a.startswith("Bearer "): return a.replace("Bearer ","").strip()==AUTH_TOKEN
        if "token=" in self.path: return urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query).get("token",[""])[0]==AUTH_TOKEN
        return False
    def do_GET(self):
        if not self._auth(): return self._j({"error":"Unauthorized"},401)
        p=urllib.parse.urlparse(self.path).path
        if p in ("/","/status"): self._j({"status":"ok","message":"AI Agent Server","repo":"anonysec/ai-agent-server"})
        elif p=="/run":
            c=urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query).get("cmd",[""])[0]
            if c: self._run(c)
            else: self._j({"error":"Missing cmd"},400)
        else: self._j({"error":"Not found"},404)
    def do_POST(self):
        if not self._auth(): return self._j({"error":"Unauthorized"},401)
        if self.path!="/exec": return self._j({"error":"Use /exec"},404)
        l=int(self.headers.get("Content-Length",0))
        b=self.rfile.read(l).decode()
        c=None
        try: c=json.loads(b).get("command")
        except: pass
        if not c: c=urllib.parse.parse_qs(b).get("command",[""])[0]
        if c: self._run(c)
        else: self._j({"error":"No command"},400)
    def _run(self,cmd):
        try:
            r=subprocess.run(cmd,shell=True,capture_output=True,text=True,timeout=45)
            self._j({"success":r.returncode==0,"stdout":r.stdout.strip(),"stderr":r.stderr.strip()})
        except Exception as e: self._j({"error":str(e)},500)
if __name__=="__main__": print(f"AI Agent Server started (token: {AUTH_TOKEN})"); socketserver.TCPServer((HOST,PORT),H).serve_forever()
PYEOF
fi

sed -i "s/AUTH_TOKEN = \"[0-9]\{4\}\"/AUTH_TOKEN = \"$TOKEN\"/" agent_server.py 2>/dev/null || true
chmod +x agent_server.py

cat > run.sh << 'R'
#!/bin/bash
T=$(grep -oP 'AUTH_TOKEN = "\K[0-9]+' agent_server.py 2>/dev/null || echo "7722")
echo "Token: $T"
python3 agent_server.py
R
chmod +x run.sh

cat > start.sh << 'S'
#!/bin/bash
python3 agent_server.py
S
chmod +x start.sh

cat > "$SERVICE_NAME.service" << SERV
[Unit]
Description=AI Agent Server (anonysec/ai-agent-server)
After=network.target
[Service]
Type=simple
User=$(whoami)
WorkingDirectory=$(pwd)
ExecStart=/usr/bin/env python3 $(pwd)/agent_server.py
Restart=always
RestartSec=5
[Install]
WantedBy=multi-user.target
SERV

echo "🚀 Enabling auto-start..."
if command -v systemctl &>/dev/null; then
    sudo cp "$SERVICE_NAME.service" /etc/systemd/system/ 2>/dev/null || true
    sudo systemctl daemon-reload 2>/dev/null || true
    sudo systemctl enable "$SERVICE_NAME" 2>/dev/null || true
    sudo systemctl start "$SERVICE_NAME" 2>/dev/null || true
    echo "✅ Auto-start enabled"
else
    nohup python3 agent_server.py > agent.log 2>&1 &
fi

echo ""
echo "✅ Installation Complete!"
echo "   Location : $INSTALL_DIR"
echo "   Token    : $TOKEN"
echo ""
echo "Test:"
echo "  curl -H \"Authorization: Bearer $TOKEN\" http://localhost:8080/status"
echo ""
echo "Uninstall:"
echo "  bash <(curl -s https://raw.githubusercontent.com/$REPO/main/install.sh) uninstall"
echo "=============================================="
