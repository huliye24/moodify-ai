# Moodify Failure Semantics

**Version:** 1.0
**Date:** 2026-08-11
**Evidence base:** MFY-FAILURE-INJECTION-001 (10 injections, 8 PASS + 2 FINDING, both fixed and deployed)

## 1. Operating principles

1. **Fail closed.** Degraded or tampered input never silently becomes a dataset row.
2. **Queue state survives.** Crash and reboot do not lose jobs; work resumes.
3. **Resource pressure defers, never corrupts.** Low memory/disk delays work, not corrupts it.
4. **Versions record.** Every case records the software versions that produced it, so any later fix can identify affected cases.

## 2. Failure modes and recovery semantics

| Failure mode | Behavior | Recovery |
|---|---|---|
| Worker killed mid-job (`kill -9`) | Job interrupted; recovered on restart, `recovered_interrupted_jobs=1`, attempts incremented | systemd auto-restart; job re-executes to completion (FI-01) |
| Server reboot | Queue persisted on disk; node operational in ~30 s | systemd startup (FI-02) |
| Corrupted source audio (non-audio bytes) | Job FAILED cleanly (`SpectrogramGenerationFailed`), worker continues | Re-submit with a valid source (FI-03) |
| Corrupted source audio (truncated wav) | Rejected by `validate_source_audio` (probe duration + decoded samples + silence check, threshold 1e-6) | Re-submit with a valid source (fix for FI-03 finding, 2026-08-11) |
| Missing artifact in case dir | aggregate_dataset → `rejected_cases.jsonl` with FileNotFoundError | Case flagged; not silently skipped (FI-04, FI-10) |
| Tampered manifest hash | `_verify_artifact_hashes` rejects source/candidate hash mismatch | Case flagged, never accepted (fix for FI-05 finding, 2026-08-11) |
| Duplicate submit (same content) | Ingest returns `duplicate` + original job_id; no new ledger row | Idempotent by content hash (FI-06) |
| Repeated execution request | Both retries REQUEUED; attempts 1→3; no duplicate artifacts | Harmless by design (FI-07) |
| Insufficient disk (< 3 GiB free) | `resource_defer`; job stays QUEUED | Resumes when disk frees (FI-08) |
| Low memory (< 300 MiB available) | `resource_defer`; job stays QUEUED | Resumes when memory frees (FI-09) |
| Partial output directory | dataset builder rejects missing required files | Case flagged in `rejected_cases.jsonl` (FI-10) |

## 3. Deferral thresholds (2C2G node)

- Minimum available memory: 300 MiB (`MOODIFY_NODE_MIN_AVAILABLE_MB`)
- Minimum free disk: 3 GiB (`MOODIFY_NODE_MIN_FREE_DISK_GB`)
- Poll interval: 10 s (`MOODIFY_NODE_POLL_SECONDS`)
- Single worker concurrency enforced; soft pressure signal `MemoryHigh=1500M`

## 4. Known findings (both fixed 2026-08-11)

- **MFY-FI-FINDING-001 (MEDIUM, fixed):** dataset aggregation did not verify artifact hashes; tampered manifests could enter the dataset. Fixed by `_verify_artifact_hashes` in `dataset_builder.py`.
- **MFY-FI-FINDING-002 (LOW, fixed):** truncated wav could be accepted as a successful scan. Fixed by `validate_source_audio` in `runner.py` (decode + duration + silence checks).

## 5. Unresolved / accepted risks

- Server-reboot injection not re-run in the same session (prior evidence 2026-08-10, acceptance.md Gate C).
- Cross-machine determinism verified for the before-scan path only; after-scan and candidate processing rely on the same DSP code but were not separately injected on both machines.
