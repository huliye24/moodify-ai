# IMP-006 — Build provenance manifest utility

Promoted from `WI-006` after `TP-305` unattended-safety selection.

## Objective

Utility hashes immutable inputs, records versions and parameters, writes atomically, and detects later source drift.

## Allowed paths

- `tools/ear_v1_contracts`
- `tests/ear_v1_contracts`

## Required workspace outputs

- `tools/ear_v1_contracts/provenance.py`
- `tests/ear_v1_contracts/test_provenance.py`

## Safety and acceptance

- Follow the root `AGENTS.md` authority and product identity.
- Modify only the allowed paths and their necessary package initializers.
- Do not process private audio, publish, deploy, change credentials, change Git
  remotes, delete legacy code, or promote experimental capability.
- Use JSON Schema Draft 2020-12 unless an existing repository convention proves
  another draft authoritative.
- Add focused tests and run the complete `tests/ear_v1_contracts` suite.
- Preserve failure evidence. Do not edit `TASK_LEDGER.json`; the wrapper owns it.
