#!/bin/bash
T=$(grep -oP 'AUTH_TOKEN = "\K[0-9]+' agent_server.py 2>/dev/null || echo "7722")
echo "Token: $T"
python3 agent_server.py
