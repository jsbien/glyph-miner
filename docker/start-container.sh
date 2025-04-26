#!/bin/bash

# Start MySQL
service mysql start
sleep 5

# Start nginx
service nginx start

# Set correct PYTHONPATH
export PYTHONPATH=/opt/glyph-miner/server:/opt/glyph-miner/server/web:$PYTHONPATH

# Start uwsgi by module, not by file
uwsgi --http :9090 --module server.server:app
