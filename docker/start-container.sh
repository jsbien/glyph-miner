#!/bin/bash

# Start MySQL
service mysql start
sleep 5

# Start nginx
service nginx start

# Set correct PYTHONPATH
export PYTHONPATH=/opt/glyph-miner/server:/opt/glyph-miner/server/web:$PYTHONPATH

# Start uwsgi by module and correct directory
uwsgi --http :9090 --chdir /opt/glyph-miner --module server.server:app
