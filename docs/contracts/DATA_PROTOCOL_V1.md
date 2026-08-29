# Moodify Auditory Data Protocol v1 (Frozen)

Protocol ID: `MFY-DATA-PROTOCOL-001`
Status: FROZEN — 2026-08-10, after MFY-DATA-FACTORY-001 pilot on 4 owned tracks
Schema version: `1.0`
Supersedes: draft in the MFY-DATA-FACTORY-001 task package

## Scientific unit

The primary independent experimental unit is a **song-level ProductionCase**.
Timeline frames are repeated measurements inside a case and must not be counted
as independent songs during train/test splitting.

## Experimental relation

For source state `X`, intervention `I`, output state `Y`, delta `Δ`, and human
preference `H`:

`X + I → Y → Δ(X,Y) → H`

Moodify's first learnable asset is the mapping between source evidence,
intervention parameters, measurable consequence, and human judgment.

## Candidate semantics

- A: smallest useful intervention (CONSERVATIVE)
- B: balanced intervention (BALANCED)
- C: stronger exploratory intervention (EXPLORATORY)

Candidates differ primarily in intervention strength while preserving the same
technical objective, creating interpretable response curves instead of three
unrelated "styles". A/B/C are intervention intensities, not musical genres.

## Case directory (frozen)

```text
cases/<case_id>/
  00_source/            # immutable source byte copy (preserved extension)
  01_source_scan/       # BEFORE scan: metrics.json + timeline + NPZ + spectrograms
  02_plans/             # plan_A.json / plan_B.json / plan_C.json (persisted before processing)
  03_candidates/        # candidate_{A,B,C}.wav + candidate_{A,B,C}.json (registration)
  04_after_scan/        # A/ B/ C/ — AFTER scan per candidate
  05_comparison/        # source_vs_A/ source_vs_B/ source_vs_C/ (deltas + judgment + report)
  06_human_review/      # review.json (template; completed by human operator)
  07_learning/          # training_record.json + pairwise_preferences.jsonl (finalize step)
  case_manifest.json    # versions, hashes, status
  production_case.json  # canonical ProductionCase contract (lifecycle/authority)
```

## Machine assets (authoritative for analysis)

- metrics JSON (`metrics.json`)
- timeline JSONL (`timeline_metrics.jsonl`)
- NPZ/STFT arrays (`analysis_data.npz`)
- intervention parameter JSON (`02_plans/plan_{A,B,C}.json`)
- delta JSON (`05_comparison/source_vs_{X}/metrics_delta.json`)
- candidate/source hashes (`case_manifest.json`, `03_candidates/*.json`)
- review JSON (`06_human_review/review.json`)
- training JSONL (`07_learning/pairwise_preferences.jsonl`, `cases.jsonl`)

Human-readable evidence (spectrogram PNG, contact sheets, reports) is
derivative; plots must be reproducible from machine assets whenever practical.

## Version fields persisted per case

- `data_protocol_version` = `MFY-DATA-PROTOCOL-001`
- `scan_profile_id` + `scan_profile_hash`
- `plan_generator_version` = `MFY-ABC-HEURISTIC-001`
- `moodify_package_version`
- source SHA-256; candidate SHA-256 per A/B/C
- judgment authority = `moodify.auditory.judgment` (canonical)

Records produced by incompatible versions must not be silently compared.

## Human review contract

Ranking domain is exactly `SOURCE, A, B, C`; all four ranked exactly once.
Rejected candidates and free-text notes are supported. A complete 4-item
ranking generates exactly six pairwise preference rows.

## Dataset split rule

Future model evaluation MUST split by source song / ProductionCase, never
randomly by timeline frame. Otherwise leakage will exaggerate model quality.

## First-stage scale interpretation

100 source songs × 3 candidates = 300 intervention outcomes. With ranking over
SOURCE/A/B/C, each song yields 6 ordinal pairwise relations = 600 preference
relations. Enough for serious exploratory analysis and simple ranking or
calibration models; not automatically enough for a large neural model.

## Plan-v1 rule provenance

Plan generation v1 is deterministic heuristic seeded from measured scan metrics
(presence-band energy, low-mid/bass energy, air energy, crest factor) with
clipping/true-peak guardrails. Thresholds are calibration seeds versioned with
`PLAN_GENERATOR_VERSION`, not psychoacoustic truths. Machine judgment never
grants artistic approval; human ranking is a separate authority layer.
