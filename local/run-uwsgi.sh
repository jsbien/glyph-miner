#!/bin/bash
# Save PID to file
echo $$ > /tmp/uwsgi-wrapper.pid

# Create timestamped logfile in current directory
timestamp=$(date +"%Y%m%d-%H%M%S")
logfile="uwsgi-$timestamp.log"

echo "Logging to $logfile"
echo "Ctrl+C to stop."

# Run uWSGI with a timestamped log file (captures print() and error output)
exec /home/jsbien/git/glyph-miner/uwsgi-env/bin/uwsgi \
  --socket 127.0.0.1:9091 \
  --protocol uwsgi \
  --chdir /home/jsbien/git/glyph-miner \
  --pythonpath /home/jsbien/git/glyph-miner \
  --module server.server:application \
  --master \
  --processes 1 \
  --threads 2 \
  --logto uwsgi-$(date +%Y%m%d-%H%M%S).log

