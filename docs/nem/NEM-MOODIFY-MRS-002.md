# NEM-MOODIFY-MRS-002: MRS Scoring Hardening

## 1. Node Metadata

- **NEM ID**: NEM-MOODIFY-MRS-002
- **Owner**: Raphael Davad
- **Project**: Moodify
- **Status**: EXPERIMENT
- **Start Date**: 2026-06-04
- **Target Gate**: ADOPT
- **Protocol**: NEM-18 = Build-6 + Validate-6 + Harden-6
- **Parent Node**: NEM-MOODIFY-STUDIO-OS-001 (ADOPT ✅)

## 2. Node Purpose

NEM-MOODIFY-STUDIO-OS-001 proved the Studio OS works end-to-end. During that node, three MRS-scoring weaknesses surfaced:

1. **over_dark detection is binary** — a single boolean flag decides "reprocess." No graduated measurement of how dark is "too dark."
2. **Gate thresholds are hardcoded** — `mrs_score_delta ≥ 0.0`, `transient_damage ≤ 1.0`, `loudness_penalty ≤ 1.0`. These have never been tuned against real data.
3. **pseudo_mrs is a placeholder** — the formula in `metrics.py:216` has `peak_score`, `rms_score`, `crest_score`, `dc_score` weights that were chosen by intuition, not calibration.
4. **No genre-specific thresholds** — a piano track and an electronic track go through the same gate. This cannot be correct.
5. **MRS Open v0.3.1 D_ref is static** — `0.274350`, set once, never recalibrated.

This node hardens the MRS scoring layer so that gate decisions are backed by calibrated thresholds, genre-aware logic, and graduated over_dark detection — not intuition and binary flags.

## 3. Build-6: MRS Calibration Infrastructure

| Step | Type | MHP | Task | Status |
|------|------|-----|------|--------|
| B1 | E | 071 | Genre-specific threshold configuration — YAML with per-genre defaults | ✅ |
| B2 | E | 072 | Graduated over_dark detector — 3-level (none/mild/severe) replacing binary flag | ✅ |
| B3 | V | 073 | Pseudo-MRS weight calibration — run grid search on calibration data | ✅ |
| B4 | V | 074 | Gate threshold unit tests — 16 tests, all paths covered | ✅ |
| B5 | S | 075 | MRS calibration guide — 6 sections, operator-ready | ✅ |
| B6 | N | 076 | Generate Validate-6 entry from Build-6 evidence | ✅ |

## 4. Validate-6: Calibration Dataset & Live Audit

| Step | Type | MHP | Task |
|------|------|-----|------|
| V1 | E | 077 | Build calibration dataset — 50+ labeled samples across 5 genres |
| V2 | E | 078 | Run calibration pipeline — before/after MRS, gate decisions, human labels |
| V3 | V | 079 | Compare calibrated MRS vs pseudo-MRS — correlation, agreement rate |
| V4 | V | 080 | Gate accuracy analysis — false positive/negative rates per genre |
| V5 | S | 081 | Generate calibration report with per-genre metrics and recommendations |
| V6 | N | 082 | Gate decision: ADOPT / HOLD / REBUILD for MRS scoring |

## 5. Harden-6: MRS Production Hardening

| Step | Type | MHP | Task |
|------|------|-----|------|
| H1 | E | 083 | Fix calibration issues exposed by Validate-6 |
| H2 | E | 084 | Refactor MRS scoring engine — configurable thresholds, genre dispatch |
| H3 | V | 085 | Full regression — all 129+ Studio OS tests + new MRS tests |
| H4 | V | 086 | Integration audit — CLI ↔ API ↔ Console ↔ Calibration alignment |
| H5 | S | 087 | Finalize MRS manifest — thresholds doc, D_ref audit, version bump |
| H6 | N | 088 | Generate next NEM entry (NEM-MOODIFY-RUNTIME-003 or NEM-MOODIFY-PRESET-004) |

## 6. Runtime Plan

```yaml
runtime:
  mode: unattended
  max_duration_hours: 48
  failure_policy: stop_after_5_consecutive_failures
  output_dir: outputs/nem_mrs_002/
  log_dir: logs/nem_mrs_002/
  report_dir: reports/nem_mrs_002/
  calibration_samples: 50
  genres: [electronic, piano, vocal, rock, ambient]
  presets: [warm_vocal, clean_master, wide_space]
```

## 7. Gate Criteria

| Criterion | Threshold | Method |
|-----------|-----------|--------|
| Build-6 completion | 6/6 tasks done | All tests green |
| Genre thresholds | 5 genres with distinct thresholds | YAML config |
| over_dark detection | 3-level graduated (none/mild/severe) | Unit test |
| Calibration dataset | ≥50 labeled samples | Registry count |
| Pseudo-MRS vs calibrated correlation | r ≥ 0.7 | Statistical test |
| Gate accuracy | ≥85% match with human labels | GateAudit |
| Regression | All 129+ Studio OS tests pass | Full pytest |
| Documentation | MRS calibration guide written | Manual review |
| Next entry | Defined and scoped | NEM document |

## 8. Final Decision

To be filled after Validate-6 and Harden-6 complete.

- **Decision**: PENDING
- **Reason**: —
- **Next node**: —

---

> 一个工程节点不应只被写出来，而应被构建、验证、固化，并留下下一次进化的入口。
