# MHP-070: Next NEM Entry — Generate NEM-MOODIFY-002

**Status**: proposed
**Direction**: NEM-MOODIFY-STUDIO-OS-001 / Harden-6 / N (Next Entry)
**Depends on**: MHP-069 (manifest finalized)
**Protocol**: NEM-18 = Build-6 + Validate-6 + Harden-6

## Context

The NEM-18 protocol requires every node to define the next node. NEM-MOODIFY-STUDIO-OS-001 is the first NEM node for Moodify — it proves the Studio OS works. The next node should build on this foundation.

Based on evidence from the completed NEM-18 cycle, two natural candidates emerge:

### Candidate A: NEM-MOODIFY-MRS-002 — MRS Scoring Hardening
The MRS scoring system is functional but:
- Uses pseudo-MRS as fallback when MRS Open v0.3.1 is unavailable
- over_dark detection is binary (triggered/not triggered)
- No genre-specific thresholds
- Gate thresholds are hardcoded (0.0 delta, 1.0 transient)

### Candidate B: NEM-MOODIFY-RUNTIME-003 — Runtime Worker Hardening
The runtime system runs but:
- No parallel processing (sequential only)
- No cloud worker integration (scheduler models exist, no real cloud backend)
- No progress streaming
- No automatic retry with backoff (exists in runner but untested at scale)

## Goal

Read the real evidence from this NEM-18 cycle and decide the next node. Write the NEM document and its Build-6 plan files.

## Process

1. Read `reports/nem_studio_os_001/validation_report.md` (MHP-063)
2. Read `reports/nem_studio_os_001/failure_analysis.md` (MHP-062)
3. Read `reports/nem_studio_os_001/regression_report.md` (MHP-067)
4. Read `docs/INTEGRATION_AUDIT.md` (MHP-068)
5. Identify the highest-value next investment
6. Write `docs/nem/NEM-MOODIFY-XXX-002.md` (master document)
7. Write Build-6 plan files (MHP-071→076)
8. Update PROJECT_ROADMAP.md

## Acceptance Criteria
- Next NEM node chosen with evidence-based rationale
- NEM master document written
- Build-6 plan files (6) written
- PROJECT_ROADMAP.md updated with completed and next nodes

## Done Means

The NEM-18 cycle closes cleanly. A developer opens `docs/nem/NEM-MOODIFY-XXX-002.md` and starts the next node with zero context-reconstruction cost.

> 一个工程节点不应只被写出来，而应被构建、验证、固化，并留下下一次进化的入口。
