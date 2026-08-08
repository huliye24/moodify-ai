# Moodify Project Analytics

This directory is the single home for repeatable project analytics. Product
code, generated audio, experiments, and task handoffs must not store analytics
state here.

## Operating model

Every analysis run is immutable and timestamped in Asia/Shanghai:

```text
project_analytics/
  ANALYSIS_CATALOG.md        # what to analyse and when
  metric_contracts.json     # stable definitions and denominators
  registry.jsonl            # append-only index of completed runs
  schemas/                   # machine-checkable run contracts
  scripts/                   # reproducible collectors
  runs/
    YYYY-MM-DDTHHMMSS+0800/
      <analysis-id>/
        manifest.json       # identity, time, scope, sources, validation
        snapshot.json       # bounded calculated metrics
        report.md           # decision-facing interpretation
```

Use the actual start time for the directory and preserve the ISO timestamp,
including timezone, inside `manifest.json`. Never overwrite an old run to make
history look cleaner. A correction is a new run that names the superseded run.

## Standard flow

1. Select an analysis from `ANALYSIS_CATALOG.md`.
2. Freeze the question, grain, metric definitions, source paths, and timestamp.
3. Run the relevant script into a new timestamped directory.
4. Validate calculations, denominators, source conflicts, and test exit codes.
5. Write the decision and caveats to `report.md`.
6. Append exactly one entry to `registry.jsonl`.
7. Compare with earlier compatible runs only when metric-contract versions match.

## First implemented collector

```powershell
py -3.11 project_analytics/scripts/collect_project_health.py
```

The collector creates a new timestamped `project-health` run, executes the Core
test collection gate, writes the snapshot/report/manifest, and registers the
run. Use `--skip-tests` only for a clearly labelled partial diagnostic.

