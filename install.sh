#!/bin/bash
#
# ========================================================
#  AI Agent Server - Full Auto Installer
#  Repo: anoneysec/ai-agent-server
# ========================================================
#
# Usage:
#   curl -fsSL https://raw.githubusercontent.com/anoneysec/ai-agent-server/main/install.sh | bash
#   curl -fsSL ... | bash -s -- 8847
#   bash install.sh 7722
#   bash install.sh uninstall
#

set -e

REPO="anoneysec/ai-agent-server"
INSTALL_DIR="$HOME/ai-agent-server"
SERVICE_NAME="ai-agent-server"
DEFAULT_TOKEN="7722"

# --- Handle uninstall ---
if [[ "$1" == "uninstall" ]]; then
    echo "🛑 Uninstalling AI Agent Server..."
    
    # Stop and disable service
    if command -v systemctl &> /dev/null; then
        sudo systemctl stop "$SERVICE_NAME" 2>/dev/null || true
        sudo systemctl disable "$SERVICE_NAME" 2>/dev/null || true
        sudo rm -f /etc/systemd/system/"$SERVICE_NAME".service
        sudo systemctl daemon-reload 2>/dev/null || true
    fi
    
    # Kill any running process
    pkill -f "agent_server.py" 2>/dev/null || true
    
    # Remove installation
    rm -rf "$INSTALL_DIR"
    
    echo "✅ Uninstalled successfully."
    echo "   (Token revoked - service stopped)"
    exit 0
fi

# --- Normal install ---

# Get token
if [ -n "$1" ] && [[ "$1" =~ ^[0-9]{4}$ ]]; then
    TOKEN="$1"
else
    read -p "Enter 4-digit token (default: $DEFAULT_TOKEN): " INPUT
    TOKEN="${INPUT:-$DEFAULT_TOKEN}"
fi

if ! [[ "$TOKEN" =~ ^[0-9]{4}$ ]]; then
    echo "⚠️  Invalid token. Using default: $DEFAULT_TOKEN"
    TOKEN="$DEFAULT_TOKEN"
fi

echo "=============================================="
echo "🤖 AI Agent Server Installer"
echo "   Repo: $REPO"
echo "   Token: $TOKEN"
echo "=============================================="

mkdir -p "$INSTALL_DIR"
cd "$INSTALL_DIR"

# Download from GitHub
GITHUB_RAW="https://raw.githubusercontent.com/$REPO/main"
GOT_FILES=false

echo ""
echo "📥 Downloading latest files..."

if curl -fsSL "$GITHUB_RAW/agent_server.py" -o agent_server.py 2>/dev/null; then
    curl -fsSL "$GITHUB_RAW/README.md" -o README.md 2>/dev/null || true
    curl -fsSL "$GITHUB_RAW/examples.md" -o examples.md 2>/dev/null || true
    GOT_FILES=true
    echo "✅ Downloaded from GitHub"
fi

# Fallback to local zip
if [ "$GOT_FILES" = false ]; then
    echo "📦 Using local files..."
    if [ -f "agent_server.py" ]; then
        echo "✅ Using existing files"
    else
        ZIP=""
        for p in "$HOME/ai-agent-server.zip" "./ai-agent-server.zip" "/tmp/ai-agent-server.zip" "$HOME/Downloads/ai-agent-server.zip"; do
            [ -f "$p" ] && ZIP="$p" && break
        done

        if [ -n "$ZIP" ]; then
            echo "📦 Extracting $ZIP..."
            rm -rf /tmp/ai-tmp
            unzip -o "$ZIP" -d /tmp/ai-tmp >/dev/null 2>&1 || true
            if [ -d /tmp/ai-tmp/ai-agent-server ]; then
                cp -r /tmp/ai-tmp/ai-agent-server/* .
            else
                cp -r /tmp/ai-tmp/* .
            fi
            rm -rf /tmp/ai-tmp
        else
            echo "❌ Could not find source. Please run from extracted folder."
            exit 1
        fi
    fi
fi

# Patch token
echo "🔐 Setting token to $TOKEN..."
sed -i "s/AUTH_TOKEN = \"[0-9]\{4\}\"/AUTH_TOKEN = \"$TOKEN\"/" agent_server.py 2>/dev/null || true
sed -i "s/AUTH_TOKEN = '[0-9]\{4\}'/AUTH_TOKEN = '$TOKEN'/" agent_server.py 2>/dev/null || true

chmod +x agent_server.py 2>/dev/null || true

# Create run scripts
cat > run.sh << 'RUN'
#!/bin/bash
TOKEN=$(grep -oP 'AUTH_TOKEN = "\K[0-9]+' agent_server.py 2>/dev/null || echo "7722")
echo "🚀 Starting AI Agent Server (anoneysec/ai-agent-server)"
echo "   Token: $TOKEN"
echo ""
echo "Test commands:"
echo "  curl -H \"Authorization: Bearer $TOKEN\" http://localhost:8080/status"
echo ""
python3 agent_server.py
RUN
chmod +x run.sh

cat > start.sh << 'START'
#!/bin/bash
python3 agent_server.py
START
chmod +x start.sh

# Create systemd service
echo "⚙️  Creating systemd service..."
cat > "$SERVICE_NAME.service" << SERV
[Unit]
Description=Full Access AI Agent Server (anoneysec/ai-agent-server)
After=network.target

[Service]
Type=simple
User=$(whoami)
WorkingDirectory=$(pwd)
ExecStart=/usr/bin/env python3 $(pwd)/agent_server.py
Restart=always
RestartSec=5
StandardOutput=append:$(pwd)/agent.log
StandardError=append:$(pwd)/agent.log

[Install]
WantedBy=multi-user.target
SERV

# Install and enable service
echo "🚀 Installing and enabling auto-start..."
sudo cp "$SERVICE_NAME.service" /etc/systemd/system/ 2>/dev/null || {
    echo "⚠️  Could not copy service file (no sudo). Starting manually..."
}

if command -v systemctl &> /dev/null; then
    sudo systemctl daemon-reload 2>/dev/null || true
    sudo systemctl enable "$SERVICE_NAME" 2>/dev/null || true
    sudo systemctl start "$SERVICE_NAME" 2>/dev/null || true
    echo "✅ Service enabled and started (auto-start on boot)"
else
    echo "⚠️  systemd not found. Starting manually..."
fi

# Start immediately if not using systemd
if ! systemctl is-active --quiet "$SERVICE_NAME" 2>/dev/null; then
    echo "▶️  Starting server in background..."
    nohup python3 agent_server.py > agent.log 2>&1 &
    sleep 1
fi

echo ""
echo "=============================================="
echo "✅ Installation Complete & Running!"
echo "=============================================="
echo ""
echo "📍 Installed to : $INSTALL_DIR"
echo "🔑 Token        : $TOKEN"
echo "🔄 Auto-start   : Enabled (systemd)"
echo ""
echo "📊 Status:"
echo "   curl -H \"Authorization: Bearer $TOKEN\" http://localhost:8080/status"
echo ""
echo "📌 Run command:"
echo "   curl -X POST -H \"Authorization: Bearer $TOKEN\" \\"
echo "        -d 'command=whoami && uptime' http://localhost:8080/exec"
echo ""
echo "🛑 To uninstall + revoke token:"
echo "   curl -fsSL https://raw.githubusercontent.com/$REPO/main/install.sh | bash -s -- uninstall"
echo "   # or"
echo "   bash install.sh uninstall"
echo ""
echo "📜 Logs:"
echo "   tail -f $INSTALL_DIR/agent.log"
echo ""
echo "=============================================="
