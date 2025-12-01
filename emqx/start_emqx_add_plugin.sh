#!/bin/sh
set -e

# EMQX 起動
#/opt/emqx/bin/emqx foreground

# API 待機（初回登録用）
echo "Waiting for EMQX management API..."
while true; do
  HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:18083/api/v5/status || true)
  if [ "$HTTP_CODE" = "200" ]; then
    break
  fi
  echo "Waiting for EMQX API... (status $HTTP_CODE)"
  sleep 2
done

echo "EMQX started."

# APIキーからトークン取得
TOKEN=$(curl -s -X POST \
  -u "$MYEMQX_API_KEY:$MYEMQX_API_SECRET" \
  http://localhost:18083/api/v5/api_key/$MYEMQX_API_KEY/token | \
  sed -n 's/.*"token":"\([^"]*\)".*/\1/p')

echo "API key is active. Configuring HTTP Auth & ACL..."
echo "TOKEN is $TOKEN"

# ====== HTTP 認証の設定 ======
curl -s -X POST http://localhost:18083/api/v5/authentication \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "mechanism": "http",
    "enable": true,
    "config": {
      "url": "https://cityos_support:8080/mqtt/auth",
      "method": "post",
      "headers": {"content-type": "application/x-www-form-urlencoded"},
      "request_body": "clientid=%c&username=%u&password=%P",
      "connect_timeout": "5s",
      "timeout": "5s",
      "pool_size": 32,
      "enable_pipelining": 100
    }
  }'

echo "authentication OK"

# ====== HTTP ACL（Authorization）の設定 ======
curl -s -X POST http://localhost:18083/api/v5/authorization/sources \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "type": "http",
    "enable": true,
    "config": {
      "url": "https://cityos_support:8080/mqtt/acl",
      "method": "post",
      "headers": {"content-type": "application/x-www-form-urlencoded"},
      "request_body": "access=%A&username=%u&clientid=%c&topic=%t",
      "connect_timeout": "5s",
      "timeout": "5s",
      "pool_size": 32,
      "enable_pipelining": 100
    }
  }'

echo "authentication/source OK"
