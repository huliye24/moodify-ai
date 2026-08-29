#!/bin/bash
# Moodify 可靠实验启动器
# 用法: ./run_suite.sh quick    (5 min, 预检+保护)
#       ./run_suite.sh full     (2-4 hours, 检查点+超时+恢复)
#       ./run_suite.sh --resume bmatrix  (从检查点恢复)

SUITE=${1:-quick}
cd /home/ubuntu/moodify
export PYTHONPATH=moodify-core-package/src:$PYTHONPATH
mkdir -p outputs/reports outputs/status outputs/checkpoints

LOG_FILE=outputs/reports/$(date +%Y-%m-%d_%H-%M-%S)_${SUITE}.log

echo "=== Moodify Reliable Runner ===" | tee -a $LOG_FILE
echo "Suite: $SUITE" | tee -a $LOG_FILE
echo "Start: $(date)" | tee -a $LOG_FILE
echo "Host: $(hostname)  CPU: $(nproc)  RAM: $(free -h | awk 'NR==2{print $2}')  Disk: $(df -h / | awk 'NR==2{print $4}')" | tee -a $LOG_FILE

# 预检
python3 -c "
from moodify.physics.reliable_runner import preflight_check
checks = preflight_check()
print(f'Pre-flight OK: disk={checks[\"disk_free_mb\"]}MB')
" 2>&1 | tee -a $LOG_FILE

if [ ${PIPESTATUS[0]} -ne 0 ]; then
    echo "FATAL: Pre-flight failed. Aborting." | tee -a $LOG_FILE
    exit 1
fi

# 执行
python3 -u -m moodify.physics.reliable_runner --suite $SUITE --timeout 7200 >> $LOG_FILE 2>&1
EXIT_CODE=$?

echo "" | tee -a $LOG_FILE
echo "Exit: $EXIT_CODE  Time: $(date)" | tee -a $LOG_FILE
echo "" | tee -a $LOG_FILE

# 显示最新报告
echo "=== Latest Reports ===" | tee -a $LOG_FILE
ls -lt outputs/reports/*_reliable_report.md 2>/dev/null | head -3 | tee -a $LOG_FILE
echo "" | tee -a $LOG_FILE

# 检查是否有未清理的检查点 (说明上次崩溃了)
CHECKPOINTS=$(find outputs/checkpoints -name "checkpoint.json" 2>/dev/null | wc -l)
if [ $CHECKPOINTS -gt 0 ]; then
    echo "WARNING: $CHECKPOINTS uncleaned checkpoints (may need --resume)" | tee -a $LOG_FILE
fi

exit $EXIT_CODE
