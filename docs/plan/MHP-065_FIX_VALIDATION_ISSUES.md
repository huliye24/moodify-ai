# MHP-065: Fix Validation Issues — Patch Failures Found in 6h Run

**Status**: proposed
**Direction**: NEM-MOODIFY-STUDIO-OS-001 / Harden-6 / E (Execution)
**Depends on**: MHP-064 (Gate Decision: ADOPT or HOLD)
**Protocol**: NEM-18 = Build-6 + Validate-6 + Harden-6

## Context

MHP-062 classified every failure from the 6h unattended run. MHP-064 made the gate decision. Harden-6 begins by fixing the highest-priority issues. This is not "add new features" — it's "make what we have reliable."

## Goal

Fix every issue classified as CRITICAL or HIGH in the failure analysis. For MEDIUM issues, fix if the fix is clear and low-risk. For LOW issues, document and defer.

### Fix priority (from MHP-062 taxonomy)

| Priority | Action |
|----------|--------|
| CRITICAL | Fix immediately, add regression test |
| HIGH | Fix in this task, add regression test |
| MEDIUM | Fix if fix is ≤30 min; otherwise document and defer |
| LOW | Document in known issues, defer to next NEM |

## Non-Goals

- Don't add new features
- Don't refactor working code (MHP-066 does that)
- Don't change the API contract
- Don't remove functionality

## Acceptance Criteria
- All CRITICAL issues fixed and verified
- All HIGH issues fixed and verified
- MEDIUM issues either fixed or documented with deferral reason
- Every fix has a regression test
- Existing 107+ tests still pass
- Fix log written to `reports/nem_studio_os_001/fix_log.md`

## Test Plan
```bash
python3 -m pytest moodify_runtime/tests/ -v
```

## Done Means

The issues that could block production adoption are resolved. The system is more reliable than it was before Validate-6.
