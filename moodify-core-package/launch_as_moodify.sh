#!/bin/bash
set -e

PROJECT_DIR=/home/moodify/moodify-lab
LOG_DIR=$PROJECT_DIR/logs
mkdir -p $LOG_DIR $PROJECT_DIR/outputs

TIMESTAMP=$(date +%Y%m%d_%H%M%S)

echo "==========================================" | tee -a $LOG_DIR/master.log
echo "Moodify Autonomous Build - $(date)" | tee -a $LOG_DIR/master.log
echo "==========================================" | tee -a $LOG_DIR/master.log

# Read prompt from file (proven approach from run_claude.sh)
PROMPT=$(cat $PROJECT_DIR/work_prompt.txt)

echo "Launching Claude Code at $(date)" | tee -a $LOG_DIR/master.log

nohup claude -p "$PROMPT"     --dangerously-skip-permissions     --verbose     --output-format stream-json     --max-budget-usd 50     --add-dir $PROJECT_DIR     > $LOG_DIR/claude_output_${TIMESTAMP}.jsonl     2> $LOG_DIR/claude_error.log &

CLAUDE_PID=$!
echo "Claude PID: $CLAUDE_PID" | tee -a $LOG_DIR/master.log
echo $CLAUDE_PID > $LOG_DIR/claude.pid

sleep 5
if kill -0 $CLAUDE_PID 2>/dev/null; then
    echo "Claude is running (PID: $CLAUDE_PID)" | tee -a $LOG_DIR/master.log
else
    echo "ERROR: Claude failed to start" | tee -a $LOG_DIR/master.log
fi
