# MHP-064: Gate Decision — ADOPT / HOLD / REBUILD

**Status**: proposed
**Direction**: NEM-MOODIFY-STUDIO-OS-001 / Validate-6 / N (Next Entry)
**Depends on**: MHP-063 (validation report complete)
**Protocol**: NEM-18 = Build-6 + Validate-6 + Harden-6

## Context

The NEM-18 protocol requires an explicit gate decision at the end of Validate-6. This is not a code task — it's a human engineering judgment informed by real data. MHP-064 reads the validation report (MHP-063) and the failure analysis (MHP-062) and makes the call.

## Goal

Read evidence. Make decision. Document it.

### Decision options

| Decision | Meaning | Next Action |
|----------|---------|-------------|
| ADOPT | Production-ready | Enter Harden-6 immediately |
| HOLD | Good but needs fixes | Enter Harden-6 with specific fix list |
| REBUILD | Fundamentally broken | Return to Build-6 with revised scope |
| FORK | Direction split | Create two NEM children |

## Process

1. Read `reports/nem_studio_os_001/validation_report.md`
2. Read `reports/nem_studio_os_001/failure_analysis.md`
3. Check gate criteria from NEM-MOODIFY-STUDIO-OS-001 §7
4. Make decision with explicit rationale citing metrics
5. Write decision to `reports/nem_studio_os_001/gate_decision.md`
6. Update NEM-MOODIFY-STUDIO-OS-001 §8 (Final Decision)

## Acceptance Criteria
- Gate decision documented with rationale
- Decision cites specific metrics from MHP-061/062/063
- If HOLD or REBUILD: specific conditions for re-evaluation are stated
- If ADOPT: Harden-6 entry tasks are confirmed
- NEM-18 master document updated

## Done Means

The Validate-6 phase is formally closed. The node either proceeds to Harden-6 or loops back with clear reasons.
