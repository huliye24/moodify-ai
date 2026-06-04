# Recovery Scenario Matrix — MHP-103

| # | Scenario | Detection | Recovery | Estimated RTO | Tested? |
|---|----------|-----------|----------|---------------|---------|
| 1 | Task subprocess exit code != 0 | Supervisor exit_code check | Retry (max_retries=2), then mark failed | 2s | ✅ MHP-095 |
| 2 | Task subprocess timeout | Supervisor timeout | Kill + retry, then mark failed | timeout+N*retry_delay | ✅ MHP-095 |
| 3 | Runner process SIGKILL | Heartbeat age > 60s | New runner reads queue, skips done tasks | 30s + heartbeat interval | ⚠️ Build NEM |
| 4 | Disk full mid-run | Free space monitor (< 3GB) | Pause queue, alert operator | Manual intervention | ⚠️ Build NEM |
| 5 | Stale lock file | Lock file age > 30min | Force-release via CLI, restart runner | 1min | ⚠️ Build NEM |
| 6 | JSONL file corruption | Parse error on read | Restore from backup, compact | 5min | ❌ System NEM |
| 7 | Multi-runner collision | Lock file contention | Second runner exits with "already running" | Immediate | ✅ lock.py |
| 8 | Memory exhaustion | RSS monitoring | Graceful shutdown + alert | Manual intervention | ❌ System NEM |
