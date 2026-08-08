# DSK-MFY-RUNTIME-INTEGRATION-001 — Codex Final Acceptance

**Decision:** ACCEPTED_AFTER_CODEX_FINISH
**Date:** 2026-08-01
**Acceptance owner:** Codex

## 1. Runtime Integration Verdict

The production-control spine is now the authoritative user-facing path for
real execution, verification, evidence packaging, and completion. CLI v2
`case` commands drive the full 16-state lifecycle; engines are invoked only
through an immutable `ApprovedExecutionEnvelope` produced after the approval
gate; verification and evidence packaging are mandatory preconditions of
`COMPLETED`; and every legacy raw path is explicitly classified
`UNCONTROLLED_TOOL_EXECUTION`.

## 2. Actual Complete State Path Executed

Golden case `MFY-CASE-5030DEA8F22D` (source: `moodify-core-package/tests/baseline/test_audio/vocal_folk.wav`):

```text
CREATED -> SOURCE_REGISTERED -> SPECIFIED -> ANALYZED -> PLANNED
-> TECHNICALLY_VALIDATED -> AWAITING_ARTISTIC_APPROVAL -> APPROVED
-> EXECUTING -> EXECUTED -> VERIFYING -> VERIFIED -> PACKAGED -> COMPLETED
```

Full transition log persisted in `case_final.json` under the golden-case
artifact directory.

## 3. CLI v2 Commands Implemented

```text
moodify case create   <project_dir> --spec <json|file> --owner <name> [--asset-id]
moodify case analyze  <project_dir> <case_id>
moodify case approve  <project_dir> <case_id> --owner <name>
moodify case status   <project_dir> <case_id>
moodify case execute  <project_dir> <case_id>      (raw WAV path rejected)
moodify case verify   <project_dir> <case_id>
moodify case package  <project_dir> <case_id>
```

All commands are non-interactive, emit one JSON document on stdout (errors on
stderr), use stable error codes, and return non-zero exit codes on failure.
`case execute` accepts only a production `case_id` — never a raw audio path.

## 4. Engine Integrated

`NativeExecutionEngine` (`moodify/app/engines.py`) — deterministic pure-Python
DSP (numpy + soundfile), `name="native"`, `version="1.0.0"`, actions
gain/eq/compressor/limiter/fade_in/fade_out. It implements the
`ExecutionEngine` protocol, receives only the `ApprovedExecutionEnvelope`,
renders to a staging path, and atomically promotes the final output. It never
mutates case state, never approves, never writes approval records, and refuses
unsupported actions or source-hash mismatch before touching audio.

## 5. Approval-to-Execution Binding

`ProductionControlService.execute()` (production_control.py:326):

1. loads the case; 2. requires state `APPROVED`; 3. recalculates the source
   SHA-256; 4. verifies spec hash; 5. verifies plan hash; 6. calls
   `check_approval_gate()`; 7. verifies engine name and version; 8. transitions
   `EXECUTING`; 9. builds the frozen `ApprovedExecutionEnvelope`
   (case_id, case_version, source_path, source_sha256, one_point_spec_hash,
   plan_id, plan_hash, approval_id, approved_by, engine_name, engine_version,
   actions, parameters, output_path, created_at) — generated only after the
   gate succeeds; 10. invokes the engine adapter; 11. records the envelope,
   plan identity, action manifest and parameters in `execution_record`; 12.
   transitions `EXECUTED` on success (else `FAILED`) and returns a structured
   result.

Invariant: no approved execution envelope → no formal engine invocation.
`check_approval_gate` (production_control.py:259) rejects a stale plan hash
(`PLAN_HASH_STALE`), changed source (`SOURCE_CHANGED`), changed spec
(`SPEC_CHANGED`), or engine mismatch (`ENGINE_MISMATCH`).

## 6. Verification Implemented

