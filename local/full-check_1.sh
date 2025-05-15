#!/bin/bash

VERSION="full_check_1.sh v1.0"
LOG_FILE="test-$(date +'%Y%m%d-%H%M%S').log"

# Log to both file and console
echo "📄 Logging to: $LOG_FILE"
exec > >(tee "$LOG_FILE") 2> >(tee -a "$LOG_FILE" >&2)

echo "🧪 $VERSION"
echo "🕒 $(date +'%Y-%m-%d %H:%M:%S')"
echo "🔢 Commit: $(git rev-parse --short HEAD)"

# 🧠 Ensure Node.js is available (via nvm)
export NVM_DIR="$HOME/.nvm"
if [ -s "$NVM_DIR/nvm.sh" ]; then
  source "$NVM_DIR/nvm.sh"
else
  echo "❌ NVM not found"
  exit 1
fi

# 🔢 Get full path to node binary
NODE_BIN=$(nvm which node)
if [ ! -x "$NODE_BIN" ]; then
  echo "❌ node binary not found or not executable"
  exit 1
fi
echo "🟢 Node: $NODE_BIN"
echo "🟢 Node version: $("$NODE_BIN" --version)"

# Clean stale .pyc files before starting anything
echo "🧹 Cleaning up stale .pyc files..."
find server/ -name '*.pyc' -delete

# 🔁 Restart the server
echo "🔁 Restarting server..."
local/restart-server.sh || {
  echo "❌ Server restart failed"
  exit 1
}

# Check if the ping endpoint responds correctly after restart
echo "📡 Verifying uwsgi restart via /api/ping..."
curl -s -w "\nHTTP Status: %{http_code}\n" http://localhost:9090/api/ping

# Add ping test to confirm server is up
echo "📶 Pinging server..."
curl -s -o /dev/null -w "%{http_code}" http://localhost:9090/api/ping | grep -q 200
if [ $? -eq 0 ]; then
  echo "✅ Ping succeeded"
else
  echo "❌ Ping failed"
fi

# 🌐 HTML check
echo "🔍 Running HTML check..."
if ! "$NODE_BIN" local/html-check.js http://localhost:9090; then
  echo "❌ HTML test failed"
  HTML_RESULT=1
else
  echo "✅ HTML test passed"
  HTML_RESULT=0
fi

# 🧹 Clear old collections via debug API
echo "🧹 Clearing collections table..."
if ! curl -X POST -s http://localhost:9090/api/debug/clear > /dev/null; then
  echo "❌ Failed to clear collections via debug endpoint"
else
  echo "✅ Collections cleared"
fi

# 📡 POST check
echo "📡 Running POST check..."
if ! python3 local/post-check.py http://localhost:9090/api/collections; then
  echo "❌ POST test failed"
  POST_RESULT=1
else
  echo "✅ POST test passed"
  POST_RESULT=0
fi

# 📡 GET check
echo "📡 Running GET check..."
if ! python3 local/test_get_collections.py; then
  echo "❌ GET test failed"
  GET_RESULT=1
else
  echo "✅ GET test passed"
  GET_RESULT=0
fi

# 🧪 Batch upload test (new)
echo "🧪 Running batch_upload_pages_TEST.sh..."
if ! (cd utils && ./batch_upload_pages_TEST.sh); then
  echo "❌ Batch upload test failed"
  BATCH_RESULT=1
else
  echo "✅ Batch upload test passed"
  BATCH_RESULT=0
fi

# ✅ Final result
if [ "$HTML_RESULT" -eq 0 ] && [ "$POST_RESULT" -eq 0 ] && [ "$GET_RESULT" -eq 0 ] && [ "$BATCH_RESULT" -eq 0 ]; then
  echo "✅ All tests passed"
  exit 0
else
  echo "❌ One or more tests failed"
  exit 1
fi
