# Moodify Sound Protocol (MSP) 0.2 — Analysis Jobs and Report Trio

**Status:** EXPERIMENTAL, implemented local CLI contract; not frozen, not a network protocol or deployed service. MSP/0.1 remains valid and unchanged; 0.2 adds a second job `type` on top of the same Core.

## Why 0.2 exists

MSP/0.1 can only *process* audio. An agent that wants to understand an audio file first — before deciding whether to process it, and without side effects — had no protocol surface. MSP/0.2 adds a read-only `analyze` job that produces a measurement report and a *draft* post-processing plan, and makes the judgment boundary machine-readable so an AI consumer cannot accidentally mistake measurement for musical judgment.

The discipline this encodes (Canon v2.0 "Generated is not finished", Canon invariant against black-box one-click mastering):

1. **No single total score.** The report lists measurements with per-metric *visibility* declarations (what the metric can see, and what it is blind to). It never collapses them into one number.
2. **Judgment is layered.** `judgment_boundary` records, per layer, whether it was EXECUTED, NOT_RUN, or NOT_PROMISED. 0.2 analyze jobs execute only Layer 1 (technical measurement). Layers 2–5 (comparison, musical, production, cultural) are `NOT_PROMISED`.
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
moodify protocol process job.json     # type decides analyze vs process
```

An analyze job runs the existing `release.analyze_to_case` (the 1.0 scan chain: ffmpeg probe → wave/spectral representation → BS.1770/true-peak/LRA/stereo/spectral metrics) plus `auditory/protocol_report.py` report assembly. It writes a case bundle containing `report.json`, `report.md`, and `report.html` and prints one JSON result with `status: analyzed_review_required` and `review_required: true`.

A 0.2 `process` job has the same fields as 0.1 plus `"type": "process"` and behaves exactly like a 0.1 job (preset processing via `v01_pipeline.process_audio`).

## The report trio

- **`report.json`** — `moodify.msp_report/0.2`, jsonschema-validated, the AI-consumable authority. Sections: `measurements` (each with `visibility`, `group`), `findings`, `plan`, `judgment_boundary`, `technical_state` (`workflow_decision`: `NO_TECHNICAL_BLOCKERS` | `REVIEW_RECOMMENDED` | `REMEDIATION_REQUIRED`), `provenance` (core version, scan-profile parameters SHA-256, judgment-rules version, ffmpeg version).
- **`report.md`** — deterministic text rendering for humans and diffs.
- **`report.html`** — single-file display screen: inline CSS only, spectrograms embedded as base64 PNG, no CDN, no JavaScript. Findings render as fixed severity badges; the boundary and footer state what the report does *not* judge.

Non-numeric probe fields (e.g. `source_sha256`) never enter `measurements`; they live in `source`/`provenance`. Metrics that could not be computed are kept with `status: UNAVAILABLE` and a null value plus warnings — absence is reported, not hidden.

Re-rendering without recomputation:

```powershell
moodify report <case_id|path/to/report.json>
```

## What this does not claim

The report is evidence of *what was measured*, not evidence that audio sounds good, that identity is preserved, or that the draft plan is correct. The plan has not been executed. Layer 2 comparison requires a reference; Layers 3–5 are human/production judgment the machine does not promise. Agents must not treat `analyzed_review_required` as `verified`, and must not execute `plan.nodes` without an explicit 0.2 `process` (or Mix Graph) job.

## Freeze gate

Before `moodify.msp_report/0.2` or `moodify.sound/0.2` is promoted from EXPERIMENTAL to frozen: golden evidence pack under `artifacts/` with full report trios for at least three pilot tracks (including a known-good reference), byte-identical re-render proof for md/html, and the schema round-trip test — same precedent as the Mix Graph v0.1 golden freeze.

## Scope and next version

MSP/0.2 exposes read-only analysis plus the 0.1 process surface on one Core. Mix Graph payloads over the protocol (v0.3 target), before/after comparison jobs (Layer 2), and cloud execution remain targets, not implemented claims. Version strings are exact; incompatible jobs must fail rather than be guessed into a new format.
