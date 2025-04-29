#!/bin/bash

# Create timestamped logfile in current directory
timestamp=$(date +"%Y%m%d-%H%M%S")
logfile="uwsgi-$timestamp.log"

echo "Logging to $logfile"
echo "Ctrl+C to stop."

# Run uwsgi with timestamped log and show print() output
uwsgi --socket 127.0.0.1:9091 \
      --protocol uwsgi \
      --chdir /home/jsbien/git/glyph-miner \
      --pythonpath /home/jsbien/git/glyph-miner/server \
      --module server.server:app \
      --master --processes 1 --threads 2 \
      --py-autoreload 1 \
      --logto uwsgi-$(date +%Y%m%d-%H%M%S).log
