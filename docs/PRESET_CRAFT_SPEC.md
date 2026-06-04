# Preset Craft Specification — MHP-179/180/181

**E-Chain**: ECHAIN-MOODIFY-PRESET-CRAFT-002 | **Date**: 2026-06-04

## Craft Record Schema (MHP-179)

| Field | Type | Description |
|-------|------|-------------|
| craft_id | string | Unique record ID (CRFT_XXXXXXXXXXXX) |
| source_job_id | string | Operator job that produced this craft |
| source_candidate_id | string | Candidate version selected |
| audio_class | string | Project label / genre hint |
| preset | string | DSP preset name |
| processing_chain | string | Processing pipeline description |
| mrs_score_delta | float | MRS improvement |
| risk_conditions | object | over_dark, transient, loudness flags |
| gate_decision | string | approve / reprocess / reject |
| adoption_status | string | experimental→candidate→stable→adopted |
| version_history | array | Status transitions with timestamps |

## Preset Safety Manual (MHP-180)

| Gate | Severity | Failure Action |
|------|----------|----------------|
| over_dark | CRITICAL | Reject preset for this sample |
| over_bright | CRITICAL | Reject preset for this sample |
| transient_damage | HIGH | Reject for this sample |
| vocal_thinning | HIGH | Reject for vocal/piano presets |
| stereo_collapse | MEDIUM | Warn (many inputs are mono) |

## Preset Versioning (MHP-181)

- Presets versioned as `{name}@{major}.{minor}.{patch}`
- Parameter changes = minor bump
- Safety gate threshold changes = patch bump
- Category reassignment = major bump
