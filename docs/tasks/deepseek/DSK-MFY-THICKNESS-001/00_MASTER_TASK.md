# DSK-MFY-THICKNESS-001 — Moodify Engineering Thickness Sprint

**Created:** 2026-07-30  
**Purpose:** turn the features verified today into durable, auditable industrial-software assets.  
**Execution rule:** no claim is complete until code, tests, evidence, recovery behavior, and an engineering log agree.

## 1. Outcome

This sprint does not add a new consumer feature. It strengthens the current Moodify music-processing infrastructure through the five-pass hardening model:

1. Correctness;
2. Failure and boundary behavior;
3. Repeatability and determinism;
4. Compatibility and recovery;
5. Inheritance and institutional memory.

The sprint is complete only when every accepted issue has one of these terminal states:

- `IMPLEMENTED_AND_VERIFIED` — code or documentation changed and its acceptance check passed;
- `EVIDENCED_NO_CHANGE` — evidence proves that no change is needed;
- `BLOCKED_BY_HUMAN_AUTHORITY` — only for rights approval or professional listening judgment, with the exact owner and required decision recorded.

`RECOMMENDED`, `REVIEWED`, `MOSTLY_DONE`, and unverified code are not completion states.

## 2. Current Evidence Baseline

- Branch: `codex/mainline-cloud-dev-20260603`
- HEAD: `b4bb5ef1d511169f315e10d18f4d6a27827d67e9`
- Descriptive state: `v2.0.0-mvp-dirty`
- Python: `3.11.9`
- Current smoke evidence: Core `113 passed`, Runtime `43 passed`, Workspace `41 passed`; total `197 passed, 0 failed`.
- Treatment source of truth: `27` records and `3` completed feedback records.
- Stale summary claim: `30` records and `6` feedback records.
- Missing expected records: `electronic_wide_space.json`, `piano_clean_master.json`, `vocal_folk_warm_vocal.json`.
- MHP-026 rights gate: five candidate tracks remain pending; no audio processing is authorized.
- Historic MRS risks: gate accuracy `9.1%`, pseudo-MRS preference correlation approximately `0.19`, MRS Open agreement approximately `60.6%`.

## 3. Role Separation

### DeepSeek — bounded audit worker

DeepSeek receives one JSONL task per call. It must identify one concrete issue or certify that no issue exists, cite only supplied evidence, propose a bounded implementation action, and define a machine-checkable acceptance test. It must not edit code, redesign product direction, fabricate missing evidence, or approve audio rights.

### Codex / engineer — implementation owner

The implementation owner validates DeepSeek findings against the repository, rejects unsupported claims, makes accepted changes, adds tests, executes the required checks, and creates evidence artifacts.

### Judge — independent gate

The Judge checks the diff, test results, logs, and acceptance matrix. The Judge may return `PASS`, `REWORK`, or `HUMAN_BLOCKED`. The implementer may not self-promote an incomplete item to `PASS`.

### Human owner — non-delegable decisions

Only the authorized human may approve source-audio rights and professional listening judgments. Neither DeepSeek nor automated scores may substitute for this authority.

## 4. Full Work Breakdown

| Phase | Deliverable | Exit gate |
|---|---|---|
| A. Intake | frozen baseline, task manifest, rights constraints | inputs are traceable and no unauthorized audio is touched |
| B. DeepSeek audit | 18 schema-valid findings in `model_outputs.jsonl` | every output validates; unsupported findings are rejected |
| C. Triage | accepted/rejected/merged decision ledger | every finding has evidence and an owner |
| D. Implementation | minimal patches, tests, docs, migration/recovery notes | accepted items reach terminal state |
| E. Verification | targeted tests, full relevant suites, repeat run, failure injection | zero unexplained failures and stable rerun evidence |
| F. Inheritance | engineering log, failure ledger, standard ledger, product-history entry | a future maintainer can reconstruct why and how |

## 5. Today’s Four-Hour Execution Window

Today is the preparation and audit-start window, not a false promise that all hardening can fit into four hours.

| Time | Work | Required artifact |
|---|---|---|
| 00:00–00:30 | Freeze baseline and validate task pack | manifest and validation output |
| 00:30–02:00 | Run 18 DeepSeek audit tasks sequentially | raw outputs, rejected outputs, run summary |
| 02:00–03:15 | Human/Codex evidence triage | validated decision ledger |
| 03:15–04:00 | Select first implementation batch and write exact acceptance commands | implementation queue and engineering log |

No repository implementation is declared complete today unless its code, tests, rerun, and log all finish inside this window.

## 6. Non-Negotiable Completion Standard

- Do not weaken, skip, or delete a failing test to obtain green status.
- Do not fabricate the three missing Treatment Records.
- Do not process the five rights-pending tracks.
- Do not allow MRS alone to release or reject sound quality.
- Preserve raw commands, timestamps, exit codes, and artifact paths.
- Run each determinism-sensitive check at least twice with identical inputs.
- Test failure paths, interruption, retry, and partial artifact cleanup where applicable.
- Update an inheritance artifact for every accepted engineering change.
- Any scope reduction must be explicitly marked `DEFERRED`, with reason, risk, and owner; it is not completion.

## 7. Commands

Dry-run pack validation:

```powershell
python scripts/deepseek_worker_client.py `
  --task-file docs/tasks/deepseek/DSK-MFY-THICKNESS-001/tasks.jsonl `
  --prompt-file docs/tasks/deepseek/DSK-MFY-THICKNESS-001/03_DEEPSEEK_SYSTEM_PROMPT.md `
  --schema-file docs/tasks/deepseek/DSK-MFY-THICKNESS-001/expected_output_schema.json `
  --output-dir reports/aep_worker/ECHAIN-MOODIFY-THICKNESS-016/20260730_pack_validation `
  --dry-run
```

Live execution requires `DEEPSEEK_API_KEY` and an explicit output directory. Do not overwrite a prior run; use a new `run_id`.

