# MHP-469: Tidal Safety Risk Taxonomy

**Status**: completed
**Date**: 2026-06-04
**Chain**: ECHAIN-MOODIFY-TIDAL-CORE-008 / NEM-MOODIFY-TIDAL-CORE-PROBE-024
**Plan-6**: Probe Plan-6A: Boundary / P3 (Validation)
**Depends on**: MHP-468 (Tidal Lifecycle Vocabulary)

## 1. Purpose

This taxonomy classifies every failure mode the tidal cycle can encounter during unattended operation. Each risk is assigned a severity, detection mechanism, blast radius, and mitigation strategy. This document serves as the safety design basis for the Build NEM's safety cutoff engine (MHP-489).

## 2. Severity Scale

| Level | Name | Definition | Engine Response |
|-------|------|-----------|-----------------|
| S0 | **NON_EVENT** | Informational, no impact | Log only |
| S1 | **DEGRADED** | Minor degradation, cycle continues | Log + increment counter |
| S2 | **IMPAIRED** | Phase or task affected, recoverable | Retry or skip phase |
| S3 | **BLOCKED** | Cycle cannot proceed, engine can recover | Pause engine, retry after delay |
| S4 | **CRITICAL** | Engine integrity at risk | Graceful shutdown |
| S5 | **FATAL** | System or host at risk | Immediate stop + alert |

## 3. Risk Taxonomy

### 3.1 Resource Exhaustion Risks

#### R-DISK-001: Disk Space Exhaustion
| Field | Value |
|-------|-------|
| Severity | S3 → S4 (if persistent) |
| Detection | `shutil.disk_usage()` pre-cycle health check |
| Threshold | < 3 GB free |
| Blast radius | All write operations (events, heartbeat, reports, outputs) |
| Current mitigation | Pause 5 minutes, retry health check |
| Gap | No backpressure on task generation; queue keeps growing |
| Build target | Halt task generation when disk < 5 GB; auto-purge old runs |

#### R-MEM-001: Memory Starvation
| Field | Value |
|-------|-------|
| Severity | S3 |
| Detection | `/proc/meminfo` MemAvailable pre-cycle health check |
| Threshold | < 500 MB free |
| Blast radius | OOM killer may terminate the engine or subprocess |
| Current mitigation | Pause 5 minutes, retry |
| Gap | No per-task memory tracking; no subprocess memory limits |
| Build target | Per-task memory budget; subprocess `memory_limit` |

#### R-CPU-001: CPU Saturation
| Field | Value |
|-------|-------|
| Severity | S2 |
| Detection | None currently |
| Threshold | Load average > nproc * 2 |
| Blast radius | Tasks slow down; heartbeat intervals stretch; timeouts may fire |
| Current mitigation | None |
| Gap | No load check before starting a cycle |
| Build target | Pre-cycle load check; skip or defer heavy tasks under high load |

#### R-FD-001: File Descriptor Exhaustion
| Field | Value |
|-------|-------|
| Severity | S3 |
| Detection | None currently |
| Threshold | Open FDs > 80% of ulimit |
| Blast radius | Event/record writes fail silently; subprocess spawn fails |
| Current mitigation | None (Python GC handles most FD cleanup) |
| Gap | No FD monitoring |
| Build target | Pre-cycle FD check; log warning at 70% |

### 3.2 Process & Subprocess Risks

#### R-PROC-001: Subprocess Hang
| Field | Value |
|-------|-------|
| Severity | S2 |
| Detection | `subprocess.run(timeout=...)` |
| Threshold | `phase_run` timeout = 3600s; other phases = 600s |
| Blast radius | Single phase blocked, cycle delayed |
| Current mitigation | Timeout raises `subprocess.TimeoutExpired`; supervisor has retry |
| Gap | Timeout doesn't kill child processes of the subprocess |
| Build target | Process group kill on timeout; orphan reaper |

#### R-PROC-002: Subprocess Crash
| Field | Value |
|-------|-------|
| Severity | S2 |
| Detection | Non-zero exit code from subprocess |
| Blast radius | Phase may produce incomplete output |
| Current mitigation | Supervisor retries once; error appended to record |
| Gap | No distinction between transient crash and deterministic crash |
| Build target | Crash classifier (transient vs deterministic); escalate after N repeats |

#### R-PROC-003: Engine Process Crash
| Field | Value |
|-------|-------|
| Severity | S4 |
| Detection | PID file contains stale PID; heartbeat stops updating |
| Blast radius | Tidal cycle stops completely |
| Current mitigation | Top-level try/except in `TidalEngine.run()`; structured error record |
| Gap | No external watchdog; operator must notice manually |
| Build target | External watchdog script/systemd; auto-restart with backoff |

