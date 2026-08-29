# IMP-012 — Create traceability integrity checker

Promoted from `WI-012` after `TP-305` unattended-safety selection.

## Objective

Checker rejects missing source, measurement, evidence, schema-version, or verification links and produces a reusable evidence report.

## Allowed paths

- `tools/ear_v1_contracts`
- `tests/ear_v1_contracts`

## Required workspace outputs

- `tools/ear_v1_contracts/check_traceability.py`
- `tests/ear_v1_contracts/test_traceability_checker.py`

## Safety and acceptance

- Follow the root `AGENTS.md` authority and product identity.
- Modify only the allowed paths and their necessary package initializers.
- Do not process private audio, publish, deploy, change credentials, change Git
  remotes, delete legacy code, or promote experimental capability.
- Use JSON Schema Draft 2020-12 unless an existing repository convention proves
  another draft authoritative.
- Add focused tests and run the complete `tests/ear_v1_contracts` suite.
- Preserve failure evidence. Do not edit `TASK_LEDGER.json`; the wrapper owns it.
