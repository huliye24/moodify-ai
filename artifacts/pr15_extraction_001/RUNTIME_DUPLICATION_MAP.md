# Runtime and Cloud Duplication Map

| Responsibility | Implementations found | Surviving concept | Disposition |
|---|---|---|---|
| Queue | `moodify_runtime/queue.py`, `workers/job_queue.py`, packaged night runtime queue | durable claim/attempt metadata | Reimplement one infrastructure queue keyed by canonical case/execution IDs; delete packaged duplicates later |
| Scheduler | runtime scheduler plus night scripts/config | compute request/lease/run/cost separation | Keep as reference; do not make scheduler status product state |
| Worker | runtime runner, cloud worker, night worker, packaged night worker | immutable execution envelope, heartbeat, bounded retry | Extract interfaces; archive duplicate workers |
| Supervisor | `supervisor.py`, runtime state heartbeat/lease, checkpoint/resource guard | timeout, heartbeat, lease expiry, resumable execution | Consolidate after ProductionCase contract |
| Retry/recovery | supervisor retries, runtime failure records, queue attempts, service retry orchestrator | structured failure class and retry policy | One execution retry policy; state transitions remain PPE-owned |
| Registry | runtime registry/mainline registry/schema registry/night registry | source/worker capability registration | Separate capability registry from asset registry |
| Reports/evidence | runtime report, craft evidence, data asset, PDFs, auditory manifests | content hashes, producer/version, evidence indexes | Bind to minimum EvidenceArtifact contract; PDFs are presentation only |
| Runtime state | queue status, ComputeRun, resumable task state, operator job, tidal states | infrastructure projection | None may replace ProductionCase state |

## Decision

No cloud/runtime implementation should be migrated before the canonical ProductionCase and EvidenceArtifact contracts. Preserve lease, heartbeat, bounded retry, atomic JSONL/file-write, structured failure, and cost-accounting concepts. Archive duplicated `night/moodify_daily_run_system*` packages and generated ZIPs after evidence extraction.
