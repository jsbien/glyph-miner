#!/bin/bash
set -ex


# start mysqld and set up database
echo "Starting mysql"
/usr/sbin/mysqld &
sleep 10
#echo "CREATE DATABASE glyphminer" | mysql --default-character-set=utf8
echo CREATE DATABASE IF NOT EXISTS glyphminer | mysql --default-character-set=utf8
#echo "GRANT USAGE ON *.* TO glyphminer@localhost IDENTIFIED BY 'glyphminer'" | mysql --default-character-set=utf8
mysql --default-character-set=utf8 -e "CREATE USER IF NOT EXISTS 'glyphminer'@'localhost' IDENTIFIED WITH mysql_native_password BY 'glyphminer';"
#echo "GRANT ALL PRIVILEGES ON glyphminer.* TO glyphminer@localhost" | mysql --default-character-set=utf8
mysql --default-character-set=utf8 -e "GRANT ALL PRIVILEGES ON glyphminer.* TO 'glyphminer'@'localhost'";
echo FLUSH PRIVILEGES | mysql --default-character-set=utf8

mysql --user=glyphminer --password=glyphminer --default-character-set=utf8 glyphminer < /opt/glyph-miner/server/schema.sql


# Start nginx
echo "[INFO] Starting nginx..."
#service nginx start
nginx -g 'daemon off;' &
echo "[INFO] Started nginx"

# Set correct PYTHONPATH
export PYTHONPATH=/opt/glyph-miner:$PYTHONPATH

# Start uWSGI in socket mode (like original)
echo "[INFO] Starting uWSGI..."
uwsgi --socket 127.0.0.1:9090 --chdir /opt/glyph-miner --module server.server:app --catch-exceptions --py-autoreload 1 --honour-stdin
