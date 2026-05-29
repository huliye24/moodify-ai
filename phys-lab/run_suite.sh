#!/bin/bash
# Moodify 异步实验启动器
# 用法: ssh tencent './run_suite.sh quick'
#       ssh tencent './run_suite.sh full'
#       ssh tencent './run_suite.sh engineering'

SUITE=${1:-quick}
LOG_DIR=/home/ubuntu/moodify/outputs/reports
mkdir -p $LOG_DIR

RUN_ID=$(date +%Y-%m-%d_%H-%M-%S)
LOG_FILE=$LOG_DIR/${RUN_ID}_run.log

echo "=== Moodify Experiment Suite: $SUITE ===" | tee -a $LOG_FILE
echo "Start: $(date)" | tee -a $LOG_FILE
echo "Log: $LOG_FILE" | tee -a $LOG_FILE

cd /home/ubuntu/moodify

# Kill any previous experiments
pkill -f batch_runner 2>/dev/null || true
sleep 1

# Launch batch runner
PYTHONUNBUFFERED=1 nohup python3 -u -m moodify.physics.batch_runner \
    --suite $SUITE \
    >> $LOG_FILE 2>&1 &

PID=$!
echo "PID: $PID" | tee -a $LOG_FILE
echo "" | tee -a $LOG_FILE
echo "Experiment launched. Monitor with:"
echo "  tail -f $LOG_FILE"
echo ""
echo "Check results after completion:"
echo "  cat outputs/reports/$(date +%Y-%m-%d)*_report.md"
echo ""
echo "Auto-stop: process will exit automatically when all experiments complete."

# Save PID for monitoring
echo $PID > /tmp/moodify_experiment.pid
