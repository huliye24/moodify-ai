# Moodify Failure and Boundary Ledger

**Created:** 2026-07-30
**Purpose:** Preserve failure symptom, trigger, affected versions, reproduction, containment, fix, regression test, and residual risk for every engineering-hardening cycle.
**Part of:** ECHAIN-MOODIFY-THICKNESS-016 / DSK-MFY-THICKNESS-001

---

## FL-001: Treatment Summary Staleness — Count Mismatch

| Field | Value |
|---|---|
| **Date discovered** | 2026-07-30 |
| **Symptom** | Derived summary (`summary.json`) claimed 30 records and 6 completed feedback items; source directory contained 27 treatment records and 3 completed feedback items |
| **Trigger** | Three treatment records were renamed from `.json` to `.bak` (intentionally excluded from aggregation) without regenerating the derived summary |
| **Affected versions** | v2.0.0-mvp-dirty, HEAD `b4bb5ef1` |
| **Reproduction** | `python -c "import json; s=json.load(open('treatment_records/summary.json')); print(s['record_count'])"` returned 30 while source scan returned 27 |
| **Containment** | Re-ran the aggregator: `python scripts/v01_aggregate_treatment_records.py`. Summary now matches source. |
| **Fix** | Regenerated summary from authoritative source files. Added `scan_absent_records()` to track intentionally excluded `.bak` files. Added backup-before-overwrite to prevent data loss during regeneration. |
| **Regression test** | Aggregator re-run produces 27 records, 3 completed; `known_absent` field lists the 3 `.bak` files. SHA-256 of JSON output is deterministic across runs. |
| **Residual risk** | The aggregator must be re-run whenever treatment records are added, removed, or renamed. This is currently a manual step. |

## FL-002: Windows Encoding — GBK Default Breaks UTF-8 Files

| Field | Value |
|---|---|
| **Date discovered** | 2026-07-30 |
| **Symptom** | Three treatment records (`mhp026_ai_vocal_001_*.json`) failed to parse when read without explicit UTF-8 encoding on Windows (system default: GBK) |
| **Trigger** | `open(path)` without `encoding="utf-8"` on Windows platform |
| **Affected versions** | v2.0.0-mvp-dirty, HEAD `b4bb5ef1` |
| **Reproduction** | `python -c "json.load(open('treatment_records/mhp026_ai_vocal_001_clean_master.json'))"` raised `UnicodeDecodeError` |
| **Containment** | The production aggregator (`v01_aggregate_treatment_records.py`) already uses `encoding="utf-8"`. The hardening gates module also uses `encoding="utf-8"`. |
| **Fix** | Verified all file I/O in aggregator and hardening modules uses explicit `encoding="utf-8"`. Added test: `test_malformed_json_does_not_crash`. |
| **Regression test** | All 27 records load without error when using explicit UTF-8. Test verifies malformed JSON does not crash the scanner. |
| **Residual risk** | Future modules added without explicit UTF-8 encoding will have the same failure on Windows. Standard review should enforce `encoding="utf-8"` on all `open()` calls. |

## FL-003: Craft Write-Back Without Gate

| Field | Value |
|---|---|
| **Date discovered** | 2026-07-30 |
| **Symptom** | `write_manifest()` in `craft_evidence.py` wrote manifests to disk without checking whether the run succeeded, had errors, or had rights clearance |
| **Trigger** | Manifest with step errors could be persisted identically to a clean manifest |
| **Affected versions** | v2.0.0-mvp-dirty, HEAD `b4bb5ef1` |
| **Reproduction** | Created a manifest with a step error and wrote it to disk — no rejection occurred |
| **Containment** | Added `can_write_back()` predicate that checks: no step errors, complete steps, rights cleared, and human approval (when required) |
| **Fix** | `craft_evidence.py` now exports `can_write_back(manifest, rights_cleared, human_approved) -> (bool, str)` |
| **Regression test** | 6 tests in `tests/test_craft_evidence.py::TestCanWriteBack` covering: clean pass, step error rejection, incomplete rejection, no-rights rejection, human-approval-required rejection, no-steps rejection, zero-total-steps rejection |
| **Residual risk** | `write_manifest()` is not gated automatically — callers must invoke `can_write_back()` before writing. This is by design but requires discipline. |

## FL-004: MRS as Sole Release Authority

| Field | Value |
|---|---|
| **Date discovered** | 2026-07-30 |
| **Symptom** | MRS gate accuracy is 9.1%, pseudo-MRS preference correlation is ~0.19, MRS Open agreement is ~60.6%. No code-level gate prevented MRS from being treated as sound-quality release authority. |
| **Trigger** | Audited MRS historical metrics against release requirements |
| **Affected versions** | All versions with MRS-based gates |
| **Reproduction** | N/A — design gap, not runtime failure |
| **Containment** | Created `mrs_can_release()` function in `hardening_gates.py` that requires explicit `human_approved=True`. MRS scores alone return `(False, reason)`. |
| **Fix** | `mrs_can_release(mrs_score, human_approved)` — returns False without human approval. `MRS_AUTHORITY_STATEMENT` documents the metric limitations. |
| **Regression test** | 4 tests in `tests/test_hardening_gates.py::TestMrsCanRelease` covering: MRS-alone rejection, human-approval pass, None-score rejection, authority statement contains metrics |
| **Residual risk** | Callers must use this gate before promoting results. There is no runtime enforcement in existing processing pipelines — this is a new gate that existing code does not yet call. |

---

## Ledger Summary

| ID | Severity | Status | Regression test |
|---|---|---|---|
| FL-001 | P0 | RESOLVED | Deterministic aggregator output |
| FL-002 | P1 | CONTAINED | UTF-8 encoding test |
| FL-003 | P0 | RESOLVED | can_write_back tests |
| FL-004 | P0 | RESOLVED | mrs_can_release tests |

## Independent Audit Correction — 2026-07-30

The Session 002 status above is superseded as follows:

- FL-003 is `OPEN`: `can_write_back()` is not called by the real Craft Library write paths.
- FL-004 is `OPEN`: `mrs_can_release()` is not called by delivery or approval boundaries.
- A predicate with unit tests is containment research, not production enforcement.
- `.bak` artifacts are excluded from active aggregation, but the suffix alone does not prove why they were excluded.
- Rights must not be inferred from `human_feedback.status`; the authoritative machine input is now `docs/product/daily/2026-07-30/validation_set_rights.json`.
