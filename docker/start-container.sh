#!/bin/bash

# Start MySQL
service mysql start
sleep 5

# Start nginx
service nginx start

# Add server/ and server/web/ folders to PYTHONPATH
export PYTHONPATH=/opt/glyph-miner/server:/opt/glyph-miner/server/web:$PYTHONPATH

# Start uwsgi server
uwsgi --http :9090 --wsgi-file server/server.py --callable app
