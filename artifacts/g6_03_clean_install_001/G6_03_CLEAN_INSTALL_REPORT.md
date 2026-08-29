# MFY-G6-03-CLEAN-INSTALL-001 — Linux Clean Install Report

**Date:** 2026-08-11
**Protocol reference:** MOODIFY_AUGUST_2026_FREEZE_PROTOCOL Gate 6 — G6-03 Clean install on Linux
**Target machine:** Aliyun data node 120.55.191.146 (MFY-ALIYUN-DATA-NODE-001), Ubuntu 26.04 LTS, kernel 7.0.0-28-generic, 2 vCPU / 1.6 GiB
**Source of truth:** `ops/data_node/requirements-node.lock.txt` (55 pinned packages, Python 3.14, G6-01)

## Procedure

1. Fresh venv created at `/opt/moodify-clean-check/.venv` — no pre-existing packages.
2. `pip install -r ops/data_node/requirements-node.lock.txt` — exact pinned versions only, no `--upgrade`, no extra index.
3. `pip check` — dependency consistency verification.
4. Package install: `pip install --no-deps -e .` (deps come from the lock file only).
5. Smoke test: generate a 3 s 440/880 Hz sine WAV, run the canonical `run_production_case` (MFY-WSE-SCAN-PROFILE-001) end-to-end, verify output structure and case status.

Production services (`moodify-data-worker`, `moodify-api`, 4 timers) were left untouched — this verification ran in an isolated tree.

## Result

| Check | Result |
|---|---|
| Lock-file install (55 packages, e.g. numpy 2.4.6, scipy 1.18.0, librosa 0.11.0, pedalboard 0.9.24, fastapi 0.141.1) | PASS — all resolved at pinned versions |
| `pip check` | PASS — "No broken requirements found." |
| Package build + install (moodify 0.1.0, editable) | PASS — "Successfully installed moodify-0.1.0" |
| `import moodify` | PASS — 0.1.0 |
| Full production case on generated audio | PASS — closed loop, final status `ALGO_REVIEWED` |
| Case structure | `01_source_scan` 7 files, `02_plans` 3, `03_candidates` 6, `04_after_scan` 3, `05_comparison` 3 |

## Artifacts

- `install.log` — full pip install transcript (lock file + package)
- `smoke_test.log` — import + production-case smoke run transcript
- `case_manifest.json` — case `case_2f50f9f79d3b403a8ee3b1b8f8749f90`, source sha256 `ce05f32cce0d0cd461cb1b282193e1bdc358a59e91fd05074abcbd50512c8aea`, status `ALGO_REVIEWED`

## Notes

- Node production tree (`/opt/moodify`, `/root/venv`, `/var/lib/moodify`) was not modified; the clean environment remains at `/opt/moodify-clean-check` for future verification.
- The lock file is confirmed reproducible on Linux py3.14: a fresh machine can go from lock file to a closed-loop case with no manual intervention beyond the two pip commands.
