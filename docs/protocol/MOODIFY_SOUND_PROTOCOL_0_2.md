# Moodify Sound Protocol (MSP) 0.2 — Analysis, Comparison, and Report Trio

**Status:** EXPERIMENTAL, implemented local CLI contract; not frozen, not a network protocol or deployed service. MSP/0.1 remains valid and unchanged; 0.2 adds two job `type`s on top of the same Core.

## Why 0.2 exists

MSP/0.1 can only *process* audio. An agent that wants to understand an audio file first — before deciding whether to process it, and without side effects — had no protocol surface. MSP/0.2 adds a read-only `analyze` job that produces a measurement report and a *draft* post-processing plan, a `compare` job that measures one file against a reference (Layer 2), and makes the judgment boundary machine-readable so an AI consumer cannot accidentally mistake measurement for musical judgment.

The discipline this encodes (Canon v2.0 "Generated is not finished", Canon invariant against black-box one-click mastering):

1. **No single total score.** The report lists measurements with per-metric *visibility* declarations (what the metric can see, and what it is blind to). It never collapses them into one number.
2. **Judgment is layered.** `judgment_boundary` records, per layer, whether it was EXECUTED, NOT_RUN, or NOT_PROMISED. `analyze` jobs execute only Layer 1 (technical measurement); `compare` jobs additionally execute Layer 2 (loudness-aligned relative deltas). Layers 3–5 (musical, production, cultural) are `NOT_PROMISED` for both.
3. **Plans are drafts.** `plan.status` is always `DRAFT_PLAN_NOT_EXECUTED`. Only conservative, reversible standard operators are drafted (currently: `limiter` with `-1.0 dBFS` ceiling when true-peak margin is below 0.5 dB). Clipping is deliberately *not* mapped to an operator — repairing clipping requires a remix/re-render decision upstream, so it appears as a note, never an auto node.
4. **Findings cite their evidence.** Every finding carries `code`, `severity`, the metric it came from, and `check` (`absolute_rule` for standalone absolutes, `delta_rule` for the Core's threshold table).

## Analyze job

```json
{
  "protocol": "moodify.sound/0.2",
  "type": "analyze",
  "source": "audio/source.wav",
  "output_dir": "outputs"
}
```

Paths are resolved relative to the job file. The four keys are required and exhaustive: unknown keys are rejected. Supported input extensions are WAV, FLAC, MP3, AIFF, and M4A; decoding requires **ffmpeg (with ffprobe) on PATH or the WinGet Links location** — audio decode in the analyze path is ffmpeg-first. Existing cases are never intentionally overwritten.

```powershell
moodify protocol validate job.json
moodify protocol process job.json     # type decides analyze vs compare vs process
```

An analyze job runs the existing `release.analyze_to_case` (the 1.0 scan chain: ffmpeg probe → wave/spectral representation → BS.1770/true-peak/LRA/stereo/spectral metrics) plus `auditory/protocol_report.py` report assembly. It writes a case bundle containing `report.json`, `report.md`, and `report.html` and prints one JSON result with `status: analyzed_review_required` and `review_required: true`.

A 0.2 `process` job has the same fields as 0.1 plus `"type": "process"` and behaves exactly like a 0.1 job (preset processing via `v01_pipeline.process_audio`).

## Compare job (Layer 2)

```json
{
  "protocol": "moodify.sound/0.2",
  "type": "compare",
  "source": "audio/candidate.wav",
  "reference": "audio/reference.wav",
  "output_dir": "outputs"
}
```

Five keys, exact. `source` is the candidate; `reference` is the baseline. The job analyzes **both** files through the same scan path (two independent case bundles), validates the pair, computes deltas, renders delta spectrograms, and writes a compare report trio plus two delta PNGs to `<output_dir>/compare_<candidate>_<reference>/`. Result status: `compared_review_required`.

Pair validation (fail-closed, `ComparisonDurationMismatch`/`ComparisonChannelMismatch`/`ScanProfileMismatch` → exit 2): same scan-profile hash, duration within **±50 ms**, equal channel count. Independent case IDs are expected — the same-case `validate_pair` semantics used by the internal before/after flow are unchanged. Comparing musically different material is meaningless for mastering deltas and is rejected by the duration check, not guessed around.

What Layer 2 reports — and what it does not:

- **Loudness alignment first.** The candidate is gain-normalized to the reference's integrated LUFS before spectral comparison (`gain-to-before-LUFS`); a pure loudness change therefore yields near-zero normalized band deltas. The applied gain is published in `comparison.loudness_normalization`.
- **Relative deltas are described, never graded.** `metric_deltas` carry before/after/Δ/direction per metric (with the metric's visibility declaration); `band_deltas` carry raw and loudness-normalized band-ratio changes. **No significance threshold is applied** — "is this change better" belongs to Layer C calibration, and `comparison.visibility_note` says so in the report itself.
- **`judgment_boundary.layer2_comparison = EXECUTED`** on compare reports only. An analyze report must not carry a `comparison` section, and a compare report must — the schema enforces both directions.
- Absolute findings and the draft plan still describe the *candidate only*; the reference never silently alters them.

## The report trio

- **`report.json`** — `moodify.msp_report/0.2`, jsonschema-validated, the AI-consumable authority. Sections: `measurements` (each with `visibility`, `group`), `comparison` (compare jobs only), `findings`, `plan`, `judgment_boundary`, `technical_state` (`workflow_decision`: `NO_TECHNICAL_BLOCKERS` | `REVIEW_RECOMMENDED` | `REMEDIATION_REQUIRED`), `provenance` (core version, scan-profile parameters SHA-256, judgment-rules version, ffmpeg version).
- **`report.md`** — deterministic text rendering for humans and diffs.
- **`report.html`** — single-file display screen: inline CSS only, spectrograms embedded as base64 PNG, no CDN, no JavaScript. Compare reports add an L2 section: pair checks, normalization gain, the delta table, and a four-panel contact sheet (reference spectra + delta spectra). Findings render as fixed severity badges; the boundary and footer state what the report does *not* judge.

Non-numeric probe fields (e.g. `source_sha256`) never enter `measurements`; they live in `source`/`provenance`. Metrics that could not be computed are kept with `status: UNAVAILABLE` and a null value plus warnings — absence is reported, not hidden.

Re-rendering without recomputation (works for analyze and compare report trios):

```powershell
moodify report <case_id|path/to/report.json>
```

## Threshold provenance and calibration (Layer C)

Every threshold in `UNIVERSAL_THRESHOLDS` (judgment-rules **v1.1**) carries provenance in `THRESHOLD_PROVENANCE`: `source_class` (`STANDARD` | `EXPERIMENTAL` | `DEFAULT`), the citation itself, the date and commit where the value was fixed (`2026-08-02`, `5452ff44` — the value set is unchanged since introduction), `calibration_status`, and whether the limit is `calibratable`. Status 2026-10-02: **0 STANDARD / 0 EXPERIMENTAL / 16 DEFAULT** — every limit is published as `DEFAULT_UNCALIBRATED`. Uncalibrated thresholds are engineering defaults and must not be consumed as perceptually validated limits.

Where this surfaces:

- every case bundle's `judgment_rules.json` carries `threshold_provenance` and `calibration_summary`;
- every report carries `provenance.judgment_calibration` (machine-readable) plus the calibration counts and note in the rendered md/html provenance section; findings carry `reference_basis` / `calibration_status` / `threshold_source_class`;
- the sensitivity report (`moodify.auditory.sensitivity`, evidence pack `artifacts/msp02_calibration_001/`) sweeps every rule through the production `evaluate_risk_flags` path — all 16 observed flip points equal the declared thresholds — and maps rules to `auditory.lab` perturbation ladders able to produce threshold-crossing stimuli (reachability only; no threshold value is derived from ladders yet).

Layer C discipline is provenance only: changing a threshold value is a recalibration and requires experiment evidence plus a human-decision record (pinned by tests).

## What this does not claim

The report is evidence of *what was measured*, not evidence that audio sounds good, that identity is preserved, or that the draft plan is correct. The plan has not been executed. Layer 2 reports relative deltas; it does not judge whether they are improvements (no significance thresholds exist in this layer). Layers 3–5 are human/production judgment the machine does not promise. Agents must not treat `analyzed_review_required`/`compared_review_required` as `verified`, and must not execute `plan.nodes` without an explicit 0.2 `process` (or Mix Graph) job.

## Freeze gate

Before `moodify.msp_report/0.2` or `moodify.sound/0.2` is promoted from EXPERIMENTAL to frozen: golden evidence packs under `artifacts/` — `msp02_analysis_001` (analyze: four cases incl. a clipped negative control), `msp02_compare_001` (compare: loudness-aligned A/B golden pairs), and `msp02_calibration_001` (threshold provenance registry + sensitivity report) — with full report trios, byte-identical re-render proof for md/html, and the schema round-trip tests — same precedent as the Mix Graph v0.1 golden freeze.

## Scope and next version

MSP/0.2 exposes read-only analysis, loudness-aligned comparison, threshold provenance, and the 0.1 process surface on one Core. Mix Graph payloads over the protocol (v0.3 target), perceptual significance calibration (grading deltas as better/worse — Layer C delivered provenance and sensitivity verification, not perceptual limits), and cloud execution remain targets, not implemented claims. Version strings are exact; incompatible jobs must fail rather than be guessed into a new format.
