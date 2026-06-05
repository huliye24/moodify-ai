# MHP-849: AWJ Scope and Forbidden Files Policy — Completion Report

**Generated**: 2026-06-05
**Status**: done
**E-Chain**: ECHAIN-MOODIFY-MAP-CHAIN-015 / NEM-MOODIFY-MAP-PROBE-045 / Probe Plan-6A

## Deliverables

| Artifact | Path | Status |
|----------|------|--------|
| AWJ Policy | `docs/policy/map_chain_awj_scope.md` | done |
| MHP Report | `reports/echain_moodify_map_chain_015/mhp_849_awj_scope_policy.md` | done (this file) |

## Policy Coverage

| MAP Layer | Allowed Files Defined | Role Matrix | Forbidden Files Listed |
|-----------|----------------------|-------------|----------------------|
| S Scan | 4 files | A/W/J | yes |
| A Analyze | 3 files | A/W/J | yes |
| D Diagnose | 3 files | A/W/J | yes |
| P Process | 5 files | A/W/J | yes |
| V Validate | 4 files | A/W/J | yes |
| R Report | 5 files | A/W/J | yes |
| G Generate | 3 files | A/W/J | yes |
| Policy Surface | 3 paths | A/W/J | yes |

## Forbidden Files

8 files/patterns listed with rationale:
- 4 production files (operator_api, supervisor, scheduler, cloud_worker)
- 1 sealed history pattern
- 1 cross-NEM isolation rule
- 1 security boundary (env/config)
- 1 core MRS semantics file

## Judge Gate Contract

The policy includes machine-checkable `WORKER_ALLOWED_FILES`, `ARCHITECT_ONLY_FILES`, and `FORBIDDEN_FILES` sets suitable for a Judge gate script.

## Acceptance Criteria Check

- [x] Each MAP layer (S/A/D/P/V/R/G) has a list of allowed files.
- [x] Each role (Architect/Worker/Judge) has clear read/write/approve permissions.
- [x] Forbidden files are listed with rationale.
- [x] Policy is machine-parseable (Python sets included for Judge gate).
