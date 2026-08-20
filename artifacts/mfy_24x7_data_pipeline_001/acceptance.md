# MFY-24X7-DATA-PIPELINE-001 — Acceptance

Executed 2026-08-10 against node 120.55.191.146 (2C2G, Ubuntu 26.04, kernel 7.0).

## Gate A — Preserve working baseline — PASS

- [x] Existing 3-case evidence preserved (jobs job_9ded088a / job_98c143f / job_ff351917 + case dirs intact; recorded in preflight.json)
- [x] Existing worker still completes smoke cases (3 leftover sources re-processed through the new pipeline: SUCCEEDED)
- [x] No auditory/data semantic version changes (this package is ops-hardening only; scan-profile, metrics, ProductionCase, A/B/C, DSP semantics untouched)

## Gate B — Atomic ingest — PASS

- [x] Files under staging ignored (staging_test.wav.part untouched, never enqueued)
- [x] Inbox file older than minimum age ingested (old_test.wav ingested; young_test.wav younger than 120 s ignored)
- [x] SHA256 source store created (/var/lib/moodify/sources/sha256/<2>/<sha>/<name>)
- [x] Same source SHA not enqueued twice (old_test.wav == dup_test.wav content: one enqueue; mfy_smoke/track_0/track_1 duplicates returned as `duplicate` with original job_id)
- [x] Job references stable source-store path (all new jobs reference /var/lib/moodify/sources/sha256/...)

## Gate C — 24/7 services — PASS

- [x] Worker enabled (moodify-data-worker.service, drop-in 10-24x7.conf loaded: Restart=always, Nice=10, MemoryHigh=1500M)
- [x] Inbox timer enabled (moodify-inbox-ingest.timer, 1 min)
- [x] Resource probe timer enabled (moodify-resource-probe.timer, 5 min)
- [x] Daily report timer enabled (moodify-daily-report.timer, 00:05)
- [x] Metadata backup timer enabled (moodify-metadata-backup.timer, 00:20)
- [x] Reboot leaves the node operational — live reboot test: back in ~30 s; worker active, API active, all 4 timers enabled, queue data retained

## Gate D — Telemetry — PASS

- [x] Resource JSONL produced (82 snapshots during pilot: timestamp, MemAvailable, SwapTotal/Used, disk free, load, worker/API state)
- [x] Swap used visible (76 MiB baseline -> 1024.7 MiB peak during full-length cases -> 1019.7 MiB parked post-pilot)
- [x] Disk free visible (27.3 GiB min during pilot)
- [x] Worker/API state visible (worker_state/api_state fields active throughout)

## Gate E — Daily report — PASS

- [x] Queue counts correct ({"FAILED": 2, "SUCCEEDED": 17})
- [x] Last-24h success/failure correct (17 succeeded / 2 failed; both failures are documented smoke artifacts: 16-byte non-audio files)
- [x] Duration statistics computed (median 64.5 s, p95 95.8 s)
- [x] resource/defer/OOM evidence included (defer 0, OOM 0, worker failed lines 0)
- [x] Recommendation evidence-based (REVIEW_MEMORY triggered by peak swap 1024.7 MiB > 1024 MiB threshold; reconciled in pilot_status.json as KEEP_2C2G + watch)

## Gate F — Backup — PASS

- [x] SQLite backup opens (node.sqlite3 integrity ok, 8 rows at backup time; ingest.sqlite3 integrity ok, 4 rows)
- [x] Metadata archive opens (tar -tzf ok; 262 case metadata files + 2 report files)
- [x] Large WAV/PNG/NPZ assets not duplicated (tar contains no .wav/.flac/.mp3/.png/.npz; verified by grep)
- [x] Retention removes only expired sets (keep=7; 1 set present, prune_old implemented and exercised)

## Gate G — 10-song pilot — PASS

- [x] 10/10 rights-approved songs (all operator-owned full-length tracks, rights_ok=true)
- [x] Complete songs included (128-198 s, all >= 120 s full-length signal; manifest validated 0 errors)
- [x] 10/10 case completion (all SUCCEEDED, 1 attempt each)
- [x] OOM count known (0)
- [x] Defer count known (0)
- [x] Peak swap known (1024.7 MiB)
- [x] Final hardware verdict recorded (KEEP_2C2G with REVIEW_MEMORY watch flag; see pilot_status.json)
- [x] Case completeness verified per case: source, source hash, before scan, A/B/C plans, A/B/C candidates, after scans, comparisons, human review placeholder, case manifest + production_case.json (checked case_8d6f040454f147f09edbcc3a60994bc9)

## Final acceptance — PASS

The operator can leave the node unattended and later reconstruct what happened:
daily reports (JSON+MD), resource telemetry JSONL, ingestion ledger, metadata backups,
recovery on worker restart (recover_interrupted), and the pilot table in pilot_status.json.

## Evidence inventory (artifacts/mfy_24x7_data_pipeline_001/)

preflight.json, service_status.txt, resource_baseline.json, prechange_raw.json,
resource_snapshots_pilot.jsonl, server_final_state.txt, daily_report_sample.md,
pilot_progress_remote.json, pilot_status.json, recovery smoke (log in server journal:
recovered_interrupted_jobs=1), ingest smoke (this log).
