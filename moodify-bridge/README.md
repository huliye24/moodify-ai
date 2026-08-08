# moodify-bridge

`moodify-bridge` is a local-first, append-only research-production bridge for Moodify. It records immutable production cases, content-addressed assets, measurements, evidence, hypotheses, governed rules, and golden-case replay results. It does **not** train an audio model or mutate source/project files.

## One-Point Refine

The single default action is **refine** — deliberate, reversible, evidence-backed craft in service of the work's own identity. One command:

```powershell
py -3.12 -m moodify_bridge.cli refine prepare SPEC.yaml --output-dir NEW_DIR
```

The default result surface expresses five narrative centres in a 12-word canon:
- **Essence** — what the work is
- **Protect** — what must survive, including what must not occur
- **Allow** — what may change
- **Action** — what the system did
- **Entrust** — what remains for a human to decide

Technical evidence (gates, measurements, ledger, candidate history) is preserved in `evidence/` and expanded on demand. No internal acronyms, no automatic scores, no false claims of improvement.

In Edition 0.1, `source` is the path to an existing ProductionCase YAML
manifest. `refine prepare` prepares a plan and a verifiable evidence package;
it does not process audio or claim that a candidate is final.

Full principle: `docs/strategy/MOODIFY_ONE_POINT_PRINCIPLE.md`. Language contract: `docs/tasks/deepseek/DSK-MFY-ONE-POINT-006/LANGUAGE_CANON.md`.

### Optional lyrics evidence

`OnePointSpec` may reference an authorized UTF-8 lyrics file through `lyrics`.
Moodify records its identity, explicit section labels, normalized repetition,
and an optional human-authored `declared_intent`. It performs no sentiment,
psychological, identity, or "true meaning" inference.

```yaml
lyrics:
  path: E:/moodify/authorized/lyrics.txt
  language: zh-CN
  version: authorized-draft
  rights_basis: owner-provided
  declared_intent: "A human-authored statement of direction."
```

The path must resolve inside the Moodify workspace. Authorized content is
copied only into `evidence/lyrics/` and covered by the package manifest; lyrics
body text never appears in CLI output, `result.json`, or the default summaries.
Use `rights_basis: unknown` when authorization is unresolved: the body is not
read and the result becomes `NEEDS_EVIDENCE`. Omitting `rights_basis` is an
invalid strict contract. Files must be non-empty UTF-8 text without NUL bytes
and no larger than 1 MiB.

## Storage contract

- `.moodify-bridge/ledger.duckdb`: metadata, immutable initial case snapshots, append-only events, approvals, and validation results.
- `.moodify-bridge/metrics/`: larger metric records as Zstandard-compressed Parquet.
- User-selected `.yaml` files: hypotheses, rules, approvals, and evidence packets.
- Audio/project assets remain at their local paths and are identified by SHA-256 plus byte size.

Raw `cases` rows are insert-only through the API. A correction is a `revision_appended` ledger event; it never rewrites the archived raw record. Rule state changes are one-step lifecycle transitions and every promotion requires a separately authored `HumanApproval` YAML record.

## Install (Python 3.12)

```powershell
cd E:\moodify\moodify-bridge
py -3.12 -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -e ".[dev,audio]"
```

The `audio` extra is needed only to read audio and compute integrated loudness. LRA and true peak remain explicit nulls until a standards-compliant backend is added. No proxy values are invented.

## Exact CLI usage

Run commands from the repository directory so paths in the demonstration manifest resolve correctly.

```powershell
# Create and validate the immutable synthetic golden case
moodify-bridge case create demo/case.yaml --root .demo-ledger
moodify-bridge case validate 11111111-1111-4111-8111-111111111111 --root .demo-ledger

# Hash any asset without modifying it
moodify-bridge assets hash demo/assets/source.txt

# Measure an actual archived audio asset (the demo intentionally has none)
moodify-bridge measure run CASE_UUID ASSET_UUID path/to/audio.wav --root .moodify-bridge

# Compile evidence; absent measurements become warnings
moodify-bridge evidence compile 11111111-1111-4111-8111-111111111111 demo/evidence.yaml --root .demo-ledger

# Compare equal-length, equal-sample-rate audio; optionally store metrics in Parquet
moodify-bridge compare reference.wav candidate.wav --output comparison.parquet

# Create a hypothesis YAML
moodify-bridge hypothesis create H-002 1.0.0 "Gain transparency" "Scalar gain preserves waveform shape." --evidence "correlation and residual" --created-by researcher --output hypotheses/H-002.yaml

# Validate a rule against governance requirements
moodify-bridge rule validate demo/rule.yaml --root .demo-ledger

# Promote exactly one lifecycle step with explicit human-authored approval
Copy-Item demo/rule.yaml demo/promoted-rule.yaml
moodify-bridge rule promote demo/promoted-rule.yaml experimental demo/approval.yaml --root .demo-ledger

# Replay the canonical archived golden case
moodify-bridge regression run 11111111-1111-4111-8111-111111111111 demo/case.yaml --root .demo-ledger

# Build reports (writes reports/demo.md and reports/demo.html)
moodify-bridge report build 11111111-1111-4111-8111-111111111111 reports/demo --root .demo-ledger
```

