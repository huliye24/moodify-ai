# IMP-008 — Add deterministic synthetic fixture definitions

Promoted from `WI-008` after `TP-305` unattended-safety selection.

## Objective

Definitions are parameter-only, reproducible, contain no private audio, and cover silence, tone, impulse, clipping, phase inversion, and lossless rewrap controls.

## Allowed paths

- `configs/ear_v1`
- `tests/ear_v1_contracts`

## Required workspace outputs

- `configs/ear_v1/synthetic_fixtures.json`
- `tests/ear_v1_contracts/test_fixture_definitions.py`

## Safety and acceptance

- Follow the root `AGENTS.md` authority and product identity.
- Modify only the allowed paths and their necessary package initializers.
- Do not process private audio, publish, deploy, change credentials, change Git
  remotes, delete legacy code, or promote experimental capability.
- Use JSON Schema Draft 2020-12 unless an existing repository convention proves
  another draft authoritative.
- Add focused tests and run the complete `tests/ear_v1_contracts` suite.
- Preserve failure evidence. Do not edit `TASK_LEDGER.json`; the wrapper owns it.
