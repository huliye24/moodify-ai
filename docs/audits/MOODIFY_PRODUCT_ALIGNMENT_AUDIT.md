# Moodify Product Alignment Audit

**Date:** 2026-08-01 | **HEAD:** df3a8a3 | **Last updated:** 2026-08-01 (DSK-MFY-RUNTIME-INTEGRATION-001) | **Auditor:** DeepSeek

## 1. Executive Conclusion

**Current product behavior:** Moodify is an **intent-preserving production-control system** with a controlled runtime.

The production-control spine (`moodify/app/production_control.py`) is the authoritative user-facing path: CLI v2 `case` commands drive a 16-state lifecycle, engines execute only via an approved execution envelope, verification and evidence packaging are mandatory before `COMPLETED`, and all legacy raw paths are explicitly classified `UNCONTROLLED_TOOL_EXECUTION`.

### What Moodify Is Today (Based on Code)

A controlled production system: `ProductionCase` → OnePointSpec (explicit declaration, empty-state acknowledgement) → hash-bound Plan → TechnicalGate → exact-plan human Artistic Approval → controlled execution (`ApprovedExecutionEnvelope`) → mandatory verification → validated evidence package → `COMPLETED`. Legacy CLI DAW render, `run execute`, and `app.orchestrator.execute_plan()` remain as explicitly uncontrolled tools and cannot produce formal production assets.

### Overall Alignment Score

**4.0 / 5** — weighted across 14 categories (up from 3.0 after the control-spine milestone; see §7).

## 2. Five-Principle Assessment

### Principle I — Identity Before Intervention: Score 2/5

| Check | Status |
|---|---|
| OnePointSpec with must_preserve/must_avoid | EXISTS (bridge schemas) |
| Schema enforces non-empty preserve/avoid | YES (model validator) |
| Plan generator respects preserve/avoid | **NO — P0 CONTRADICTION** |
| Conflict detection exists | PARTIAL (keyword-based in bridge services) |
| Conflict is fail-closed | PARTIAL (BLOCKED for detected conflicts, but many conflicts pass undetected) |
| Engine can bypass specification | **YES — P0 BYPASS** (CLI DAW works directly on WAV files) |

**Critical gap:** `generate_plan()` in `app/orchestrator.py` reads `must_preserve` but does not validate desired_change against it. The constraint model exists in `OnePointSpec` but the orchestrator does not consume it.

### Principle II — Plan Before Apply: Score 1/5

| Check | Status |
|---|---|
| Plan can be serialized | YES (TreatmentPlan dataclass) |
| Dry-run mode exists | YES (`plan.dry_run = True`) |
| Dry-run avoids audio modification | YES |
| Approval state exists | **NO — P0 MISSING** |
| Execute requires approval | **NO — P0 CONTRADICTION** |
| Approval tied to exact plan version | **NO** |
| Rejected plan state | **NO** |
| Plan invalidated by source change | **NO** |
| Engine-version change invalidates plan | **NO** |

**Critical invariant FAIL:**
```python
# This executes without any approval check:
def execute_plan(plan, source, output_dir):
    adapter = SoXAdapter()
    # ... no approval gate, no state check, no authorization
    return result
```

### Principle III — Evidence by Default: Score 2/5

| Check | Status |
|---|---|
| Source SHA-256 recorded | YES (CLI DAW, Bridge) |
| Output SHA-256 recorded | YES |
| Engine name/version recorded | PARTIAL (in adapter evidence, not aggregated) |
| Human owner recorded | YES (OnePointSpec.human_owner) |
| Approval identity recorded | PARTIAL (field exists, no runtime write) |
| Before/after measurements | PARTIAL (spectral evidence exists but separate) |
| Unified evidence package | PARTIAL (EvidenceAggregator exists but mostly empty) |
| Evidence without actual execution | NOT CHECKED |
| Failed runs distinguishable | PARTIAL |

### Principle IV — Replaceable Execution: Score 3/5

| Check | Status |
|---|---|
| Engine adapters exist | YES (SoX, matchering, RubberBand, native, FFmpeg) |
| probe() reports real status | YES |
| Engine-specific params isolated | PARTIAL (mixed in orchestrator) |
| Plan can express actions engine-agnostically | YES (type: gain, params: {gain_db}) |
| Missing engine handled explicitly | YES (UNAVAILABLE) |
| Engine swap without changing evidence format | PARTIAL (not proven) |

