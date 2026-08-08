# DSK-MFY-PPE-HARDENING-005 Implementation Audit

**Date:** 2026-08-01 UTC
**Phase:** Batch 0 — Fact Freeze
**Auditor:** DeepSeek (Worker)

## 1. Environment Freeze

| Item | Value |
|---|---|
| Branch | `codex/mainline-cloud-dev-20260603` |
| HEAD | `df3a8a3c8ead4eae0675733169614efe59bf395d` |
| Python | 3.12.3 (`C:\Users\Administrator\AppData\Local\Programs\Python\Python312\python.exe`) |
| duckdb | 1.5.5 |
| numpy | 2.5.1 |
| pyarrow | 21.0.0 |
| pydantic | 2.13.4 |
| PyYAML | 6.0.3 |
| typer | 0.27.0 |
| pytest | 9.1.1 |
| ruff | 0.16.1 |
| mypy | 1.20.2 |
| Platform | Windows 10 Enterprise 10.0.19045 |

## 2. Baseline Test Results

| Suite | Result |
|---|---|
| `pytest` (10 tests) | **10 passed, 0 failed** |
| `ruff check src tests` | **All checks passed** |
| `mypy src` | **Success: no issues found in 9 source files** |

Test files:
- `tests/test_metrics.py` — 3 tests (deterministic levels, comparison gain, stereo correlation)
- `tests/test_schemas.py` — 4 tests (demo case strict, unknown field reject, decision validate, production approval require)
- `tests/test_store_workflow.py` — 3 tests (immutability, missing measurement warning, promotion requires approval)

## 3. Readonly Baseline SHA-256 Hashes

```
8372f0508b0666c27db3baf3a92202c66d023b5bdb8c8cfa3ab9df0ae69d19ad  outputs/ppe_2026-08-01/01_COMMAND_CHECKLIST.md
cdfdc9c224c950f1b531c2f203a2bd6e2483b60ccce071df78edcb9ee8c86ce5  outputs/ppe_2026-08-01/02_PRODUCTION_GATES_DRAFT.md
0850b05e5b546d760e8aa653a4ce47bb323315009bb7b9529a195b8ff87c3211  outputs/ppe_2026-08-01/03_EXECUTION_REPORT.md
4ab54a77c83c4fb3354a59184432bfdc49b2521f198a214c960afecd2b0396c6  outputs/ppe_2026-08-01/evidence.yaml
f58b62c91f5242c74fbbc26524fcd0a9c603b45d19ef80844a7a890fbbb4e7de  outputs/ppe_2026-08-01/ledger/ledger.duckdb
5280b3e72122962ce218e03bb08d18e5bc215692941c1771a08eedd4d43e8e98  outputs/ppe_2026-08-01/failure_isolation/ledger/ledger.duckdb
3819c49b7bc8435da66ead8a55bf908d6996844e06403dd68317487ded3a515d  moodify-bridge/demo/case.yaml
d5eff0e1564e10a32a121e71cb149e100cd9f0e13cbacca8dbca9ccc00a4cd13  moodify-bridge/demo/rule.yaml
a504106e3362523beb259052543f2ade9bb2d8f259d5a1c126face4a3e120641  moodify-bridge/demo/approval.yaml
b9a19b1269175812237f9a0d590efbfc1a86582462ce5ba2e69ec55b4a98bb4a  moodify-bridge/demo/assets/source.txt
70fbb3a629c5d667ae47acdbd391723ab49ed0e680951323a2befc5cf8b3da4f  POSC_002_Function_Is_Not_Form_Edition_0.1.pdf
```

Note: `demo/evidence.yaml` does not exist — this is a runtime artifact, not a static demo asset.

## 4. Known Issues Reproduced

### Issue A — Semantics: `human_approval=true` with `approval_id=null`

**Trigger:** `rule validate demo/rule.yaml`
**Observed output:**
```json
{"checks": {"human_approval": true}, "approval_id": null}
```

