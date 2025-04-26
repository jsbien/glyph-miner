#!/bin/bash

# Start MySQL
service mysql start
sleep 5

# Start nginx
service nginx start

# Start the uwsgi server manually
uwsgi --http :9090 --wsgi-file server/server.py --callable app
