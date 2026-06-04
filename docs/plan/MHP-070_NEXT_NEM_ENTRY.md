# MHP-070: Next NEM Entry — Generate NEM-MOODIFY-002

**Status**: completed
**Direction**: NEM-MOODIFY-STUDIO-OS-001 / Harden-6 / N (Next Entry)
**Depends on**: MHP-069 (manifest finalized)
**Protocol**: NEM-18 = Build-6 + Validate-6 + Harden-6

## Context

The NEM-18 protocol requires every node to define the next node. NEM-MOODIFY-STUDIO-OS-001 is the first NEM node for Moodify — it proves the Studio OS works. The next node should build on this foundation.

Based on evidence from the completed NEM-18 cycle, two natural candidates emerged.

## Decision

### Winner: **NEM-MOODIFY-MRS-002 — MRS Scoring Hardening** 🏆

**Rationale**:
1. The MRS scoring system is functional but relies on pseudo-MRS as fallback
2. over_dark detection is binary only (triggered/not triggered)
3. No genre-specific thresholds
4. Gate thresholds are hardcoded (0.0 delta, 1.0 transient)
5. The validation run showed MRS metrics are computed but not calibrated
6. MRS quality directly impacts every gate decision — it's the most leveraged fix

### Runner-up: NEM-MOODIFY-RUNTIME-003 — Runtime Worker Hardening
- Deferred because: Runtime works reliably (0 crashes in 129 tests). Parallel processing and cloud workers are feature additions, not production blockers. MRS calibration will benefit Runtime quality more than Runtime hardening will benefit MRS quality.

## Next Node: NEM-MOODIFY-MRS-002

### 6-Step Development Plan (NEM-18)

**Build-6: MRS Threshold Hardening**
- E1: Genre-specific MRS threshold configuration
- E2: over_dark graduated detection (not binary)
- V1: MRS calibration dataset with 50+ labeled samples
- V2: Gate threshold tuning from calibration data
- S1: MRS scoring documentation and calibration guide
- N1: Next cycle entry

**Validate-6: MRS Production Calibration**
- E1: Deploy calibrated MRS thresholds
- E2: 100-sample validation dataset with human labels
- V1: Compare calibrated MRS vs pseudo-MRS on 100 samples
- V2: Gate decision accuracy analysis
- S1: Calibration report with per-genre metrics
- N1: Gate decision

**Harden-6: MRS Production Hardening**
- E1: Fix issues found in Validate-6
- E2: Refactor MRS scoring engine for configurable thresholds
- V1: Full regression
- V2: Integration audit
- S1: Finalize manifest
- N1: Next NEM entry

### Gate Criteria

| Criterion | Threshold | Method |
|-----------|-----------|--------|
| Genre-specific thresholds | ≥5 genres | Config + test |
| over_dark detection | 3-level (none/mild/severe) | Graduated logic |
| Calibration dataset | ≥50 labeled samples | Ground truth |
| MRS vs pseudo-MRS correlation | r ≥ 0.7 | Statistical test |
| Gate accuracy | ≥85% match with human labels | Validation |
| Regression | All 129+ tests pass | Full pytest |

## Updated PROJECT_ROADMAP.md

See PROJECT_ROADMAP.md for the full NEM-18 progress and next node plan.

---

> 一个工程节点不应只被写出来，而应被构建、验证、固化，并留下下一次进化的入口。
