# DSK-MFY-ONE-POINT-006 Failure Ledger

No bugs found during implementation. All failures are by-design behaviors.

## FL-OP-001: spec_identity not deterministic (resolved)

- **Stage:** 3 (dual-run testing)
- **Severity:** Bug — fixed
- **Root cause:** spec_identity hash included the random spec_id UUID, making it non-deterministic across runs.
- **Fix:** Hash only semantic fields (essence, protect, allow, avoid, owner, source), excluding UUIDs and timestamps.
- **Verified:** Dual-run normalized comparison now IDENTICAL.

## Known Design Limitations (not bugs)

1. Conflict detection is keyword-based; cannot detect semantic conflicts (e.g., "more presence" vs "natural dynamics").
2. `refine prepare` does not generate audio; the `prepare` suffix is honest.
3. Promotion atomicity (from HARDENING-005) inherited but not re-tested here.
