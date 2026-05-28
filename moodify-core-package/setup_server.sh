#!/bin/bash
# Setup moodify project on cloud server
set -e

cd /root/moodify-lab

# Find and copy moodify source to clean path
MOODIFY_SRC=$(find . -path '*/moodify/src/moodify' -type d 2>/dev/null | head -1)
echo "Found source: $MOODIFY_SRC"

if [ -n "$MOODIFY_SRC" ]; then
    mkdir -p src
    cp -r "$MOODIFY_SRC" src/
    echo "Source copied to src/moodify/"
fi

# Find and copy MOODIFY_INTENT.md to root
INTENT_FILE=$(find . -name 'MOODIFY_INTENT.md' 2>/dev/null | head -1)
echo "Found intent: $INTENT_FILE"
if [ -n "$INTENT_FILE" ]; then
    cp "$INTENT_FILE" ./MOODIFY_INTENT.md
    echo "Intent copied"
fi

# Copy requirements.txt and pyproject.toml
REQ_FILE=$(find . -name 'requirements.txt' -path '*/moodify/*' 2>/dev/null | head -1)
if [ -n "$REQ_FILE" ]; then
    cp "$REQ_FILE" ./requirements.txt
    echo "requirements.txt copied"
fi

TOML_FILE=$(find . -name 'pyproject.toml' -path '*/moodify/*' 2>/dev/null | head -1)
if [ -n "$TOML_FILE" ]; then
    cp "$TOML_FILE" ./pyproject.toml
    echo "pyproject.toml copied"
fi

# Copy tests
TEST_DIR=$(find . -path '*/moodify/tests' -type d 2>/dev/null | head -1)
if [ -n "$TEST_DIR" ]; then
    cp -r "$TEST_DIR" ./tests
    echo "Tests copied"
fi

# Copy CLI
CLI_FILE=$(find . -name 'cli.py' -path '*/moodify/src/moodify/*' 2>/dev/null | head -1)
if [ -n "$CLI_FILE" ]; then
    cp "$CLI_FILE" src/moodify/cli.py
    echo "CLI copied"
fi

echo "=== Final structure ==="
find . -maxdepth 4 -type f -not -name '*.tar.gz' | grep -v 'Moodify' | grep -v 'moodify_core' | sort
