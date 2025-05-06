#!/bin/bash

# Activate virtualenv if needed
source ~/git/glyph-miner/uwsgi-env/bin/activate

# Run uwsgi using HTTP protocol on port 9092 for isolated backend testing
uwsgi --http 127.0.0.1:9092 \
      --chdir /home/jsbien/git/glyph-miner \
      --pythonpath /home/jsbien/git/glyph-miner \
      --module server.server:application \
      --master --processes 1 --threads 2 \
      --py-autoreload 1 \
      --logto /tmp/uwsgi-http-$(date +%Y%m%d-%H%M%S).log
