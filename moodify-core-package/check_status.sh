#!/bin/bash
# Moodify Build Status Check
cd /home/moodify/moodify-lab
echo "=== Moodify Build Status - $(date) ==="
echo ""
echo "Claude Code Process:"
ps aux | grep "claude -p" | grep -v grep || echo "  NOT RUNNING"
echo ""
echo "Output size: $(wc -c < logs/claude_output.jsonl 2>/dev/null || echo 0) bytes"
echo "Tool calls: $(grep -c 'tool_use' logs/claude_output.jsonl 2>/dev/null || echo 0)"
echo ""
echo "Recently modified source files:"
find src -name "*.py" -newer /home/moodify/moodify-lab/work_prompt.txt -type f 2>/dev/null | sort
echo ""
echo "Latest log entry:"
tail -1 logs/claude_output.jsonl 2>/dev/null | python3 -c "import sys,json; d=json.loads(sys.stdin.read()); print(d.get('type','?') + ': ' + str(d.get('message',{}))[:120])" 2>/dev/null || echo "(cannot parse)"

