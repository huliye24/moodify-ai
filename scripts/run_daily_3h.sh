#!/usr/bin/env bash
set -e
cd ~/moodify-o3is
export PYTHONPATH=.
source .venv/bin/activate

echo "===== Moodify Daily Run 3H Test START ====="
date

echo "[1/6] register samples"
python3 -m moodify_runtime.cli --config configs/runtime_config.json register --source daily_input

echo "[2/6] plan queue"
python3 -m moodify_runtime.cli --config configs/runtime_config.json plan

echo "[queue lines]"
wc -l data/moodify_runtime/run_queue.jsonl || true

echo "[3/6] run pending tasks"
python3 -m moodify_runtime.cli --config configs/runtime_config.json run

echo "[4/6] generate report"
python3 -m moodify_runtime.cli --config configs/runtime_config.json report

echo "[5/6] generate craft memory"
python3 -m moodify_runtime.cli --config configs/runtime_config.json craft

echo "[6/6] next plan"
python3 -m moodify_runtime.cli --config configs/runtime_config.json next

date
echo "===== Moodify Daily Run 3H Test FINISH ====="
