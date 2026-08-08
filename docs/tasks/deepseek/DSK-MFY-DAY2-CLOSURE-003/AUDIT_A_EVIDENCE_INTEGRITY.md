# AUDIT A — Static Evidence Integrity Audit

**Task**: DSK-MFY-DAY2-CLOSURE-003  
**Date**: 2026-07-31  
**Status**: COMPLETE — ALL CHECKS PASSED

## A1. VSR-001 Rights Gate Markdown vs JSON Consistency

- **gate_id**: `VSR-001` — MATCH (both MD and JSON)
- **confirmed_by**: `user_in_current_codex_task` (JSON) / "用户（当前 Codex 任务中的授权确认人）" (MD) — CONSISTENT
- **confirmed_at**: `2026-07-31T08:45:00+08:00` (JSON) / `2026-07-31 08:45:00 +08:00` (MD) — CONSISTENT (ISO 8601 variants)
- **scope**: `internal_validation_only` — MATCH with MD Section 1
- **Assets**: All 5 (VS-001 through VS-005) present in both formats, all status=`ready`

**Result**: PASS. No discrepancy between Markdown and JSON.

## A2. Five Source Files — Existence and SHA-256

| ID | Exists | Size (bytes) | SHA-256 |
|---|---|---|---|
| VS-001 | True | 34,429,612 | MATCH |
| VS-002 | True | 4,991,948 | MATCH |
| VS-003 | True | 2,508,563 | MATCH |
| VS-004 | True | 6,646,380 | MATCH |
| VS-005 | True | 5,865,189 | MATCH |

**Result**: PASS. All files present. All SHA-256 match `VALIDATION_SET_V0.1.md` Section 3.

## A3. VS-001 Format Properties (ffprobe)

- **Codec**: pcm_s16le (matches "WAV/PCM 16-bit" in manifest)
- **Sample rate**: 48,000 Hz (matches manifest)
- **Channels**: 2 (matches manifest)
- **Duration**: 179.320 s (matches manifest)
- **Size**: 34,429,612 bytes (matches manifest)

**Result**: PASS. All properties consistent with `VALIDATION_SET_V0.1.md` and `TRIAL_PREFLIGHT_REPORT.md`.

## A4. Original Run JSON Parseability

All 4 critical JSON files in `outputs/daily_runs/20260731_vs001_trial/` parse successfully:
- `process/metadata.json` — OK
- `process/manifest.json` — OK
- `process/validation_report.json` — OK
- `treatment_record.json` — OK

**Result**: PASS.

## A5. Process Manifest Artifact Integrity

All 5 manifest artifacts verified against actual files:

| Artifact | Size Match | SHA-256 Match |
|---|---|---|
| `warm_vocal.wav` | MATCH | MATCH |
| `_report.json` | MATCH | MATCH |
| `_report.pdf` | MATCH | MATCH |
| `before_spectrum.png` | MATCH | MATCH |
| `after_spectrum.png` | MATCH | MATCH |

MAP_CHAIN_VERSION content: `map_chain_v0.2.0` — MATCH (trailing newline diff in `diff` is false flag).

**Result**: PASS.

## A6. Metadata Code Identity

| Field | Metadata Value | Current Value | Match |
|---|---|---|---|
| git_hash | `df3a8a3...` | `df3a8a3...` | Yes |
| git_branch | `codex/mainline-cloud-dev-20260603` | Same | Yes |
| python_version | 3.11.9 | 3.11.9 | Yes |
| map_chain_version | 0.2.0 | — | Consistent |
| input_sha256 | `27bea8e0...` | — | Matches VS-001 source |

**WARNING (P2)**: Working tree is dirty (38 modified tracked files, numerous untracked files). Git hash identifies the commit but does NOT capture uncommitted changes. Full reproducibility requires git diff or stash snapshot of working tree state at run time.

**Result**: PASS with noted limitation.

## A7. Treatment Record Path Existence

All 6 referenced paths exist and are readable:
- `before_audio` — exists
- `after_audio` — exists
- `inspector_metrics` — exists
- `matched_after_audio` — exists
- `inspector_report_md` — exists
- `inspector_report_html` — exists

**Result**: PASS.

## A8. Cross-Document Metric Consistency

`dynamic_range_delta_db = -7.61` confirmed identical across:
- `validation_report.json` (process)
- `metrics_comparison.json` (inspector)
- `treatment_record.json`
- `TRIAL_PREFLIGHT_REPORT.md`

Also consistent across all three JSON files:
- `peak_delta_db = 3.7`, `rms_delta_db = 5.89`, `mrs_delta = 24.82`
- `dynamic_damage` risk flag present in all locations
- `damage_loss = 0.208` consistent

**Result**: PASS. No metric disagreement between files.

## A9. Blind A/B File Identity

| File | SHA-256 | Identity Confirmed |
|---|---|---|
| A.wav | `27bea8e0...` | = Source (VS-001) |
| B.wav | `014e2ae8...` | = `after_matched.wav` |
| A.wav size | 34,429,612 | = Source size |
| B.wav size | 34,294,484 | = after_matched size |

**Result**: PASS. A.wav is byte-identical to source; B.wav is byte-identical to inspector's after_matched.wav.

## A10. Mapping Seed Reproducibility

- Seed: `20260731|VS-001|warm_vocal|round-01`
- Seed SHA-256: `4696473a...` — MATCH with `TRIAL_PREFLIGHT_REPORT.md`
- First byte: 70 (even) → A=Before, B=After Matched
- Mapping file at `blind/_mapping/round-01.json` independently records same rule
- Mapping directory physically separate from scoring materials (`blind/round-01/`)

**Result**: PASS. Seed, hash, rule, and mapping all independently reproducible.

## Batch A Summary

| Check | Result |
|---|---|
| A1 Rights MD/JSON | PASS |
| A2 Source SHA-256 | PASS |
| A3 Format properties | PASS |
| A4 JSON parseable | PASS |
| A5 Manifest artifacts | PASS |
| A6 Metadata identity | PASS (P2: dirty tree) |
| A7 TR paths | PASS |
| A8 Metric consistency | PASS |
| A9 A/B identity | PASS |
| A10 Mapping seed | PASS |

**Batch A Conclusion: PASS. All evidence files are internally consistent, hash-verified, and traceable.**
