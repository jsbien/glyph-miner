#!/bin/bash

# Start MySQL
service mysql start
sleep 5

# Start nginx
service nginx start

# Set correct PYTHONPATH
export PYTHONPATH=/opt/glyph-miner:$PYTHONPATH

# Start uwsgi properly
# uwsgi --http :9090 --chdir /opt/glyph-miner --module server.server:app
# uwsgi --http :9090 --chdir /opt/glyph-miner --module server.server:application
# uwsgi --http :9090 --chdir /opt/glyph-miner --module server.server:application --catch-exceptions --py-autoreload 1 --honour-stdin
uwsgi --http :9090 --chdir /opt/glyph-miner --module server.server:app --catch-exceptions --py-autoreload 1 --honour-stdin
