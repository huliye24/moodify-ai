#!/usr/bin/env bash
set -e
cd ~/moodify-o3is
export PYTHONPATH=.
source .venv/bin/activate

echo "===== PREP: Copy real AI music to night_inputs ====="
echo "Source: 07Music/albums/"

# Count existing
BEFORE=0
echo "night_inputs before:  files"

# Move the loadtest_backup out of the way if exists
if [ -d data/night_inputs/loadtest_backup ]; then
    echo "loadtest_backup exists, will skip"
fi

# Copy ALL audio from 07Music/albums
COPIED=0
find ~/07Music/albums -type f \( -name "*.wav" -o -name "*.mp3" -o -name "*.flac" \) | while read src; do
    fname=""
    if [ ! -f "data/night_inputs/" ]; then
        cp "" "data/night_inputs/"
    fi
done

AFTER=0
echo "night_inputs after:  files"

echo ""
echo "===== Moodify Daily Run -- 100+ REAL AI SONGS ====="
date

echo "[1/6] register samples"
python3 -m moodify_runtime.cli --config configs/runtime_config.json register --source real_ai_20260602

echo "[2/6] plan queue"
python3 -m moodify_runtime.cli --config configs/runtime_config.json plan

echo ""
echo "[queue total lines]"
wc -l data/moodify_runtime/run_queue.jsonl || true

echo ""
echo "[3/6] run ALL pending tasks"
python3 -m moodify_runtime.cli --config configs/runtime_config.json run

echo ""
echo "[4/6] generate report"
python3 -m moodify_runtime.cli --config configs/runtime_config.json report

echo ""
echo "[5/6] generate craft memory"
python3 -m moodify_runtime.cli --config configs/runtime_config.json craft

echo ""
echo "[6/6] next plan"
python3 -m moodify_runtime.cli --config configs/runtime_config.json next

echo ""
date
echo "===== Moodify Daily Run -- 100+ REAL AI SONGS -- FINISH ====="