Use `moodify-bridge COMMAND --help` or `moodify-bridge COMMAND SUBCOMMAND --help` for option details.

## Metrics

Adapters cover peak/RMS/crest factor; integrated loudness/LRA/true peak; spectral entropy/centroid/flux; configurable frequency-band fractions; waveform correlation; least-squares scalar gain; relative residual; difference SNR; and left-right correlation. Undefined metrics (silence, short signal, missing backend/data, wrong channel shape) are represented as `null` with warnings.

## Schema/versioning and migrations

All Pydantic v1-domain models carry `schema_version: 1.0.0`, reject unknown fields, and are frozen. SQL migrations live in `migrations/` and are recorded in `schema_migrations`. Additive or breaking schema work should introduce a new model namespace/version and a new numbered migration; archived payloads retain their original schema version.

## Tests

```powershell
python -m pytest
python -m mypy src
python -m ruff check src tests
```

Tests use fixed timestamps/UUIDs and synthetic arrays. They verify strict schemas, deterministic metrics, immutable case insertion, appended revisions, explicit missing measurements, and mandatory human approval.

## Unified PPE Baseline

A single command executes the full baseline pipeline and writes all artifacts:

```powershell
py -3.12 -m moodify_bridge.cli ppe run demo/case.yaml --output-dir NEW_RUN_DIR
```

The output directory must be new or empty. Existing directories are rejected.

Artifacts generated:
```
NEW_RUN_DIR/
  run_manifest.json        # full run metadata
  environment.json         # Python version, platform, packages
  command_results.jsonl    # per-step actions, exit codes, errors
  gate_results.json        # six-gate evaluation (PASS/WARN/FAIL)
  evidence.yaml            # evidence packet
  ledger/ledger.duckdb     # immutable case ledger
  reports/case.md          # Markdown report
  reports/case.html        # HTML report
  FINAL_STATUS.txt         # PASS / PASS_WITH_WARNINGS / FAIL
```

`run_manifest.json` includes an `artifact_hashes` map for the eight material
artifacts created before the manifest (environment, command log, gates, final
status, evidence, ledger, and both reports). Consumers should recompute every
listed SHA-256 before trusting a run. The manifest cannot contain its own hash;
archive systems may hash it externally.

Six gates: `input_complete`, `identity_consistent`, `measurement_available`, `candidates_comparable`, `human_approved`, `report_complete`. A blocking FAIL gate results in `FINAL_STATUS=FAIL`. WARN gates result in `PASS_WITH_WARNINGS`. No fabricated data — missing measurements stay missing, missing candidates are declared.

### Stable CLI errors

Expected user errors return clean messages with stable exit codes and no Python traceback:

| Error | Exit code |
|---|---|
| Non-empty output directory | 2 |
| Missing approval file | 2 |
| Approval/rule ID mismatch | 2 |
| Invalid rule transition | 2 |
| Missing case file | 1 (FAIL manifest) |
| Invalid YAML | 1 (FAIL manifest) |

### Rule promotion atomicity

All validations (ID match, version match, transition legality) execute before
database or rule-file writes. Promotion uses a same-directory temporary file and
`.promoting` recovery marker. If the database write succeeds but the atomic file
replace is interrupted, the CLI returns `PROMOTION_RECOVERY_REQUIRED`; the marker
and temporary file remain intact, and retrying the identical command completes
the replace without inserting a duplicate approval. A mismatched or incomplete
marker stops for manual review instead of deleting recovery evidence.

### Approval semantics

`rule validate` outputs three explicit fields:
- `approval_required` — whether the current rule state demands human approval
- `approval_present` — whether an approval record exists for this rule/version
- `approval_gate_satisfied` — whether the approval requirement is met

There is no ambiguous `human_approval: true` with `approval_id: null`.
