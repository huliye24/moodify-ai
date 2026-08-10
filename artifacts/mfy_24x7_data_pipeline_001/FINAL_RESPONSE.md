# MFY-24X7-DATA-PIPELINE-001 — Final Response

## 1. Verdict

PASS (10-song pilot included)

## 2. Baseline preserved

- Existing node implementation: unchanged semantics; core package updated with recovery hardening only (recover_interrupted requeues RUNNING work immediately on worker restart instead of waiting for the 6 h lease; rejected_cases.jsonl in dataset aggregation; `node` extra for matplotlib)
- Existing 3-case evidence: preserved (job_9ded088a / job_98c143f / job_ff351917 + case dirs; recorded in preflight.json)
- Auditory/data semantic changes: NONE

## 3. Server configuration

- vCPU: 2 (unchanged)
- RAM: 1.6 GiB (unchanged)
- Swap: 2 GiB file /swapfile, swappiness=10 (unchanged)
- Disk: 40 GiB, 28 GiB free after pilot (27% used)
- Worker concurrency: 1 (unchanged)
- Permanent services: moodify-data-worker.service + moodify-api.service + 4 timer-driven ops services (inbox ingest, resource probe, daily report, metadata backup)

## 4. Installed 24/7 pipeline

- Atomic inbox: staging/*.part -> fsync/complete -> mv to inbox; ingest ignores staging
- Source store: /var/lib/moodify/sources/sha256/<2>/<sha>/<name> (immutable, deduplicated by SHA256)
- Ingestion ledger: /var/lib/moodify/ops/ingest.sqlite3 (WAL, source_sha256 PK, job_id)
- Resource probe: every 5 min -> /var/lib/moodify/ops/resource_snapshots.jsonl
- Daily report: 00:05 -> /var/lib/moodify/reports/YYYY-MM-DD/node_daily_report.{json,md}
- Metadata backup: 00:20 -> /var/backups/moodify/YYYY-MM-DD/ (SQLite via backup API + metadata tar.gz, no heavy assets, keep=7)
- systemd timers: inbox-ingest (1 min), resource-probe (5 min), daily-report (00:05), metadata-backup (00:20); worker drop-in 10-24x7.conf (Restart=always, Nice=10, MemoryHigh=1500M)

## 5. Validation

- Ingest smoke: PASS (staging ignored, min-age respected, SHA256 store, dedup, stable-path jobs)
- Dedup smoke: PASS (identical content enqueued once; ledger returns duplicate + original job_id)
- Worker smoke: PASS (17 SUCCEEDED jobs total incl. 10 pilot; 2 FAILED are documented 16-byte non-audio smoke artifacts)
- Restart/recovery: PASS (SIGKILL mid-job -> worker restart -> recovered_interrupted_jobs=1 -> job completed attempts=2; live reboot -> node operational in ~30 s)
- Resource telemetry: PASS (82 snapshots; swap/disk/memory/service states)
- Daily report: PASS (counts, durations, failures, defer/OOM, evidence-based recommendation)
- Backup restore/open: PASS (both DBs integrity ok, archive opens, no heavy assets, retention keep=7)
- Reboot readiness: PASS (live reboot test performed with operator approval)

## 6. 10-song pilot status

| Case | Source duration | Runtime | Result | Peak swap | Min available RAM | Notes |
|---|---:|---:|---:|---:|---:|---|
| pilot-01 | 179.8 s | 87.8 s | SUCCEEDED | - | - | |
| pilot-02 | 131.3 s | 62.9 s | SUCCEEDED | 165.8 MiB | 833.7 MiB | |
| pilot-03 | 184.3 s | 85.7 s | SUCCEEDED | - | - | |
| pilot-04 | 198.0 s | 86.3 s | SUCCEEDED | - | - | |
| pilot-05 | 179.8 s | 89.6 s | SUCCEEDED | 663.4 MiB | 781.0 MiB | |
| pilot-06 | 128.5 s | 64.5 s | SUCCEEDED | - | - | |
| pilot-07 | 184.4 s | 95.0 s | SUCCEEDED | - | - | |
| pilot-08 | 193.5 s | 98.9 s | SUCCEEDED | 1024.7 MiB | 570.6 MiB | 20 s probe burst active |
| pilot-09 | 159.9 s | 89.6 s | SUCCEEDED | 1024.0 MiB | 511.7 MiB | 20 s probe burst active |
| pilot-10 | 188.5 s | 89.9 s | SUCCEEDED | 1024.0 MiB | 518.2 MiB | 20 s probe burst active |

Summary: 10/10 completed, 0 failed, 0 OOM, 0 resource defer, 0 worker restart, queue drained, disk healthy.

## 7. Hardware verdict

KEEP_2C2G (with REVIEW_MEMORY watch flag)

Evidence:
- 10/10 full-length cases SUCCEEDED, 1 attempt each; runtimes stable (62.9-98.9 s, no growth trend across the pilot)
- OOM = 0 (kernel journal), resource_defer = 0, worker NRestarts = 0
- Memory available never below 511.7 MiB during any case; recovered to ~770 MiB idle
- Queue drains to 0; disk 27.3 GiB min free
- Watch: swap parks at ~1.0/2.0 GiB during/after full-length processing (vs 76 MiB on 45 s clips). The automated daily report flags REVIEW_MEMORY (peak 1024.7 > 1024 MiB threshold). Upgrade to 2C4G (memory first) only if sustained swap > 1.2 GiB, repeated failures, or resource defers appear on future batches.

## 8. Blocking issues

None.

## 9. Next action

Operator: upload songs via `upload_one_song.sh` and let the node accumulate; watch the daily report's REVIEW_MEMORY flag for 1-2 weeks; if sustained swap > 1.2 GiB or failures appear, upgrade to 2C4G.
