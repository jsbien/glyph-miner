#!/bin/bash
set -e

SCRIPT_DIR="$(dirname "$0")"
KILL_SCRIPT="$SCRIPT_DIR/kill-uwsgi.sh"
UWSGI_SCRIPT="$SCRIPT_DIR/run-uwsgi.sh"

echo "🔄 Restarting uwsgi on 127.0.0.1:9091..."

if ! "$KILL_SCRIPT"; then
  echo "⚠️ Warning: Failed to kill existing uwsgi processes (maybe none running)"
fi

echo "🚀 Launching new uwsgi via run-uwsgi.sh..."
"$UWSGI_SCRIPT" &

echo "⏳ Waiting for server on port 9090..."
for i in {1..10}; do
  if curl -s http://localhost:9090/ >/dev/null 2>&1; then
    echo "✅ Server is up!"
    exit 0
  fi
  sleep 1
done

echo "❌ Server did not respond in time."
exit 1
