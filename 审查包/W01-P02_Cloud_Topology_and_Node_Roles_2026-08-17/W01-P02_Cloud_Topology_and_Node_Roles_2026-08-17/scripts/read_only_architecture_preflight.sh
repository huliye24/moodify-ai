#!/usr/bin/env bash
# W01-P02 read-only architecture preflight.
# Does not change infrastructure.

set -u

echo "===== P02 ARCHITECTURE PREFLIGHT ====="
date -Is 2>/dev/null || date

echo
echo "===== REPOSITORY ====="
git status --short --branch 2>/dev/null || true
git rev-parse HEAD 2>/dev/null || true

echo
echo "===== EXPECTED P00/P01 INPUT HINTS ====="
for pattern in \
  '*CLOUD_INFRASTRUCTURE_REALITY*' \
  '*MOODIFY_TRUTH_TABLE*' \
  '*CURRENT_SYSTEM_MAP*' \
  '*CURRENT_CANON*' \
  '*PRODUCT_BOUNDARY*' \
  '*CANON*ACCEPTANCE*'
do
  find . -maxdepth 5 -type f -iname "$pattern" -print 2>/dev/null | head -n 50
done

echo
echo "No changes performed."
