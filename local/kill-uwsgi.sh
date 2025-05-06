#!/bin/bash
set -e

PORT="127.0.0.1:9091"
PIDFILE="/tmp/glyphminer-uwsgi.pid"

echo "🔍 Killing uwsgi bound to $PORT..."

# If we know the master PID from a pidfile (used with --pidfile), try that first
if [ -f "$PIDFILE" ]; then
    MASTER_PID=$(cat "$PIDFILE")
    if ps -p "$MASTER_PID" > /dev/null 2>&1; then
        echo "🔪 Sending SIGINT to PID $MASTER_PID"
        kill -INT "$MASTER_PID" || true
        sleep 2
    else
        echo "ℹ️ PID $MASTER_PID not active"
    fi
fi

# Ensure all related uwsgi processes are killed if PID tracking fails
UWSGI_PIDS=$(ps -eo pid,cmd | grep '[u]wsgi' | grep "$PORT" | awk '{print $1}')

if [ -n "$UWSGI_PIDS" ]; then
    for pid in $UWSGI_PIDS; do
        echo "🔪 Killing PID $pid"
        kill -INT "$pid" || true
    done
    sleep 2
else
    echo "ℹ️ No uwsgi processes found on $PORT"
fi

# Final check
if ps -eo cmd | grep '[u]wsgi' | grep "$PORT" > /dev/null; then
    echo "❌ uwsgi still running on $PORT"
    exit 1
else
    echo "✅ uwsgi terminated cleanly"
    exit 0
fi
