# MHP-049: CLI Parity Audit — Complete the CLI ↔ API Symmetry

**Status**: proposed
**Direction**: 6-Step Plan — V1 (Validation)
**Depends on**: MHP-048
**Protocol**: 泫榛 6-Step Plan Protocol

## Evidence

- CLI has 40+ subcommands
- API has 45 routes
- But not all CLI commands have API equivalents, and vice versa
- Some API endpoints (like `POST /calibration/reviews`) have no CLI `moodify-runtime calibration-review` command
- Need to audit and close the gaps

## Goal

Audit every public function in every subsystem. For each function, verify it has:
1. A CLI entry point (or explicit decision not to)
2. An API endpoint (or explicit decision not to)
3. At least one test

Document the gaps and close the critical ones.

## Non-Goals

- Don't add CLI commands for internal helpers
- Don't add API endpoints for functions that should stay internal

## Acceptance Criteria

- Parity audit document listing all public functions × (CLI, API, test) status
- Critical gaps closed (functions with neither CLI nor API)
- Existing 95 tests still pass
- New CLI/API tests where gaps were closed

## Test Plan
```bash
python3 -m pytest moodify_runtime/tests/ -q
```
