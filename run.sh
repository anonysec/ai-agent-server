#!/bin/bash
TOKEN=$(grep -oP 'AUTH_TOKEN = "\K[0-9]+' agent_server.py 2>/dev/null || echo "7722")
echo "🚀 Starting AI Agent Server (anoneysec/ai-agent-server)"
echo "   Token: $TOKEN"
echo ""
echo "Test commands:"
echo "  curl -H \"Authorization: Bearer $TOKEN\" http://localhost:8080/status"
echo ""
python3 agent_server.py
