#!/bin/bash
set -e

# Start MySQL
echo "[INFO] Starting MySQL..."
service mysql start
sleep 5

# Start nginx
echo "[INFO] Starting nginx..."
service nginx start

# Set correct PYTHONPATH
export PYTHONPATH=/opt/glyph-miner:$PYTHONPATH

# Start uWSGI in socket mode (like original)
echo "[INFO] Starting uWSGI..."
uwsgi --socket 127.0.0.1:9090 --chdir /opt/glyph-miner --module server.server:app --catch-exceptions --py-autoreload 1 --honour-stdin
