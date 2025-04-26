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
uwsgi --http :9090 --chdir /opt/glyph-miner --module server.server:application