`ProductionControlService.verify()` implements `EXECUTED -> VERIFYING ->
VERIFIED | FAILED`. The `VerificationResult` checks: output exists, output
readable, source unchanged (observed vs expected SHA-256), output SHA-256,
engine identity matches the execution record, plan identity matches (plan_id +
plan_hash), no fatal engine error, and basic audio checks (duration positive,
sample rate, channels). Any failure transitions the case to `FAILED`; it
cannot proceed to `PACKAGED`. Technical verification never asserts artistic
correctness and never creates an approval record (test
`test_verification_does_not_create_artistic_approval`).

## 7. Evidence Package Implemented

`ProductionControlService.package()` implements `VERIFIED -> PACKAGED ->
COMPLETED`. The package contains all required artifacts:

```text
case.json  source_manifest.json  one_point_spec.json  analysis.json
plan.json  technical_gate.json  artistic_approval.json
approved_execution_envelope.json  execution_record.json
verification_result.json  evidence_manifest.json  output/processed_audio.wav
```

`evidence_manifest.json` binds case_id, case_version, source_sha256,
one_point_spec_hash, plan_hash, approval_id, execution_id, engine_name,
engine_version, output_sha256, output_path, verification_id,
verification_status, and Moodify version. `_validate_package()` verifies all
required files exist and all hashes/IDs agree — including disk-level checks
(source unchanged since registration; executed output unchanged; package
output hash equals the executed output hash). Only after validation passes is
`PACKAGED -> COMPLETED` executed. A `PACKAGED` retry (interrupted operation)
re-validates the package before completing.

## 8. Completion-Transition Proof

State graph (`ALLOWED`, production_control.py:64): `APPROVED`, `EXECUTING`,
`EXECUTED`, `VERIFYING`, `VERIFIED`, `FAILED` all exclude `COMPLETED`; only
`PACKAGED -> {COMPLETED, FAILED}` exists. Enforced at runtime by
`_transition()` and covered by parameterized tests for all six prohibited
transitions (test_production_runtime.py).

## 9. Legacy Paths and Classifications

| Path | Classification |
|---|---|
| `moodify run execute` / `run verify` (CLI v2) | EXPLICITLY_UNCONTROLLED — requires `--allow-uncontrolled`; response carries `production_controlled:false, classification:UNCONTROLLED_TOOL_EXECUTION, formal_moodify_asset:false`; creates no case, no approval, no evidence package |
| `moodify daw render` (legacy CLI) | EXPLICITLY_UNCONTROLLED — requires `--allow-uncontrolled`; prints `classification=UNCONTROLLED_TOOL_EXECUTION production_controlled=false formal_moodify_asset=false` |
| `app.orchestrator.execute_plan()` | EXPLICITLY_UNCONTROLLED — marked INTERNAL/LEGACY; returns `UNCONTROLLED_TOOL_EXECUTION` classification; status renamed `UNCONTROLLED_OK/PARTIAL/FAILED`; cannot produce formal completion |
| `ProductionControlService.execute()` | FORMAL_PATH_MIGRATED — the canonical controlled runtime path |

## 10. Files Created or Modified

**Created**

- `moodify-core-package/src/moodify/app/engines.py`
- `moodify-core-package/tests/test_production_runtime.py` (46 tests)
- `moodify-core-package/tests/cli_v2/test_cli_v2_case_commands.py` (10 tests)
- `scripts/golden_runtime_exercise.py`
- `docs/tasks/deepseek/DSK-MFY-RUNTIME-INTEGRATION-001/CODEX_FINAL_ACCEPTANCE_2026-08-01.md`

**Modified**

- `moodify-core-package/src/moodify/app/production_control.py` — envelope,
  engine protocol, `ProductionControlService`, `ProductionCaseStore`,
  empty-state spec semantics, full `to_dict`/`from_dict`, transitions log