#### R-PROC-004: Zombie/Orphan Subprocesses
| Field | Value |
|-------|-------|
| Severity | S3 |
| Detection | None currently |
| Blast radius | Accumulated zombies consume PIDs; orphans consume memory |
| Current mitigation | None |
| Build target | Process group tracking; SIGCHLD handler; orphan reaper on startup |

### 3.3 Data Integrity Risks

#### R-DATA-001: Corrupted Event Stream
| Field | Value |
|-------|-------|
| Severity | S2 |
| Detection | JSON parse error on event read |
| Blast radius | Monitoring tools cannot parse events; partial data loss |
| Current mitigation | Each event is a single `json.dumps()` + `\n` — atomic-ish but no fsync |
| Gap | No event checksum, no recovery for partially written lines |
| Build target | Append-only with fsync; event sequence numbers; checksum field |

#### R-DATA-002: Stale Registry
| Field | Value |
|-------|-------|
| Severity | S1 |
| Detection | `register` phase scans input dirs and compares with registry |
| Blast radius | Missing audio files not discovered; deleted files cause task failures |
| Current mitigation | Registration runs every cycle |
| Gap | No dedup of already-registered-and-deleted files |
| Build target | Registry health check; orphan entry cleanup |

#### R-DATA-003: Queue State Drift
| Field | Value |
|-------|-------|
| Severity | S2 |
| Detection | Task marked "done" in queue but output file missing |
| Blast radius | Report generation references non-existent outputs |
| Current mitigation | None |
| Gap | No queue-output consistency check |
| Build target | Pre-report integrity check; reconcile queue status with filesystem |

#### R-DATA-004: Heartbeat Corruption
| Field | Value |
|-------|-------|
| Severity | S2 |
| Detection | JSON parse error on heartbeat read |
| Blast radius | Monitoring shows stale/absent heartbeat; false alarm |
| Current mitigation | None (file overwrite, not atomic) |
| Build target | Atomic write (write-temp + rename); heartbeat sequence number |

### 3.4 Coordination & Timing Risks

#### R-TIME-001: Cycle Overrun
| Field | Value |
|-------|-------|
| Severity | S2 |
| Detection | `elapsed > interval` |
| Blast radius | Cycles drift; next cycle starts late; overnight throughput reduced |
| Current mitigation | `sleep_time = max(0, interval - elapsed)` — skips sleep if overrun |
| Gap | No overrun tracking; repeated overruns not escalated |
| Build target | Overrun counter; escalate to S3 after N consecutive overruns |

#### R-TIME-002: Sleep Interruption
| Field | Value |
|-------|-------|
| Severity | S1 |
| Detection | Sleep loop checks `self._running` every 10s |
| Blast radius | Shutdown delayed by up to 10s |
| Current mitigation | 10s sleep chunks |
| Gap | No record of interrupted sleep duration |
| Build target | Log actual sleep duration vs planned |

#### R-TIME-003: Clock Skew
| Field | Value |
|-------|-------|
| Severity | S2 |
| Detection | None currently |
| Blast radius | Event timestamps drift; cycle scheduling disrupted |
| Current mitigation | Uses `datetime.now(timezone.utc)` — UTC is stable but not monotonic |
| Gap | No monotonic time source for elapsed measurements |
| Build target | Use `time.monotonic()` for durations; `utc_now()` for wall clock |

#### R-COORD-001: Duplicate Engine Instance
| Field | Value |
|-------|-------|
| Severity | S4 |
| Detection | PID file check in `tidal_start.sh` |
| Blast radius | Two engines processing the same queue → race conditions, duplicate outputs |
| Current mitigation | Start script refuses if PID file exists and process is alive |
| Gap | Stale PID file can prevent restart after crash; no distributed lock |
| Build target | PID file TTL; lease file with timestamp; cloud lease for multi-machine |

### 3.5 Operational Risks

#### R-OPS-001: Unattended Error Accumulation
| Field | Value |
|-------|-------|
| Severity | S3 |
| Detection | `record.errors` list grows unbounded |
| Blast radius | Engine continues with degraded state; operator discovers hours later |
| Current mitigation | Error list is per-cycle and reset each cycle |
| Gap | No cumulative error tracking across cycles |
| Build target | Cross-cycle error counter with escalation threshold |

#### R-OPS-002: Silent Output Degradation
| Field | Value |
|-------|-------|
| Severity | S3 |
| Detection | None currently |
| Blast radius | Engine produces outputs that pass gates but are acoustically degraded |
| Current mitigation | Gate phase exists in vocabulary but not implemented |
| Gap | No gate implementation in current code |
| Build target | Implement gate phase with MRS scoring threshold |

#### R-OPS-003: Operator Cannot Intervene
| Field | Value |
|-------|-------|
| Severity | S2 |
| Detection | No operator command surface at runtime |
| Blast radius | Operator must kill the engine to change configuration |
| Current mitigation | SIGTERM for graceful stop |
| Gap | No pause, reconfigure, or skip-phase commands |
| Build target | Runtime CLI commands: `tidal pause`, `tidal resume`, `tidal skip-phase` |

