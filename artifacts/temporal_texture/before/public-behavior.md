# Moodify Public Behavior Baseline

Captured: 2026-08-04 · Branch: `codex/mainline-cloud-dev-20260603` · HEAD: see `HEAD.txt`

This file lists the external contracts that wave-1 refactoring must NOT change without
documented authority. Sources: CLI parser definitions, test expectations, existing docs.

## 1. CLI — `moodify` (moodify-core-package/src/moodify/cli.py)

Audio processing + analysis entry point. Subcommands observed at lines 628–806:

- `analyze` — spectrum analysis → PNG + JSON (v0.1.0)
- `process` — one-shot processing → WAV
- `batch` — batch process a directory of audio files
- `emotions` / `crafts` / `presets` / `v01-presets` — list emotion/preset/craft catalogs
- `serve` — start API service
- `audacity macros list` / `audacity macro run` — Audacity refinement macro engine + evidence
- `v01-analyze` / `v01-process` — v0.1.0 pipeline entry points
- `transcribe` / `transcribe-stems` — audio → MIDI (v0.2 stems)
- `legacy-analyze` / `legacy-process` — legacy diagnostics
- `evaluate-run` / `evaluate-single` / `evaluate-status` — AI evaluation loop + D-value calibration
- `capability probe` / `regenerate` / `list` — capability registry
- `score import-midi` / `export` / `backends` — canonical MoodifyScore JSON
- `daw engines` / `validate` / `plan` / `render` / `verify` — CLI-first DAW

## 2. CLI — moodify_runtime/cli.py (runtime operations)

Argparse root with `dest="command"`, required subcommand. Subcommands (lines 79–402):

- Core loop: `register` → `plan` → `run` → `report` → `craft`; plus `all` (chained)
- `failures` / `next` — failure analysis and next-round suggestions
- Operator console: `operator-create`, `operator-list`, `operator-attach-run`,
  `operator-detail`, `operator-deliver`, `operator-delivery-get`, `operator-delivery-list`,
  `operator-plan-runtime`, `operator-authorize-rights`, `operator-show-plan`,
  `operator-run`, `operator-report`
- Studio: `studio-client-*`, `studio-project-*`, `studio-order-*`, `studio-note-*`
- Scheduler: `scheduler-schedule` / `-requests` / `-allocate` / `-record` / `-runs` / `-costs`
- Calibration: `calibration-set-create` / `-sets` / `-review` / `-reviews` / `-audit`
  / `-audits` / `-threshold` / `-thresholds`
- Craft: `craft-list`, `craft-safety-check`, `craft-writeback`, `craft-records`,
  `craft-plan`, `craft-run`, `craft-inspect`
- Evidence: `pdf-report render-single` / `render-comparison` / `inspect`
- Tidal: `tidal-intel`, `tidal-intel-brief`, `tidal-ops`, `tidal-state`, `tidal-alert(s)`,
  `tidal-ack`, `tidal-note(s)`
- Data loop: `data-loop run` / `report`
- Health: `runtime-status`, `runtime-health`, `runtime-supervisor-start`

## 3. Job/queue state vocabulary

- Run queue rows: status ∈ `pending`, `retry` (runner.py:39 selects these)
- Operator job: `delivered` is a terminal state (operator_console.py:1105)
- Approval gate: `human_approved: bool` + `approved_by` identity threaded through
  `mrs_can_release()` / `hardening_gates` / `operator_api` / `craft_evidence`
- Run queue JSONL files: `input_registry.jsonl`, `run_queue.jsonl` (per cli.py help text)

## 4. Evidence/file formats

- v0.1.0 analysis: PNG + JSON per track; `v01-process` → WAV
- Acoustic CT PDF report bundle with manifest (pdf-report render-*)
- Craft chain manifest (craft-plan/craft-run/craft-inspect)
- Operator report bundle (operator-report)
- Delivery record markdown + structured record (operator-deliver)

## 5. Audio-processing semantics (must be preserved)

- Spectrum analysis / processing chain / quality gate outputs (v01-pipeline)
- DSP coefficients, artistic judgments, scoring thresholds — out of scope for wave 1
- Preset catalog values (craft_presets) are data, not code

## 6. Notes

- The 16-state control spine referenced in CODEX_TASK.md maps onto the operator/approval
  gates above; the spine is enforced via `mrs_can_release` and job lifecycle commands.
- Android app (apps/android) is outside this wave's audit scope (Kotlin not scanned by
  the stdlib auditor).