- `moodify-core-package/src/moodify/cli_v2/main.py` — `case` commands,
  `--allow-uncontrolled` on `run` paths, `CLIError.payload`, global
  `ControlError` mapping
- `moodify-core-package/src/moodify/cli.py` — `case` dispatch; `daw render`
  guard
- `moodify-core-package/src/moodify/app/orchestrator.py` — legacy marking
- `moodify-core-package/tests/cli_v2/test_cli_v2_closed_loop.py` —
  `--allow-uncontrolled` flag
- `docs/audits/MOODIFY_PRODUCT_ALIGNMENT_AUDIT.md` — P0 closure + score
- `artifacts/verification/runtime_integration/golden_case/**` — golden case

## 11. Tests Added and Executed

- `tests/test_production_runtime.py`: 46 passed (state graph, runtime,
  verification, evidence, persistence, spec semantics, legacy paths)
- `tests/cli_v2/test_cli_v2_case_commands.py`: 10 passed
- `tests/cli_v2/test_cli_v2_closed_loop.py`: 9 passed (updated for
  `--allow-uncontrolled`)
- Full core regression (excluding pre-existing broken collection in
  `tests/v2/` and three files with pre-existing `ApprovalActorType` /
  `pretty_midi` import errors): all passed
- Known pre-existing failures unrelated to this milestone: `tests/v2/*`
  (18 files), `tests/test_api_v01.py`, `tests/test_api_operator.py`
  (`cannot import name 'ApprovalActorType' from 'moodify.domain'`),
  `tests/test_transcription_stems.py` (`No module named 'pretty_midi'`)

## 12. Golden Case Artifact Location

```text
artifacts/verification/runtime_integration/golden_case/
  README.md                — case summary + state path
  cli_transcript.json      — every CLI request and response
  case_final.json          — persisted case (transitions, execution, verification)
  source_manifest.json     — fixture identity
  evidence/                — the formal evidence package (all 12 required artifacts)
  output/processed_audio.wav — the executed output
```

Rerunnable via `python scripts/golden_runtime_exercise.py`.

## 13. Updated P0 Closure Table

| ID | Contradiction | Status | Evidence |
|---|---|---|---|
| P0-01 | Plan generated without preserve constraints | CLOSED | `validate_spec_fields` rejects omitted/null; empty lists require explicit `preservation_acknowledgement` |
| P0-02 | Execute has no approval gate | CLOSED | `check_approval_gate` before every execution; envelope only after gate |
| P0-03 | CLI DAW bypasses specification layer | EXPLICITLY_UNCONTROLLED | `daw render` and `run execute` require `--allow-uncontrolled`; `case execute` rejects raw WAV; formal path cannot be confused |
| P0-04 | No distinction between technical gate and artistic approval | CLOSED | `TechnicalGateResult` + `ArtisticApprovalRecord` both enforced and persisted |
| P0-05 | Dry-run and execute use same code path | FORMAL_PATH_MIGRATED | `ProductionControlService.execute` is the canonical path; legacy `run execute` refuses dry-run plans and is classified uncontrolled |

## 14. Updated Alignment Score

**3.0 / 5 → 4.0 / 5** (weighted across the audit scorecard categories; the
control spine moved from an isolated correct model to the primary production
authority).

