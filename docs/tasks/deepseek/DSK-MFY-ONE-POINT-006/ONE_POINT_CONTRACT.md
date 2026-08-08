# One-Point Contract — DSK-MFY-ONE-POINT-006

## Status

Frozen before any implementation. Any code change must be traceable to a clause in this contract.

## 1. Input Contract: OnePointSpec

### Required Fields

| Field | Type | Meaning | Fail if |
|---|---|---|---|
| `source` | ProductionCase manifest path | The immutable case contract for this prepare-only facade | Missing, unreadable, invalid, or containing an asset hash mismatch |
| `essence` | `str` (1–500 chars) | Plain-language: what this work is | Empty or whitespace-only |
| `must_preserve` | `list[str]` (≥1 item) | What must survive — identity constraints | Empty |
| `desired_change` | `str` (1–500 chars) | What is being sought | Empty |
| `must_avoid` | `list[str]` (≥1 item) | What must not occur | Empty |
| `human_owner` | `str` (≥1 char) | Who holds final authority | Empty or whitespace-only |

### Optional Fields

| Field | Type | Meaning |
|---|---|---|
| `case_id` | UUID | Reference an existing ProductionCase |
| `limitations` | `list[str]` | Known constraints on this run |
| `reference_assets` | `list[AssetRef]` | Reference audio for comparison |
| `delivery_conditions` | `list[str]` | Conditions that must be met for completion |

### Validation Rules (fail-closed)

1. Every item in `desired_change` that contradicts any item in `must_preserve` → **BLOCKED**.
2. Every item in `desired_change` that could cause any item in `must_avoid` → **BLOCKED**.
3. `essence` that describes what the work "should become" rather than what it "is" → **WARN** but proceed.
4. BLOCKED means: no processing, no candidate generation, no gate evaluation. Status = BLOCKED, reason recorded, human_owner notified.

### Schema Compatibility

`OnePointSpec` maps to existing `ProductionCase` + evidence model. In Edition
0.1, `refine prepare` deliberately accepts a ProductionCase YAML manifest—not a
raw audio path—because it prepares a plan and evidence package without processing
audio. A future execution stage may introduce an explicit asset-ingestion adapter;
it must not silently change this field's meaning.

- `source` → existing ProductionCase YAML manifest
- `essence` → stored in result, preserved in evidence
- `must_preserve` / `must_avoid` → evidence constraints
- `desired_change` → treatment intent
- `human_owner` → HumanApproval.approver pattern (but not an approval — a jurisdiction)

## 2. Output Contract: OnePointResult

### Required Fields

| Field | Type | Meaning |
|---|---|---|
| `spec_identity` | SHA-256 of input spec | Input traceability |
| `status` | Enum (see below) | Result state |
| `essence` | `str` | Echo of input — what the work is |
| `protect` | `str` | What was protected (summary) |
| `allow` | `str` | What was allowed to change (summary) |
| `avoid` | `str` | What was avoided (summary) |
| `action` | `str` | What Moodify actually did |
| `entrust` | `str` | What still needs human judgment |
| `owner` | `str` | Echo of human_owner |
| `evidence_path` | relative path | Where to find full evidence |
| `created_at` | ISO-8601 UTC | When this result was produced |

### Status Enum (exactly 4 values)

| Value | Meaning | When |
|---|---|---|
| `READY_FOR_REVIEW` | Evidence complete, awaiting human judgment | All gates pass or WARN, evidence generated |
| `BLOCKED` | Cannot proceed — identity conflict or constraint violation | `must_preserve`/`must_avoid` conflict detected |
| `NEEDS_EVIDENCE` | Some required evidence is missing | Measurement unavailable, asset unreadable |
| `FAILED` | A blocking gate failed | Identity hash mismatch, report missing |

### Forbidden in Result

- `final`, `approved`, `completed`, `improved`, `enhanced`, `mastered`
- Any auto-generated "score" or "grade"
- Any field named `final_*` or `auto_*`
- Internal acronyms (WSE, MSE, PPE, MRS) in `action` or `entrust` fields

## 3. State Transitions

```
(BLOCKED)  → [fix spec conflicts] → READY_FOR_REVIEW
(NEEDS_EVIDENCE) → [provide missing assets] → READY_FOR_REVIEW
(FAILED) → [fix hash mismatch / asset issue] → READY_FOR_REVIEW
(READY_FOR_REVIEW) → [human decision] → (external: human declares done)
```

Moodify never transitions out of `READY_FOR_REVIEW`. Only the human_owner can close the loop.

## 4. Evidence Contract

The `evidence/` directory must contain:
- `run_manifest.json` — full run manifest (existing RunManifest)
- `gate_results.json` — gate results (existing GateResult[])
- `case.yaml` — the ProductionCase used
- `ledger/` — the DuckDB ledger
- `spec.yaml` — the input OnePointSpec
- `package_manifest.json` — SHA-256 index for the default result and complete evidence package

All paths referenced in `result.json` must resolve and their SHA-256 must match.

## 5. Compatibility

- This contract does NOT modify existing ProductionCase, ValidationResult, GateResult, or RunManifest schemas.
- `OnePointSpec` is a NEW model that adapts TO existing models via references, not replacement.
- Old CLI entries (`case create`, `rule promote`, `ppe run`) continue to work unchanged.
- `refine prepare` is a new command, not a rename.
