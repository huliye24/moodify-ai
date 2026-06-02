#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="${1:-$(pwd)}"
cd "$ROOT_DIR"

mkdir -p data/night_inputs data/moodify_runtime outputs/daily_runs reports/daily_runs logs configs

if [ ! -f configs/runtime_config.json ]; then
  cp configs/runtime_config.example.json configs/runtime_config.json
fi

chmod +x scripts/*.sh || true

echo "[Moodify Runtime] installed at: $ROOT_DIR"
echo "[Moodify Runtime] config: configs/runtime_config.json"
echo "[Moodify Runtime] put audio files into: data/night_inputs/"