| Category | Before | After | Notes |
|---|---|---|---|
| Identity before intervention | 2 | 4 | explicit-declaration spec semantics; hash bindings |
| Constraint enforcement | 1 | 3 | empty-state + acknowledgement; plan/spec/source bindings |
| Plan-before-apply | 1 | 4 | hash-bound plan; exact-plan approval; immutable envelope |
| Human approval enforcement | 1 | 4 | approval record bound to plan hash; gate enforced at runtime |
| Evidence-by-default | 2 | 4 | mandatory package + validated manifest before COMPLETED |
| Source integrity | 3 | 5 | source never overwritten; hash rechecked before/during/after |
| Replaceable execution | 3 | 4 | `ExecutionEngine` protocol; envelope-only invocation |
| CLI-native operation | 2 | 4 | `case status/execute/verify/package` JSON-first |
| Agent-native operation | 1 | 4 | non-interactive, JSON stdout, stable codes, no hidden prompts |
| Verification quality | 2 | 4 | VERIFYING stage; identity/hash/audio checks; FAIL on any failure |
| Failure and recovery | 2 | 3 | FAILED states; explicit re-approval retry; interruptions never fabricated |
| Reproducibility | 2 | 3 | deterministic plan + native engine; rerunnable golden script |
| Documentation consistency | 3 | 4 | audit + acceptance docs updated |
| Production-case traceability | 2 | 5 | transitions log, persisted state, envelope, records, evidence binding |

## 15. Highest Remaining Architectural Risk

Only one engine (`native`) is integrated; the SoX/FFmpeg adapters and the
legacy orchestrator remain uncontrolled. The next risk-ranked step is
migrating a second engine (e.g., SoX, already version-probed) onto the
`ExecutionEngine` protocol so the envelope contract is proven against a
non-native backend, followed by cleaning the pre-existing `tests/v2`
collection break (`ApprovalActorType` missing from `moodify.domain`).

## 16. Explicit Answers

1. **Can `APPROVED` transition directly to `COMPLETED`?** No. `ALLOWED` maps
   `APPROVED -> {EXECUTING, REJECTED}` (production_control.py:68) and
   `_transition()` raises `ValueError` otherwise. Tests:
   `test_completion_shortcut_transitions_are_impossible`,
   `test_transition_to_completed_rejected_at_runtime`.
2. **Can any formal CLI command invoke an engine without an approved
   execution envelope?** No. `case execute` → `ProductionControlService.execute`
   → `check_approval_gate` (raises `ARTISTIC_APPROVAL_REQUIRED` /
   `PLAN_HASH_STALE` / `SOURCE_CHANGED` / `ENGINE_MISMATCH` before any engine
   call); the envelope is built only after the gate succeeds, and the engine
   receives the envelope as its only input. Test:
   `test_engine_not_invoked_when_approval_gate_fails` (engine call counter
   remains empty).
3. **Can any formal case become `COMPLETED` without verification?** No.
   `package()` requires state `VERIFIED` and raises
   `VERIFICATION_REQUIRED` otherwise (test
   `test_package_before_verified_rejected`); verification failure transitions
   to `FAILED` and cannot reach `PACKAGED`.
4. **Can any formal case become `COMPLETED` without a valid evidence
   package?** No. `_validate_package()` runs before `PACKAGED -> COMPLETED`
   and fails on missing artifacts (`EVIDENCE_INCOMPLETE`) or any hash/ID
   mismatch (`EVIDENCE_INCONSISTENT`), leaving the case at `PACKAGED` (tests
   `test_package_missing_required_artifact_prevents_completed`,
   `test_package_output_tampered_prevents_completed`,
   `test_package_source_changed_prevents_completed`).
5. **Can a legacy raw command be mistaken programmatically for a formal
   Moodify production asset?** No. Every legacy path carries
   `production_controlled:false`, `classification:UNCONTROLLED_TOOL_EXECUTION`,
   `formal_moodify_asset:false` in its programmatic output, requires
   `--allow-uncontrolled`, creates no case, no approval metadata, no evidence
   package, and no `COMPLETED` state (tests
   `test_legacy_daw_render_classified_uncontrolled`,
   `test_orchestrator_execute_plan_is_classified_uncontrolled`,
   `test_uncontrolled_execution_creates_no_evidence_package`,
   `test_uncontrolled_execution_creates_no_completed_case`).

## 17. Success Statement

> The Moodify production lifecycle is no longer only a model around the audio
> engine. It is the authority that permits execution, observes execution,
> verifies the result, packages the evidence, and determines whether a
> production asset is complete.
