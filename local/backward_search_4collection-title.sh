#!/bin/bash

set -e

# Configuration
REPO_DIR="${1:-.}"
COMMIT_LIST="commit-list.txt"
LOGFILE="scan-history.log"
TEST_SCRIPT="./local/test_server.py"
# TEST_URL="http://localhost:9090/api/collections"  # optional if needed by test_server.py

echo "🔍 Scanning commits listed in: $COMMIT_LIST"
echo "📜 Logging results to: $LOGFILE"

cd "$REPO_DIR"
original_ref=$(git symbolic-ref --quiet --short HEAD 2>/dev/null || git rev-parse HEAD)

while read -r commit; do
  echo "🧹 Cleaning working tree..."
  git reset --hard
  git clean -fdx

  echo "⏳ Checking out $commit..."
  if ! git checkout "$commit" >/dev/null 2>&1; then
    echo "$commit CHECKOUT_FAIL" | tee -a "$LOGFILE"
    continue
  fi

  echo "📝 Commit: $commit - $(git log -1 --pretty=%s)"
  echo "🔬 Testing $commit..."

  set +e
  "$TEST_SCRIPT"
  exit_code=$?
  set -e

  if [ "$exit_code" -eq 0 ]; then
    echo "$commit PASS" | tee -a "$LOGFILE"
    echo "✅ Passing commit: $commit"
    break
  else
    echo "$commit FAIL" | tee -a "$LOGFILE"
  fi

done < "$COMMIT_LIST"

echo "🔁 Returning to original ref: $original_ref"
git checkout "$original_ref"
