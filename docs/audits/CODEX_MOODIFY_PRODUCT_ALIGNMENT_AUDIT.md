# Codex Independent Moodify Product-Alignment Audit

**Date:** 2026-08-01  
**Scope:** current working tree at `E:\moodify`; dirty/untracked state included  
**Method:** code tracing, targeted tests, synthetic-WAV runtime exercises, artifact inspection  
**Implementation changes:** none; only `CODEX_` audit documents and isolated audit artifacts were created.

## 1. Executive conclusion

Moodify is currently a **structured audio-processing pipeline**, not yet an intent-preserving, evidence-native production-control system.

The repository has credible building blocks: a strict Bridge `OnePointSpec`, source hashing, serializable plans, separate plan/execute commands, approval domain models, native/third-party adapters, spectral evidence and JSON CLI responses. The primary executable paths do not compose these parts into one enforced lifecycle. Most importantly, an executable CLI-v2 plan with no identity specification or approval produced audio, evidence and `status=completed`.

## 2. Current product behavior

Today Moodify behaves as several adjacent systems:

1. A tested v0.1 one-command analysis/preset/DSP/delivery pipeline.
2. A CLI-v2 project/asset/plan/run skeleton with source integrity and minimal native gain rendering.
3. A Bridge case/spec/evidence system with stricter identity constraints and keyword conflict detection.
4. A Workspace/domain model with approval-aware audio-version states.
5. Separate science, spectral, transcription and adapter packages.

They do not share a mandatory production-case identity, specification, approval, verification or evidence protocol. Therefore the strongest local component cannot be used to claim system-level compliance.

## 3. Alignment score

Equal weights were used because the task defines no alternative weights. A P0 cap is applied: a system permitting unapproved apply and pre-verification success cannot score above 2.0 overall.

| Category | Score / 5 | Rationale |
|---|---:|---|
| Identity before intervention | 2.0 | Strong Bridge schema, bypassed by core execution |
| Constraint enforcement | 1.0 | Keyword checks are local and semantically incomplete |
| Plan-before-apply | 2.0 | Commands separate; required invariant absent |
| Human approval enforcement | 0.0 | Unapproved plan executed successfully |
| Evidence-by-default | 2.0 | Render evidence exists; package is incomplete/unbound |
| Source integrity | 3.0 | Import/recheck hashes and new output path work in CLI-v2 |
| Replaceable execution engines | 2.0 | Adapters exist; semantics and evidence are duplicated |
| CLI-native operation | 3.0 | Structured non-GUI CLI works for a minimal loop |
| Agent-native operation | 1.0 | Missing specification/analysis/approval/status/export lifecycle |
| Verification quality | 1.0 | Optional hash/existence checks only |
| Failure and recovery | 1.0 | Some guards; no atomic package/recovery/idempotence |
| Reproducibility | 1.0 | Repeat output matched, but engine/build lock absent |
| Documentation consistency | 1.0 | Version, capability and handoff claims disagree with runtime |
| Production-case traceability | 1.0 | IDs and stores are fragmented |

**Raw mean:** 1.57/5. **Weighted overall after P0 cap:** **1.6/5**.  
**Confidence:** high for primary CLI-v2/v0.1 paths; medium for Bridge end-to-end behavior because its declared runtime was unavailable.

Higher scores are blocked by unapproved execution, desired-change bypass, success before verification, missing evidence binding, fragmented case identity and unrunnable critical tests.

## 4. Five-principle assessment

### I. Identity before intervention — not system-enforced

`OnePointSpec` requires `essence`, non-empty `must_preserve`, `must_avoid`, `desired_change` and `human_owner`. It lacks canonical confidence/uncertainty and permitted-intervention scope. CLI-v2 accepts `{"gain_db": -1}` as the entire intent and creates an executable plan without a spec.

Static tracing of `detect_conflicts` shows the five required negative cases behave as follows:

| Conflict | Result |
|---|---|
| warmth vs vocal intimacy | ignored: no warm/intimacy rule |
| loudness vs dynamic preservation | detected by loudness/dynamic pair |
| width vs mono compatibility | detected by wide/mono pair |
| high-frequency enhancement vs sibilance | ignored unless exact shared token happens to match |
| transient enhancement vs soft texture | ignored: no transient/soft pair |

