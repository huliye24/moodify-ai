#!/usr/bin/env bash
set -euo pipefail

# 在 moodify-o3is 项目根目录执行：
#   bash scripts/run_night_once.sh

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

mkdir -p data/night_inputs outputs/night_runs logs

# 自动激活常见虚拟环境
if [ -f ".venv/bin/activate" ]; then
  source .venv/bin/activate
elif [ -f "venv/bin/activate" ]; then
  source venv/bin/activate
fi

CONFIG="${1:-configs/night_config.json}"

echo "[Moodify] root=$ROOT_DIR"
echo "[Moodify] config=$CONFIG"
echo "[Moodify] start=$(date '+%F %T')"

python3 workers/cloud_night_worker.py \
  --config "$CONFIG" \
  --resume

echo "[Moodify] finish=$(date '+%F %T')"
