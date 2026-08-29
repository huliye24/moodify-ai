#!/bin/bash
# Moodify Autonomous Build Script - runs as moodify user
set -e

PROJECT_DIR=/home/moodify/moodify-lab
LOG_DIR=$PROJECT_DIR/logs
mkdir -p $LOG_DIR $PROJECT_DIR/outputs

echo "==========================================" | tee -a $LOG_DIR/master.log
echo "Moodify Autonomous Build - $(date)" | tee -a $LOG_DIR/master.log
echo "==========================================" | tee -a $LOG_DIR/master.log

# Copy prompt if not already there
if [ ! -f $PROJECT_DIR/work_prompt.txt ]; then
    cp /root/moodify-lab/work_prompt.txt $PROJECT_DIR/work_prompt.txt 2>/dev/null || true
fi

PROMPT=$(cat $PROJECT_DIR/work_prompt.txt)

echo "Launching Claude Code as moodify user at $(date)" | tee -a $LOG_DIR/master.log

su - moodify -c "cd $PROJECT_DIR && nohup claude -p '$PROMPT' --dangerously-skip-permissions --verbose --output-format stream-json --max-budget-usd 50 --add-dir $PROJECT_DIR > $LOG_DIR/claude_output_$(date +%Y%m%d_%H%M%S).jsonl 2> $LOG_DIR/claude_error.log & echo PID=\$!"

echo "Build launched at $(date)" | tee -a $LOG_DIR/master.log
echo "Monitor: tail -f $LOG_DIR/master.log" | tee -a $LOG_DIR/master.log