Detected conflicts block `refine_prepare`, but the entire Bridge layer is bypassable. Preservation is not compiled into post-processing verification.

### II. Plan before apply — structurally separated, contract violated

CLI-v2 serializes a plan before execution and refuses to execute a `dry_run=true` plan. The serialized plan contains only `dry_run`, `intent`, `plan_id`, `steps` and `warnings`. It omits source identity, constraints, owner, risks, expected effects, criteria, plan version, timestamp, engine and engine version.

The critical invariant fails at four conjuncts:

```text
approval: absent
source_hash: enforced at apply
plan_version: absent
engine_version: absent
required constraints: absent
```

Exact bypass: `moodify.cli_v2.main.cmd_run_execute()` proceeds from plan lookup and source-hash check directly to `native_render()`. `app.orchestrator.execute_plan()` is another unapproved direct path.

### III. Evidence by default — fragmented and not trustworthy enough

CLI-v2 records source/output hashes and native render facts. It does not bind the exact plan, approval, engine version, Moodify build, before measurements, deltas, spectral differences or verification result into the run evidence. `app.evidence` wrote a valid-looking bundle with zero sources/hashes and only `"output: not available"` as a limitation. Thus evidence generation is fail-open.

There is no self-contained package equivalent to the requested source/specification/analysis/approved-plan/execution/output/verification manifest. Evidence exists in several systems but is not one chain of custody.

### IV. Replaceable execution layer — partial claim

Native, SoX, Matchering and Rubber Band implementations exist, plus at least two executor interface locations. Product-level actions, approval semantics and evidence are not stable across them. No test proves a single approved plan action through two adapters without changing approval/evidence semantics. SoX unsupported actions are not rejected early in the current adapter trace.

### V. CLI-native and Agent-native — CLI partial, Agent lifecycle absent

CLI-v2 is non-GUI, subprocess-friendly and emits clean JSON with nonzero structured errors. Malformed JSON returned exit 2. It supports intake, minimal planning, apply and verification. It lacks canonical spec submission, analysis request, plan inspection contract, approval/rejection, status, recovery, batch and evidence export. An external Agent therefore cannot execute the required ten-step lifecycle without bypasses or direct file edits.

## 5. Human-authority assessment

The domain contains real `ApprovalDecision` and approval-aware `AudioVersion` transitions, but current `moodify.domain` exports prevent the targeted tests from collecting. More importantly, these models are not called by CLI-v2 apply. There is no approver identity, plan digest, approval timestamp or rejection command in the actual run record.

Technical verification and artistic approval are not represented as two mandatory, distinct decisions in the primary path. The runtime proved that a processing run can occur with no human decision. This is a direct product-definition contradiction.

## 6. Evidence-chain assessment

Observed positive facts:

- source SHA-256 is recorded at import and rechecked before CLI-v2 apply;
- output SHA-256 is recorded;
- output directories are not silently overwritten;
- render failures are represented separately from successful artifacts;
- verification recomputes output and source checks.

Observed trust gaps:

- `completed` is returned before verification;
- evidence does not contain or digest the plan;
- no approval evidence exists;
- engine/build identity is incomplete;
- empty evidence aggregation succeeds;
- retrying to a new output creates a second run for the same plan;
- the run package lacks before/after/delta and spectral material;
- the installed Moodify distribution reports 0.1.0 while core `pyproject.toml` declares 2.0.0.

## 7. CLI and Agent-readiness assessment

The positive synthetic trace completed:

```text
project init → asset import/SHA-256 → plan create → run execute → run verify
```

The target trace did not complete because there is no canonical CLI operation for specification, analysis, human approval or evidence export. The observed “positive” apply is itself the negative approval exercise.

