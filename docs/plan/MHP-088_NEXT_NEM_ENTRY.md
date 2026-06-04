# MHP-088: Next NEM Entry — RUNTIME-003 or PRESET-004

**Status**: completed
**Direction**: NEM-MOODIFY-MRS-002 / Harden-6 / N1 (Next Entry)
**Depends on**: MHP-087 (manifest finalized)
**Protocol**: NEM-18 = Build-6 + Validate-6 + Harden-6

## Context

NEM-18 protocol requires every node to define the next node. NEM-MOODIFY-MRS-002 hardens the MRS scoring layer. The next logical investment depends on what MRS-002 revealed:

### Candidate A: NEM-MOODIFY-RUNTIME-003 — Runtime Worker Hardening
The runtime system was deferred in MHP-070. After MRS hardening, the next bottleneck is likely:
- Parallel processing (sequential only — 50 samples × 3 presets = hours)
- Cloud worker integration (scheduler models exist, no real backend)
- Progress streaming and automatic retry

### Candidate B: NEM-MOODIFY-PRESET-004 — Preset Library Hardening
If MRS-002 found that certain presets consistently underperform on certain genres:
- Per-genre preset optimization
- Preset parameter space exploration
- safe_air and air_preserve_master hardening

### Candidate C: NEM-MOODIFY-CALIBRATION-005 — Continuous Calibration Loop
If MRS-002 found that thresholds drift or need regular recalibration:
- Automated nightly calibration runs
- Threshold drift detection
- D_ref auto-recalibration

## Goal

Read real evidence from MRS-002 and decide the next node. Write the NEM document and its Build-6 plan files.

## Process
1. Read `reports/nem_mrs_002/calibration_report.md` (MHP-081)
2. Read `reports/nem_mrs_002/gate_accuracy/summary.md` (MHP-080)
3. Read `reports/nem_mrs_002/integration_audit.md` (MHP-086)
4. Identify the highest-value next investment
5. Write `docs/nem/NEM-MOODIFY-XXX-003.md` (master document)
6. Write Build-6 plan files (MHP-089→094)
7. Update PROJECT_ROADMAP.md

## Acceptance Criteria
- Next NEM node chosen with evidence-based rationale
- NEM master document written
- Build-6 plan files (6) written
- PROJECT_ROADMAP.md updated with MRS-002 completion and next node

## Done Means

The MRS-002 cycle closes cleanly. A developer opens `docs/nem/NEM-MOODIFY-XXX-00X.md` and starts the next node with zero context-reconstruction cost.

> 一个工程节点不应只被写出来，而应被构建、验证、固化，并留下下一次进化的入口。
