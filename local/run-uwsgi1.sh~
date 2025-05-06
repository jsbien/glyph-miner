#!/bin/bash

# Run the glyph-miner backend using uwsgi
# This script expects to be run from the project root

uwsgi --socket 127.0.0.1:9091 \
      --protocol uwsgi \
      --chdir "$(dirname "$0")/.." \
      --module server.server:app \
      --master --processes 1 --threads 2 \
      --logto /tmp/uwsgi.log