| Exercise | Observed behavior |
|---|---|
| Modify source after planning | blocked, exit 4 `SOURCE_HASH_MISMATCH` |
| Alter plan after approval | no approval concept; invariant cannot be tested |
| Change engine version | no engine version in plan; cannot invalidate |
| Omit `must_preserve` | Bridge schema rejects it, core plan bypass accepts desired gain only |
| Preserve/change conflict | two lexical pairs detectable; three required semantic cases ignored |
| Failure/interruption during apply | not safely verified; no staging/recovery protocol |
| Evidence generation failure | missing source still writes bundle successfully |
| Retry completed operation | same output blocked; new output duplicates run |
| Noninteractive execution | subprocess/captured execution succeeds without prompt |
| Malformed JSON | structured error, exit 2 |

## 8. Failure and recovery assessment

The source-hash and output-exists guards fail closed. The broader production transaction does not. Audio is written directly to the final run directory; package completion is not atomic; no approval survives/revokes by exact revision; no idempotency key prevents duplicate logical runs; rollback is absent. Evidence failure does not prevent a bundle from being written. Interrupted apply/evidence behavior remains unverified and must not be assumed safe.

## 9. Current architecture

The current-state diagram, bypasses and module table are in `CODEX_MOODIFY_CURRENT_ARCHITECTURE.md`. The central finding is architectural plurality rather than layering: Bridge, core domain, CLI-v2, v0.1 and Runtime each own parts of the target lifecycle without a single authoritative application service.

## 10. Target architecture comparison

The target layers are mostly present as components, but only analysis and basic CLI/execution are operational. Production case, identity constraints, approval, verification and evidence are mixed or disconnected. Replaceable engines cannot yet be changed while preserving plan/approval/evidence meaning.

## 11. Critical contradictions

1. Audio can be applied without an approved plan.
2. Desired change can bypass preserve/avoid constraints.
3. A successful status is reached before verification.
4. Evidence can be generated without actual evidence inputs.
5. Public legacy processing remains a tested bypass.
6. Documentation/handoffs describe a closed loop that omits the product-defining human gate.

No tested evidence showed silent in-place source overwrite, GUI dependency or silent engine substitution in the CLI-v2 trace.

## 12. Highest-risk gaps

- No canonical production-case aggregate and immutable revision chain.
- No apply invariant binding spec, plan, source, approval and engine.
- No mandatory VERIFIED/PACKAGED transition.
- No preservation verification or semantic conflict disposition.
- No sealed evidence manifest.
- No safe idempotent execution/recovery transaction.
- Critical domain/Bridge test environments are not currently runnable as documented.

## 13. Recommended implementation sequence

The first milestone should be **“one fail-closed production case”**, not more DSP:

1. Freeze one canonical case/spec/plan/decision schema and digest rules.
2. Create one application service that enforces the full apply invariant.
3. Route one native gain action through it; quarantine public bypass status claims.
4. Add explicit APPLIED → VERIFIED → PACKAGED states and sealed evidence.
5. Prove all negative invariant tests, then add a second adapter conformance test.
6. Only afterward broaden DSP, batch and Agent endpoints.

## 14. Evidence references

- `artifacts/audits/product_alignment/codex/runtime_exercises.json`
- `artifacts/audits/product_alignment/codex/core_tests.xml`
- `artifacts/audits/product_alignment/codex/core_runnable_tests.xml`
- `artifacts/audits/product_alignment/codex/bridge_tests.xml`
- `artifacts/audits/product_alignment/codex/run_audit_exercises.py`
- `artifacts/audits/product_alignment/codex/environment_summary.md`
- `CODEX_MOODIFY_CAPABILITY_MATRIX.csv`
- `CODEX_MOODIFY_CURRENT_ARCHITECTURE.md`
- `CODEX_MOODIFY_ALIGNMENT_BACKLOG.md`

## 15. Unverified areas

- Full Bridge `refine_prepare` runtime: system Python lacks `pyarrow`; Bridge code uses Python 3.12-only syntax, while its `.venv` lacks Pydantic/Pytest.
- Interruption at each renderer/evidence write phase.
- Matchering and Rubber Band end-to-end processing under the current shell environment.
- Bit-for-bit repeatability across machines and engine versions.
- Concurrent execution, cancellation, Unicode path traversal and batch scale.
- All legacy/runtime file writers and any external API surface.
- Artistic preservation accuracy on real music; no copyrighted audio was used.
