#!/bin/bash

# Start MySQL
service mysql start
sleep 5

# Start nginx
service nginx start

# Add server/ folder to PYTHONPATH
export PYTHONPATH=/opt/glyph-miner/server:$PYTHONPATH

# Start uwsgi server
uwsgi --http :9090 --wsgi-file server/server.py --callable app
