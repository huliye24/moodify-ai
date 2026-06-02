#!/usr/bin/env bash
set -euo pipefail

# 上云后先跑这个，只处理 1 首 × 1 个 preset。
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

if [ -f ".venv/bin/activate" ]; then
  source .venv/bin/activate
elif [ -f "venv/bin/activate" ]; then
  source venv/bin/activate
fi

python3 workers/cloud_night_worker.py \
  --config configs/night_config.json \
  --smoke
