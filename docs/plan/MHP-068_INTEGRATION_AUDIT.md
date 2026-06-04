# MHP-068: Integration Audit — CLI ↔ API ↔ Console ↔ Runtime Alignment

**Status**: completed
**Direction**: NEM-MOODIFY-STUDIO-OS-001 / Harden-6 / V (Validation)
**Depends on**: MHP-067 (regression passed)
**Protocol**: NEM-18 = Build-6 + Validate-6 + Harden-6

## Context

Studio OS has four interfaces:
- **CLI** (45 subcommands, `cli.py`)
- **API** (45 routes, `operator_api.py`)
- **Console** (8 views, `operator_console.html`)
- **Runtime** (`run_daily`, `runner.py`)

They should be symmetric: every CLI command should have an API route, every API route the Console uses should have a contract test, and the Runtime should be reachable from all three interfaces.

But we've never systematically verified this symmetry. MHP-049 did a partial audit of CLI functions. MHP-044 verified Console↔API contracts. But no audit covers all four interfaces together.

## Goal

Produce an integration audit document that:

1. Lists every public function across all 17 modules
2. Shows which interfaces expose it (CLI, API, Console, Runtime)
3. Flags gaps where a function is exposed through one interface but not others
4. Verifies that the 8 Console views use only contract-tested API endpoints
5. Verifies that `run_operator_job --live` is reachable from CLI, API, and Console

## Acceptance Criteria
- Integration audit document: `docs/INTEGRATION_AUDIT.md`
- 4-interface coverage matrix for every public function
- All gaps documented with explicit decisions (not accidental omissions)
- Console views verified to only call contract-tested endpoints
- Existing tests still pass

## Done Means

A developer can see at a glance which interfaces expose which functions, and whether any capability is accidentally hidden.