The field `human_approval: true` reads as "this rule has human approval", but `approval_id: null` contradicts that. The actual semantics is: "this rule is in PROPOSED state and does not require approval." The check name conflates two distinct concepts: _approval is not required_ vs _approval is present_. Root cause in `services.py:102`:
```python
checks={"human_approval": not needs_approval or approval is not None}
```

**Fix required:** Rename check to `approval_gate_satisfied` or split into two fields: `approval_required: false` and `approval_present: null`.

### Issue B — Traceback: Missing approval file leaks Python `FileNotFoundError`

**Trigger:** `rule promote <rule> experimental <nonexistent_approval.yaml>`
**Result:** Full Python traceback with `FileNotFoundError` in Typer's rich traceback handler.

Root cause in `cli.py:127`: no try/except around `read_model(approval, HumanApproval)` for file-not-found. Typer's rich handler renders the traceback.

**Fix required:** Catch FileNotFoundError and emit stable error code + message without traceback.

### Issue C — Traceback: Illegal transition leaks `ValueError`

**Trigger:** `rule promote <rule> production <valid_approval.yaml>` (proposed→production is invalid)
**Result:** Full traceback with `ValueError: Invalid rule transition`.

Root cause in `cli.py:130`: the `promote_rule` call raises ValueError through a raw exception path that Typer renders as traceback.

**Fix required:** Convert ValueError to typer.BadParameter or handle before calling promote_rule.

### Issue D — Partial State: Approval written before transition validation (CRITICAL)

**Trigger:** `rule promote <rule> production <valid_approval.yaml>` (illegal transition)

**Evidence:**
- After failed promotion, DuckDB `approvals` table has 1 row: `(eeeeeeee-eeee-4eee-8eee-eeeeeeeeeee1, R-DEMO-001, 1.0.0)`
- `ledger_events` has 1 `human_approval_recorded` event
- Rule file was NOT modified (correct — state unchanged)
- But DB is now in partial state: approval exists but rule was never promoted

Root cause in `cli.py:130`:
```python
db.add_approval(record); emit(promote_rule(db, path, target))
```
`add_approval` executes first, then `promote_rule` raises on invalid transition.

**Fix required:** Reorder operations — validate transition FIRST, then add approval. Whole operation must be atomic: any failure must roll back both rule write and approval insert, or never write approval until all validations pass.

## 5. Data Flow Analysis

Current `rule promote` flow (BROKEN):
```
1. read_model(approval, HumanApproval)   — can FileNotFoundError
2. read_model(path, MoodifyRule)         — can FileNotFoundError
3. Check (rule_id, version) match        — can BadParameter
4. db.add_approval(record)               — WRITES APPROVAL TO DB
5. promote_rule() → validate transition  — can ValueError
6. promote_rule() → check approval in DB — can PermissionError
7. promote_rule() → write_yaml(path)     — can OSError
```

Corrected flow must be:
```
1. read_model(approval, HumanApproval)   — stable error, no traceback
2. read_model(path, MoodifyRule)         — stable error, no traceback
3. Check (rule_id, version) match        — stable error, no traceback
4. Validate transition legality          — stable error, no traceback
5. db.add_approval(record)               — only after all validations pass
6. write_yaml(path, promoted)            — only after approval persisted
```

Any failure at or after step 5 must be detectable and recoverable.

### Write Boundary

- `db.add_approval`: DuckDB INSERT into approvals + ledger_events
- `write_yaml`: overwrites rule file at `path`

If write_yaml fails after add_approval, the approval exists in DB but rule file is unchanged — another partial state.

**Mitigation:** For now (no transaction support across DuckDB + filesystem), we must validate everything before writing anything. The DB write and file write will remain two operations but at least the validation happens first. Known limitation: power failure between steps 5 and 6 can still lose the file write.

## 6. Deterministic Fields

