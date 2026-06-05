# MHP-849: AWJ Scope and Forbidden Files Policy

**Status**: done
**Direction**: ECHAIN-MOODIFY-MAP-CHAIN-015 / NEM-MOODIFY-MAP-PROBE-045 / Probe Plan-6A: Governance / S5
**Depends on**: MHP-845 (Current State Audit), MHP-846 (Interface Contract)
**Protocol**: AWJ Stack + E-Chain 54

## Context

MAP-Chain spans v01 core, MRS engine, craft operations, PDF reports, and runtime infrastructure. The AWJ (Architect/Worker/Judge) stack needs a clear, machine-checkable file scope policy so Workers cannot accidentally modify core scoring or gate logic.

## Goal

Define the canonical allowed/forbidden file policy for each MAP layer and AWJ role, in a format that can be parsed by a Judge gate script.

## Scope

Allowed: `docs/policy/map_chain_awj_scope.md`, `reports/echain_moodify_map_chain_015/*`
Forbidden: no code changes.

## Expected Output

`docs/policy/map_chain_awj_scope.md`
`reports/echain_moodify_map_chain_015/mhp_849_awj_scope_policy.md`

## Acceptance Criteria

- Each MAP layer (S/A/D/P/V/R/G) has a list of allowed files.
- Each role (Architect/Worker/Judge) has clear read/write/approve permissions.
- Forbidden files are listed with rationale.
- Policy is parseable as a JSON or YAML allowlist.
