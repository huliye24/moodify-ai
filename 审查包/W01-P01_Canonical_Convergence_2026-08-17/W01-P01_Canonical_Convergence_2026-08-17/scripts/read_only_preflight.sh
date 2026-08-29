#!/usr/bin/env bash
# W01-P01 read-only preflight.
# This script does not edit files.

set -u

echo "===== W01-P01 PRE-FLIGHT ====="
date -Is 2>/dev/null || date

echo
echo "===== GIT STATUS ====="
git status --short --branch || exit 1

echo
echo "===== HEAD ====="
git rev-parse HEAD || exit 1

echo
echo "===== ROOT AUTHORITY FILES ====="
for f in README.md AGENTS.md docs/REPOSITORY_STATUS.md docs/AUDITORY_INTELLIGENCE_ARCHITECTURE.md docs/ASSET_MODEL.md docs/LEGACY_AND_EXPERIMENTAL_POLICY.md; do
  if [ -f "$f" ]; then
    printf '\n--- %s ---\n' "$f"
    sed -n '1,80p' "$f"
  else
    printf '\nMISSING: %s\n' "$f"
  fi
done

echo
echo "===== HIGH-AUTHORITY IDENTITY PHRASES ====="
grep -RInE \
  --include='README.md' \
  --include='AGENTS.md' \
  --include='REPOSITORY_STATUS.md' \
  --include='*ARCHITECTURE*.md' \
  'The Ear of AI|Auditory Intelligence|Moodify Music|Moodify Player|PLAY' \
  . 2>/dev/null | head -n 300 || true

echo
echo "===== CANON DIR ====="
if [ -d docs/canon ]; then
  find docs/canon -maxdepth 2 -type f -print | sort
else
  echo "docs/canon: NOT PRESENT"
fi

echo
echo "Preflight complete. No files changed."
