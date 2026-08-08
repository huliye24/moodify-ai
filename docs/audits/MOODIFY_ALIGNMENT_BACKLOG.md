# Moodify Alignment Backlog

## P0 — Product Definition Violations

| ID | Problem | Risk | Proposed Change | Scope |
|---|---|---|---|---|
| P0-01 | Plan generated without preserve constraints | Silently damages work identity | Add constraint validation to `generate_plan()` | S |
| P0-02 | Execute has no approval gate | Unauthorized production runs | Add `ApprovalGate` to `execute_plan()` | M |
| P0-03 | CLI DAW bypasses specification layer | Engine runs without intent contract | Require OnePointSpec for `daw render` | M |
| P0-04 | No human/technical approval distinction | Technical pass misread as artistic ok | Schema: separate `Approval.kind` field | S |
| P0-05 | Dry-run and execute use same code path | Ambiguous state transitions | Separate `plan_preview()` from `execute_plan()` | M |

## P1 — Trust and Safety

| ID | Problem | Risk | Proposed Change | Scope |
|---|---|---|---|---|
| P1-01 | No source-hash recheck before apply | Stale plan applied to changed source | Hash check in execute_plan | S |
| P1-02 | Failed execution marked as PARTIAL without rollback | Half-processed audio | Add rollback path or explicit FAILED state | M |
| P1-03 | Evidence incomplete by default | Missing proof of what happened | Connect all evidence sources to Aggregator | L |
| P1-04 | No plan version binding in evidence | Old plan, new evidence, unclear relationship | Add plan_hash to evidence_bundle | S |

## P2 — Architecture Separation

| ID | Problem | Risk | Proposed Change | Scope |
|---|---|---|---|---|
| P2-01 | Bridge and App are two parallel orchestrators | Confusion, duplicate logic | Unify or clearly document separation | L |
| P2-02 | CLI v2 and main CLI are separate entry points | Users confused about which to use | Route CLI v2 from main CLI | M |
| P2-03 | Domain models unreferenced by runtime | Dead code, false impression of architecture | Wire domain models into app layer | M |
| P2-04 | Engine params mixed with plan model | Engine swap changes plan meaning | Isolate engine-specific params in adapter layer | M |

## P3 — Agent and Operational Readiness

| ID | Problem | Risk | Proposed Change | Scope |
|---|---|---|---|---|
| P3-01 | Agent cannot complete full lifecycle | No autonomous production possible | Complete approval + execute + verify chain | L |
| P3-02 | No idempotency in run model | Duplicate execution on retry | Add idempotency_key to Run | S |
| P3-03 | Exit codes inconsistent across commands | Agent cannot reliably parse results | Standardize exit codes (0/1/2/3) | M |
| P3-04 | No batch execution support | Inefficient at scale | Add batch plan execution | M |

## P4 — Documentation

| ID | Problem | Risk | Proposed Change | Scope |
|---|---|---|---|---|
| P4-01 | Architecture docs describe target, not current | False impression of completion | Label all docs with implementation status | S |
| P4-02 | Multiple competing schemas undocumented | Confusion about canonical model | Document schema relationships | S |
