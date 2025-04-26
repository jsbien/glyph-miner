#!/bin/bash

echo "Starting mysql"
service mysql start

# Wait for MySQL to start up
sleep 5

# Create database and user
mysql -uroot -e "CREATE DATABASE IF NOT EXISTS glyphminer;"
mysql -uroot -e "CREATE USER IF NOT EXISTS 'glyphminer'@'localhost' IDENTIFIED WITH mysql_native_password BY 'glyphminer';"
mysql -uroot -e "GRANT ALL PRIVILEGES ON glyphminer.* TO 'glyphminer'@'localhost';"
mysql -uroot -e "FLUSH PRIVILEGES;"

echo "Starting nginx"
service nginx start

echo "Starting the python backend"
/usr/local/bin/uwsgi --http :9090 --chdir /opt --wsgi-file glyph-miner/wsgi.py --callable app --pythonpath /opt/glyph-miner/web --processes 2 --threads 2 --master


