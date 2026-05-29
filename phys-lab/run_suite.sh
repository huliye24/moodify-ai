#!/bin/bash
# Moodify 异步实验启动器 — 放到云端 /home/ubuntu/run_suite.sh
# 用法: ./run_suite.sh quick    (5 min)
#       ./run_suite.sh full     (2-4 hours)
#       ./run_suite.sh engineering (25 min)

SUITE=${1:-quick}
cd /home/ubuntu/moodify
export PYTHONPATH=moodify-core-package/src:$PYTHONPATH
mkdir -p outputs/reports

LOG_FILE=outputs/reports/$(date +%Y-%m-%d_%H-%M-%S)_${SUITE}.log

echo "=== Moodify Suite: $SUITE ===" | tee -a $LOG_FILE
echo "Start: $(date)" | tee -a $LOG_FILE
echo "PID: $$" | tee -a $LOG_FILE

python3 -u -m moodify.physics.batch_runner --suite $SUITE >> $LOG_FILE 2>&1

echo "" | tee -a $LOG_FILE
echo "Done: $(date)" | tee -a $LOG_FILE
echo "" | tee -a $LOG_FILE
echo "Latest reports:"
ls -lt outputs/reports/*_report.md 2>/dev/null | head -3
