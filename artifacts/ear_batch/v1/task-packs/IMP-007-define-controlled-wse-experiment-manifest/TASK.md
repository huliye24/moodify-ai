# IMP-007 — Define controlled WSE experiment manifest

Promoted from `WI-007` after `TP-305` unattended-safety selection.

## Objective

Manifest distinguishes transform, expected sensitivity/invariance, tolerances, negative controls, and evidence outputs.

## Allowed paths

- `schemas/ear_v1`
- `tests/ear_v1_contracts`

## Required workspace outputs

- `schemas/ear_v1/wse_experiment.schema.json`
- `tests/ear_v1_contracts/test_wse_experiment_schema.py`

## Safety and acceptance

- Follow the root `AGENTS.md` authority and product identity.
- Modify only the allowed paths and their necessary package initializers.
- Do not process private audio, publish, deploy, change credentials, change Git
  remotes, delete legacy code, or promote experimental capability.
- Use JSON Schema Draft 2020-12 unless an existing repository convention proves
  another draft authoritative.
- Add focused tests and run the complete `tests/ear_v1_contracts` suite.
- Preserve failure evidence. Do not edit `TASK_LEDGER.json`; the wrapper owns it.