Current `ValidationResult` and other models use `uuid4()` and `utc_now()` defaults. These are marked as variable fields for normalization:
- `validation_id`, `packet_id`, `measurement_id`, `event_id`, etc. (UUIDs)
- `checked_at`, `compiled_at`, `measured_at`, `created_at`, etc. (timestamps)

For dual-run normalization, exclude these fields from comparison. Declare in environment.json.

## 7. Minimal Modification Files

Based on the issues found, these files need changes:

| File | Changes |
|---|---|
| `moodify-bridge/src/moodify_bridge/schemas.py` | Add `GateResult`, `GateStatus`, `RunManifest`, `EnvironmentInfo`, `CommandResult`, `PPEFinalStatus` models |
| `moodify-bridge/src/moodify_bridge/services.py` | Fix `validate_rule` semantics; reorder `promote_rule` validation before DB write; add gate evaluation, PPE runner |
| `moodify-bridge/src/moodify_bridge/cli.py` | Add `ppe run` command; stable error handling without traceback in `rule_promote` |
| `moodify-bridge/src/moodify_bridge/store.py` | No schema changes needed (read-only schema constraint) |
| `moodify-bridge/src/moodify_bridge/serialization.py` | No changes needed |
| `moodify-bridge/tests/test_gates.py` | NEW: GateResult schema tests, gate aggregation, blocking logic |
| `moodify-bridge/tests/test_ppe_runner.py` | NEW: Unified runner, manifest, CLI error codes |
| `moodify-bridge/tests/test_promotion_atomicity.py` | NEW: Partial state prevention tests |
| `moodify-bridge/tests/test_failure_matrix.py` | NEW: Fault injection matrix |

No changes to `moodify-bridge/demo/`, `outputs/ppe_2026-08-01/`, or any `migrations/` directory.

## 8. Unified Entry Point Design

Single command:
```powershell
py -3.12 -m moodify_bridge.cli ppe run demo/case.yaml --output-dir NEW_RUN_DIR
```

Internally executes the sequence: case create → case validate → assets hash → evidence compile → gate evaluation → report build → final status. Each step writes to `command_results.jsonl`. Final manifest collects all outputs.

### Output Directory Rules
- Must be explicitly provided (required argument)
- Must not exist OR must be empty (reject non-empty dirs)
- All artifacts written under this directory

### Artifact Layout
```
RUN_DIR/
  run_manifest.json
  environment.json
  command_results.jsonl
  gate_results.json
  evidence.yaml
  ledger/ledger.duckdb
  reports/case.md
  reports/case.html
  FINAL_STATUS.txt
```

## 9. Schema-Freezing Strategy

No DuckDB migration changes. All new types are Pydantic models in `schemas.py`. The existing `ValidationResult` model gets its `checks` field clarified (renamed key). New `GateResult` is a separate model.

Historical compatibility: existing `ValidationResult.checks.human_approval` consumers need an adapter period. We preserve the existing field but add clarifying fields in gate evaluation output. Old `ValidationResult.checks` is not renamed — instead, the new `GateResult` model becomes the authoritative check, and `ValidationResult` is kept for backward compat.

## 10. Batch A-D Execution Plan

### Batch A (Correctness)
1. Add `GateResult`, `GateStatus` models to schemas.py
2. Fix `validate_rule` semantics — split `human_approval` into `approval_required` + `approval_present`
3. Reorder `rule_promote`: validate → add_approval → write_yaml
4. Add atomicity tests

### Batch B (Failure Form)
1. Add stable error handling in CLI (no traceback for expected errors)
2. Add `ppe run` command with full artifact generation
3. Add `RunManifest`, `EnvironmentInfo`, `CommandResult` models
4. Handle output-dir existence check

### Batch C (Repeatability)
1. Dual-run compare with normalization
2. Automated failure matrix
3. Readonly hash verification before/after

### Batch D (Delivery)
1. Full test suite + Ruff + Mypy
2. README update
3. Validation report, failure ledger, HANDOFF
