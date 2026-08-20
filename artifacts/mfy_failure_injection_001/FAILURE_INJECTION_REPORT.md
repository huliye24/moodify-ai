# MFY-FAILURE-INJECTION-001 — Failure Injection Matrix Report

**Date:** 2026-08-11
**Node:** 120.55.191.146 (Aliyun, 2C2G, Ubuntu 26.04, kernel 7.0)
**Protocol reference:** MOODIFY_AUGUST_2026_FREEZE_PROTOCOL Gate 4 — Failure injection
**Queue before:** QUEUED 0 / RUNNING 0 / SUCCEEDED 17 / FAILED 2
**Queue after:** QUEUED 0 / RUNNING 0 / SUCCEEDED 21 / FAILED 3
**Verdict:** 8 PASS + 2 FINDING. No data corruption, no worker crash, no queue loss.

---

## Matrix results

| ID | Injection | Result | Evidence |
|---|---|---|---|
| FI-01 | Worker killed mid-job (kill -9) | **PASS** | job_0487e073 SUCCEEDED attempts=2; journal `recovered_interrupted_jobs=1`; systemd restart counter=1, auto-restart |
| FI-02 | Server reboot | **PASS** (prior evidence) | acceptance.md Gate C (2026-08-10): live reboot, node operational in ~30 s, queue data retained. Not re-run this session. |
| FI-03 | Corrupted audio (non-audio bytes + truncated wav) | **PASS with finding** | Non-audio text → FAILED cleanly (SpectrogramGenerationFailed, attempts=1, worker continued). Truncated 128 B wav → **accepted as SUCCEEDED** (see MFY-FI-FINDING-002). |
| FI-04 | Deleted artifact (case_manifest.json removed) | **PASS** | aggregate_dataset → rejected_cases.jsonl: FileNotFoundError |
| FI-05 | Modified artifact hash (source_sha256 zeroed in manifest) | **FINDING** | Aggregate **silently accepted** tampered case into cases.jsonl (see MFY-FI-FINDING-001). |
| FI-06 | Duplicate submit (same content, new filename) | **PASS** | Ingest returned `duplicate` + original job_id; no new ledger row, no double enqueue |
| FI-07 | Repeated execution request (retry x2 on same FAILED job) | **PASS** | Both retries REQUEUED; attempts 1→3; no duplicate artifacts; repeated failure of same corrupt source is harmless |
| FI-08 | Insufficient disk (fallocate 26G → free 1.50 GiB) | **PASS** | `resource_defer reason=free disk 1.50 GiB < 3.00 GiB`; job stayed QUEUED; after release → SUCCEEDED in 31 s |
| FI-09 | Low memory (hog 1088 MiB → MemAvailable 241 MiB) | **PASS** | `resource_defer reason=available memory 270 MiB < 300 MiB`; job stayed QUEUED; after release → SUCCEEDED in 36 s; no OOM kill |
| FI-10 | Partial output directory (missing 04_after_scan/B/metrics.json) | **PASS** | aggregate_dataset → rejected_cases.jsonl: FileNotFoundError |

**Recovery verification:** every injected condition was released and the node returned to a drained, healthy state (queue 0/0, 21 SUCCEEDED, disk 28 GiB free, memory 1.3 GiB available).

---

## Findings

### MFY-FI-FINDING-001 — MEDIUM — Aggregate does not verify artifact hash consistency

Manifest records `source_sha256` and `candidate_sha256`, but `aggregate_dataset` (dataset_builder.py) never checks these hashes against the actual artifact files. A tampered manifest (source_sha256 zeroed) was silently accepted into cases.jsonl and counted as a completed case.

**Impact:** a modified/degraded case can enter the dataset without detection, violating the freeze protocol's evidence-integrity principle (Gate 1.3 / Gate 4 "modified artifact hash").

**Suggested fix (before Gate 5/6):** add a `verify` step (CLI or aggregate-time) that recomputes source/candidate hashes and rejects mismatches. Rejected cases should be flagged, not silently accepted.

### MFY-FI-FINDING-002 — LOW — Truncated wav accepted as a successful scan

A 128-byte wav (valid header, cut payload) scanned SUCCEEDED via ffmpeg's showspectrumpic tolerance. Degenerate audio can produce empty/short analysis results without an explicit rejection.

**Impact:** low — scan results would be visibly degenerate in metrics.json; but silent acceptance contradicts "never silently change data semantics".

**Suggested fix:** runner pre-check before scan: decode duration must be > threshold (e.g. 0.5 s) and contain non-silent samples; otherwise fail the job explicitly.

---

## Cleanup performed

- `fi_disk_fill.bin` removed (disk restored to 28 GiB free)
- Memory hog process killed, `/var/tmp/fi_memhog*` removed
- Experiment copies under `/var/lib/moodify/fi_exp/` retained as evidence
- `fi_evidence/` retained on node; copies pulled to `artifacts/mfy_failure_injection_001/`
- Corrupt-source FAILED jobs retained (real failure cases, 3 total: 2 historical 16-byte smoke + fi_01)

## Gate 4 impact

- Failure-injection checklist item G4-03: **COMPLETE**
- Remaining Gate 4 items: full closed loop on remote (0/10), cross-machine repeatability (G4-04), real human review (3/4 local cases)
