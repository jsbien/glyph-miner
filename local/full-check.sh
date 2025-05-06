#!/bin/bash

set -e

echo ">>> Running POST test..."
python3 local/post-check.py
POST_STATUS=$?

if [ $POST_STATUS -ne 0 ]; then
  echo "❌ POST check failed. Exiting."
  exit 1
fi

echo ">>> Running GET test..."
python3 local/test_get_collections.py
GET_STATUS=$?

if [ $GET_STATUS -ne 0 ]; then
  echo "❌ GET check failed. Exiting."
  exit 2
fi

echo "✅ All checks passed."
