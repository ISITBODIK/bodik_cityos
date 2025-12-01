#!/bin/bash

# EMQXノードが起動するまで待機する関数
wait_for_emqx_node() {
  echo "Waiting for EMQX node to start..."
  local timeout=60 # タイムアウトを60秒に設定
  local count=0
  # V4.4では emqx_ctl status でノードの状態を確認
  while ! /opt/emqx/bin/emqx_ctl status > /dev/null 2>&1; do
    if [ $count -ge $timeout ]; then
      echo "EMQX node did not start within $timeout seconds. Exiting."
      exit 1
    fi
    echo "EMQX node not yet ready. Retrying in 1 second..."
    sleep 1
    count=$((count+1))
  done
  echo "EMQX node is running."
}

# EMQXのメインプロセスをバックグラウンドで起動
echo "Starting EMQX in background..."
/opt/emqx/bin/emqx foreground &
EMQX_PID=$! # EMQXプロセスのPIDを保存

# EMQXノードが起動するまで待機
wait_for_emqx_node

# ここからプラグインのロードと有効化を実行

# V4.4でもプラグイン名にバージョンを含めません (例: emqx_auth_http)
EMQX_AUTH_HTTP_PLUGIN_NAME="emqx_auth_http"

# プラグインが既にロードされているかチェックし、なければロードする
# V4.4のログのUsageにもあるように `plugins list` を使うのが正しい
if ! /opt/emqx/bin/emqx_ctl plugins list | grep "$EMQX_AUTH_HTTP_PLUGIN_NAME" | grep -q "loaded"; then
  echo "Starting $EMQX_AUTH_HTTP_PLUGIN_NAME plugin..."
  # V4.4では `emqx_ctl plugins load <plugin_name>` の形式
  /opt/emqx/bin/emqx_ctl plugins load "$EMQX_AUTH_HTTP_PLUGIN_NAME"
  if [ $? -ne 0 ]; then
    echo "Failed to start $EMQX_AUTH_HTTP_PLUGIN_NAME. Exiting."
    kill $EMQX_PID
    exit 1
  fi
  echo "$EMQX_AUTH_HTTP_PLUGIN_NAME plugin started."
fi

# プラグインが自動起動に有効になっているかチェックし、有効でなければ有効にする
# V4.4では設定ファイル emqx.conf で有効化されますが、CLIからも可能です。
# plugins list の出力で "loaded" になっていれば起動しています。
# 自動起動設定は、emqx.conf の plugins.loaded_plugins にプラグイン名を追加します。
# シェルスクリプトでこれを直接操作するのは難しいので、ここでは起動済みの状態であればよしとします。
# もし自動起動が必要であれば、Dockerfileでemqx.confを修正してコピーする方が確実です。
# ただし、現在の目的は「プラグインを動かす」ことなので、`load` で起動できればOKです。
echo "Note: For EMQX 4.x, plugin auto-boot is typically configured in emqx.conf."
echo "If this plugin needs to be persistent across restarts, ensure it's added to plugins.loaded_plugins in /opt/emqx/etc/emqx.conf"

# V4.4では "enable" コマンドは直接存在しないか、他の意味合いを持つため、
# plugins load が成功すれば、そのセッションでは有効です。
# もし永続化したい場合は、emqx.conf を修正する必要があります。
# 一旦、`enable` のチェックと実行はスキップします。

echo "EMQX and plugins configured. Keeping EMQX running."
# EMQXプロセスが終了しないように待機
wait $EMQX_PID
