#!/bin/bash
set -e

# 自前の agent.conf をそのまま使用
AGENT_CONF="/opt/apache-flume/conf/agent.conf"

echo "Starting Cygnus with config: $AGENT_CONF"

# Cygnus を起動（root のままでも可）
exec /opt/apache-flume/bin/cygnus-flume-ng agent -f "$AGENT_CONF" -n cygnusagent
