# MHP-063: Validation Report — Metrics, Decisions, Recommendations

**Status**: proposed
**Direction**: NEM-MOODIFY-STUDIO-OS-001 / Validate-6 / S (Systemization)
**Depends on**: MHP-062 (failure analysis complete)
**Protocol**: NEM-18 = Build-6 + Validate-6 + Harden-6

## Context

Validate-6 has produced real data: processing metrics, MRS distributions, gate decisions, failure classifications. This data must be synthesized into a decision-support document that answers one question: **Should Studio OS proceed to production?** (Gate: ADOPT / HOLD / REBUILD)

## Goal

Produce a validation report covering:

1. **Executive summary**: one paragraph on whether the system is production-ready
2. **Test configuration**: what was tested, sample count, preset coverage, duration
3. **Key metrics**:
   - Success rate (% tasks with status=done)
   - Mean MRS delta per preset
   - over_dark trigger rate
   - Mean processing time per sample
   - Peak memory usage
4. **Failure summary**: top failure classes with counts
5. **Preset comparison**: which preset performs best on which genre
6. **Gate recommendation**: ADOPT / HOLD / REBUILD with evidence
7. **Harden-6 priorities**: what must be fixed before production

## Acceptance Criteria
- Validation report written to `reports/nem_studio_os_001/validation_report.md`
- Report includes all 7 sections above
- Gate recommendation is evidence-based (cites specific metrics)
- Report is readable by an operator who didn't run the test

## Test Plan
```bash
# Verify report exists and has required sections
grep -c "Executive Summary" reports/nem_studio_os_001/validation_report.md
grep -c "Gate Recommendation" reports/nem_studio_os_001/validation_report.md
```

## Done Means

A project stakeholder can read one document and decide whether to ADOPT Studio OS Alpha.