### Principle V — CLI-Native & Agent-Native: Score 2/5

| Check | Status |
|---|---|
| Non-interactive execution | YES |
| JSON output | PARTIAL (CLI v2 has it, main CLI does not) |
| Stable exit codes | PARTIAL (CLI v2 stable, main CLI ad-hoc) |
| Machine-readable errors | PARTIAL (error codes exist in some paths) |
| No GUI dependency | YES |
| Agent can submit intent → get plan → execute | **NO — approval gap blocks this** |
| Idempotency | NOT IMPLEMENTED |

## 3. Human Authority Assessment: Score 1/5

**P0: No approval enforcement exists at runtime.**

- `OnePointSpec.human_owner` is a string field. No code path checks it before execution.
- `execute_plan()` does not consult any approval record.
- No distinction between "human artistic approval" and "technical validation."
- The CLI DAW `render` command executes without any authorization.

## 4. P0 Contradictions

| ID | Contradiction | Status (2026-08-01) | Evidence |
|---|---|---|---|
| **P0-01** | Plan generated without preserve constraints | **CLOSED** | `validate_spec_fields` rejects omitted/null fields and empty constraint lists without an explicit `preservation_acknowledgement` |
| **P0-02** | Execute has no approval gate | **CLOSED** | `check_approval_gate` before every execution; `ApprovedExecutionEnvelope` generated only after the gate |
| **P0-03** | CLI DAW bypasses specification layer | **EXPLICITLY_UNCONTROLLED** | `moodify daw render` and `run execute` require `--allow-uncontrolled` and return `UNCONTROLLED_TOOL_EXECUTION`; `case execute` rejects raw WAV paths |
| **P0-04** | No distinction between technical gate and artistic approval | **CLOSED** | `TechnicalGateResult` and `ArtisticApprovalRecord` are separate enforced records, both persisted in evidence |
| **P0-05** | Dry-run and execute use same code path | **FORMAL_PATH_MIGRATED** | `ProductionControlService.execute` is the canonical path; legacy `run execute` refuses dry-run plans and is classified uncontrolled |

## 5. Alignment Scorecard

| Category | Score (2026-08-01) | Notes |
|---|---|---|
| Identity before intervention | 4 | explicit-declaration spec; empty-state acknowledgement; hash bindings enforced |
| Constraint enforcement | 3 | spec validation fail-closed; plan/spec/source bound by hashes; technical gate fail-closed |
| Plan-before-apply | 4 | hash-bound plan; exact-plan human approval; immutable execution envelope |
| Human approval enforcement | 4 | `ArtisticApprovalRecord` bound to plan hash; gate checked at runtime |
| Evidence-by-default | 4 | mandatory evidence package; validated manifest before COMPLETED |
| Source integrity | 5 | source never overwritten; hash rechecked before/during/after execution |
| Replaceable execution | 4 | `ExecutionEngine` protocol; engines receive only the envelope |
| CLI-native operation | 4 | `case status/execute/verify/package` JSON-first |
| Agent-native operation | 4 | non-interactive, JSON stdout, stable error codes, no hidden prompts |
| Verification quality | 4 | VERIFYING stage; identity/hash/audio checks; FAIL transitions to FAILED |
| Failure and recovery | 3 | FAILED states; explicit re-approval retry; interrupted states never fabricated |
| Reproducibility | 3 | deterministic default plan + native engine; rerunnable golden script |
| Documentation consistency | 4 | audit + acceptance docs updated |
| Production-case traceability | 5 | transitions log, persisted state, envelope, execution/verification records, evidence binding |
| **Weighted Overall** | **4.0** | up from 3.0 (control-spine milestone) |

## 6. Historical Milestone

The original first-milestone recommendation (approval-gate file) has been
superseded by the control spine: `moodify/app/production_control.py`
(`ProductionControlService`, `ApprovedExecutionEnvelope`,
`ProductionCaseStore`) and `moodify/app/engines.py`
(`NativeExecutionEngine`). See
`docs/tasks/deepseek/DSK-MFY-RUNTIME-INTEGRATION-001/CODEX_FINAL_ACCEPTANCE_2026-08-01.md`
for the full integration evidence.
