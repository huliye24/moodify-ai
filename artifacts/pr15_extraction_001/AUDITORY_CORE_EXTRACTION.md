# Auditory Core Extraction

## Current Canonical Baseline

The current canonical executable path remains `v01_pipeline.py`: Import → Analyze → Diagnose → Process → Export. It is small and covered by the 109-test PR #16 baseline.

## Candidate Subsystems

| Candidate | Capability | Tests | Duplicate / Risk | Evidence Output | Action |
|---|---|---|---|---|---|
| `moodify/auditory/` | Decode, WSE metrics, timeline, stereo, scan, compare, judgment | 23 auditory tests reported historically; current PR CI failures are mostly missing ffmpeg | Duplicates v0.1 analysis; filesystem-shaped service API | hashed scan/comparison manifests, metrics, timelines | **EXTRACT** contract and pure logic; reimplement integration |
| `features/`, `perception/` | chroma, F0, perceptual scales, masking proxies | branch tests exist but are not isolated in current CI result | Some metrics are proxies and overlap diagnosis | dataclasses/arrays, limited provenance | **EXTRACT** only after method-version contract |
| `score_engine/` | MIDI ingest, score model, MusicXML, roundtrip, optional MuseScore | 6 files of score-engine tests | External MuseScore caused CI portability failures | deterministic score serialization and roundtrip report | **EXTRACT** as experimental MSE adapter |
| `transcription_pipeline/` | stems/transcription pipeline | mixed external-tool tests | Tool-heavy and overlaps capability registry | manifests | **KEEP_AS_REFERENCE / REIMPLEMENT** |
| `processing/` | DSP interventions | v0.1 tests plus branch tests | Multiple processing/orchestration entry points | processed audio and reports | Keep v0.1 intervention adapter canonical during migration |

## WSE

The strongest extraction candidate is the `auditory/` scan/compare path: source hashes, profile hashes, method-labelled values, timelines, stereo measurements, before/after normalization, fail-closed comparison, and manifest hash verification. Extract the contracts first; do not copy its directory-shaped orchestration unchanged.

## MSE

`score_engine/` is a coherent experimental MSE island with deterministic serialization. MIDI parsing and pure model/serialization tests are independently migratable. MuseScore and transcription backends remain optional adapters, not core dependencies.

## Judgment

`auditory/judgment.py` correctly separates technical assessment from artistic approval and defaults to human listening. Its rules are candidates for extraction, but thresholds require versioned provenance and benchmark evidence.

## Intervention

Keep the verified v0.1 DSP chain as the only canonical intervention adapter initially. PR #15 intervention implementations may later register behind one interface; they must not own case state.

## Verification

Extract source identity, method/profile version, before/after pairing rules, artifact hashes, technical judgment, and explicit human-authority escalation. Plots are artifacts, not MeasurementRecords.

## Recommended Future Authority

```text
moodify.auditory
├── source       # immutable identity and decode contract
├── representation  # WSE/MSE MeasurementRecords
├── judgment     # technical assessment, uncertainty, escalation
├── intervention # registered adapters; v0.1 DSP first
└── verification # comparison, invariants, EvidenceArtifacts
```

The public entry should accept/return canonical contracts rather than raw directory layouts. `v01_pipeline.py` remains an adapter until parity tests pass.

## Archive / Delete-Later

Archive golden-run scripts and historical reports after extracting test fixtures. Delete generated spectra, bundles, and duplicated packaged tool outputs only in a later cleanup PR.
