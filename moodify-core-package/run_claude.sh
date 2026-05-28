#!/bin/bash
cd /home/moodify/moodify-lab
mkdir -p logs outputs

PROMPT=$(cat work_prompt.txt)

nohup claude -p "$PROMPT"     --dangerously-skip-permissions     --verbose     --output-format stream-json     --max-budget-usd 50     --add-dir /home/moodify/moodify-lab     > logs/claude_output.jsonl     2> logs/claude_error.log &

echo $!

