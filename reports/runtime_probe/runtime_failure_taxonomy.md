# Runtime Failure Taxonomy — MHP-090

**Date**: 2026-06-04 | **E-Chain**: ECHAIN-MOODIFY-RUNTIME-001

## Failure Classes (observed from NEM-001 and NEM-002 validation runs)

### CRITICAL: Would block unattended production

| Class | Pattern | Freq | Mitigation |
|-------|---------|------|------------|
| SUBPROCESS_CRASH | moodify.cli process exits non-zero | ~5% of real audio tasks | Supervisor retry + crash log capture |
| DEAD_RUN | Runner process killed mid-loop, all state lost | 0 observed, 100% risk | Resumable queue + checkpoint |
| DISK_EXHAUSTED | Output disk fills during long run | Not yet observed, 49.5GB free | Disk monitor + auto-pause |

### HIGH: Would degrade production quality

| Class | Pattern | Freq | Mitigation |
|-------|---------|------|------------|
| CLI_ARG_MISMATCH | Command template doesn't match CLI interface | 1 major incident (config.py fixed) | Contract test at startup |
| TIMEOUT | Task exceeds timeout, no kill signal | 0 observed (timeout=300s, tasks ~2s) | OS-level timeout with SIGKILL |
| FILE_NOT_FOUND | Source audio path invalid | ~5% in early runs, 0% after registry fix | Registry pre-validation |
| PARTIAL_RUN | Some tasks complete, some fail, no resume | All multi-task runs | Resume from last checkpoint |

### MEDIUM: Operational friction

| Class | Pattern | Mitigation |
|-------|---------|------------|
| RACE_CONDITION | Two runners on same queue (lock mitigates) | Lock file already exists |
| STALE_LOCK | Lock file left after crash | Lock timeout + force-release CLI |
| LOG_ROTATION | daily_run.log grows unbounded | Log rotation in Build NEM |
| NO_PROGRESS | Long run with no visibility until completion | Heartbeat + progress streaming |

### LOW: Edge cases

| Class | Pattern | Mitigation |
|-------|---------|------------|
| UNICODE_PATH | Non-ASCII filenames in audio paths | Path sanitization in registry |
| LARGE_FILE | >500MB WAV causes memory pressure | Streaming read in metrics.py |
| MP3_DECODE | ffmpeg decode failure for corrupted MP3s | WAV-only validation, pre-check format |

## Recovery Capability Matrix

| Scenario | Current | Target after Build NEM |
|----------|---------|----------------------|
| Single task failure | Retry within run (max_retries=2) | Retry + exponential backoff + permanent failure after N retries |
| Runner process killed | All state lost, full re-run | Resume from last checkpoint, skip completed tasks |
| Disk full mid-run | Crash | Pause, alert, wait for operator action |
| Subprocess hang | Blocked forever (subprocess.run no timeout) | OS-level timeout + SIGKILL |
| Multi-runner collision | Lock prevents (good) | Lock + supervisor heartbeat to detect stale lock |
