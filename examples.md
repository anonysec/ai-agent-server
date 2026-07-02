# Examples

## Install
bash <(curl -s https://raw.githubusercontent.com/anonysec/ai-agent-server/main/install.sh) 8844

## Test
curl -H "Authorization: Bearer 8844" http://IP:8080/status

curl -X POST -H "Authorization: Bearer 8844" -d 'command=ls -la' http://IP:8080/exec

## Uninstall
bash <(curl -s https://raw.githubusercontent.com/anonysec/ai-agent-server/main/install.sh) uninstall