#### R-OPS-004: Morning Report Is Empty
| Field | Value |
|-------|-------|
| Severity | S1 |
| Detection | Report generation runs but output has no task results |
| Blast radius | Operator has no visibility into overnight work |
| Current mitigation | Report phase always runs |
| Gap | No "no tasks" guard; report may be empty without warning |
| Build target | Explicit "no tasks processed" marker in report; reason field |

### 3.6 Security & Access Risks

#### R-SEC-001: Malicious Audio Input
| Field | Value |
|-------|-------|
| Severity | S3 |
| Detection | None currently |
| Blast radius | Crafted audio could exploit processing library bugs |
| Current mitigation | Audio file extension whitelist (`.wav`, `.mp3`, `.flac`, `.aiff`, `.m4a`, `.ogg`) |
| Gap | No file content validation before processing |
| Build target | Magic byte check; file size limit; audio duration limit |

#### R-SEC-002: Subprocess Command Injection
| Field | Value |
|-------|-------|
| Severity | S4 |
| Detection | None currently |
| Blast radius | Preset names or file paths with shell metacharacters could inject commands |
| Current mitigation | `subprocess.run()` with list arguments (no shell) |
| Gap | Preset names from config not sanitized |
| Build target | Preset name validation regex; path sanitization |

### 3.7 Environmental Risks

#### R-ENV-001: Python Environment Breakage
| Field | Value |
|-------|-------|
| Severity | S4 |
| Detection | Import errors on engine start |
| Blast radius | Engine won't start |
| Current mitigation | None (start script fails) |
| Gap | No pre-flight import check |
| Build target | `tidal doctor` command for environment validation |

#### R-ENV-002: Config File Corruption
| Field | Value |
|-------|-------|
| Severity | S3 |
| Detection | YAML/JSON parse error on config load |
| Blast radius | Engine starts with wrong parameters or fails to start |
| Current mitigation | CLI arg defaults |
| Gap | No config validation schema |
| Build target | Config schema with defaults; `tidal config validate` |

## 4. Risk Matrix Summary

| Risk ID | Severity | Detected? | Mitigated? | Build Priority |
|---------|----------|-----------|------------|----------------|
| R-DISK-001 | S3→S4 | Yes (basic) | Partial | P0 |
| R-MEM-001 | S3 | Yes (basic) | Partial | P0 |
| R-CPU-001 | S2 | No | No | P2 |
| R-FD-001 | S3 | No | No | P2 |
| R-PROC-001 | S2 | Yes | Partial | P1 |
| R-PROC-002 | S2 | Yes | Partial | P1 |
| R-PROC-003 | S4 | Partial | No | P0 |
| R-PROC-004 | S3 | No | No | P2 |
| R-DATA-001 | S2 | No | No | P1 |
| R-DATA-002 | S1 | Partial | No | P3 |
| R-DATA-003 | S2 | No | No | P1 |
| R-DATA-004 | S2 | No | No | P2 |
| R-TIME-001 | S2 | Partial | Partial | P1 |
| R-TIME-002 | S1 | Partial | No | P3 |
| R-TIME-003 | S2 | No | No | P3 |
| R-COORD-001 | S4 | Yes (basic) | Partial | P0 |
| R-OPS-001 | S3 | No | No | P0 |
| R-OPS-002 | S3 | No | No | P0 |
| R-OPS-003 | S2 | No | No | P1 |
| R-OPS-004 | S1 | No | No | P2 |
| R-SEC-001 | S3 | No | Partial | P1 |
| R-SEC-002 | S4 | No | Partial | P0 |
| R-ENV-001 | S4 | Partial | No | P2 |
| R-ENV-002 | S3 | Partial | No | P2 |

## 5. Build NEM Safety Cutoff Requirements

From this taxonomy, the safety cutoff engine (`MHP-489`) must implement:

1. **Hard stops** (S4/S5): Disk < 1 GB, duplicate engine, command injection detected → immediate shutdown
2. **Soft stops** (S3): Memory < 500 MB, N consecutive overruns, error threshold exceeded → pause with backoff
3. **Degrade** (S2): Subprocess hangs, data corruption → skip phase, increment counter, continue
4. **Log only** (S0/S1): Empty report, sleep interruption → record, no action

## 6. Detection Coverage Gap

| Currently Detected | Currently Undetected |
|--------------------|---------------------|
| Disk space (basic) | CPU saturation |
| Memory (basic) | FD exhaustion |
| Subprocess timeout | Zombie processes |
| Subprocess exit code | Event stream corruption |
| Duplicate engine (startup only) | Queue-output drift |
| | Cumulative error threshold |
| | Output degradation |
| | Clock skew |
| | Malicious input |
| | Config corruption |
