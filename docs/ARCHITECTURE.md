# Moodify Architecture

## Overview

Moodify operates with **two parallel mainlines**:

| Mainline | Status | Purpose | Entry Point |
|----------|--------|---------|-------------|
| **v01** | Product mainline | Minimal, stable DSP pipeline | CLI `analyze`/`process`, API `/process` |
| **legacy** | Research pipeline | 6-phase workflow, LLM/RAG, physics experiments | CLI `legacy-*`, internal research |

## Core Principle

**v01 = product; legacy = research.**

- v01 must stay small, fast, and stable.
- legacy can be complex, experimental, and evolving.
- Never reconnect legacy `WorkflowOrchestrator` to the v01 `/process` path.
- Never delete legacy modules.

## Module Map

### v01 Mainline (Product)

```
v01_types.py          Data types (AudioMetrics, DiagnosisReport, ProcessResult)
v01_presets.py        3 presets x 15 DSP params
v01_analyzer.py       FFT spectrum analysis + metrics
v01_diagnostics.py    Rule-based diagnosis reports
v01_pipeline.py       Orchestration: analyze -> diagnose -> process -> export
v01_exporter.py       16-bit WAV export + peak clamp
bands.py              Unified frequency band definitions
config.py             Central path resolution (PROJECT_ROOT)
```

### Legacy System (Research)

```
diagnosis/            18-param DiagnosisEngine, defect classifier, health scorer
orchestration/        6-phase WorkflowOrchestrator
knowledge/            Emotion targets, craft chains, parameter specs
processing/           Pedalboard DSP chain, spectral operators
evaluation/           Batch AI evaluation
calibration/          Online D-value calibration
physics/              B-matrix experiments, validation suite
llm/                  DeepSeek client, RAG prompt assembler
optimizer/            5D strength space search
safety/               Parameter projection + bounds
memory/               SQLite + JSONL processing history
```

### Bridge Layer (Future)

```
reality_metrics.py    MRS (Moodify Reality Score) - distance-to-real metric
bands.py              Unified frequency bands (shared by v01 + MRS)
```

## Data Flow

### v01 Flow (Product Path)

```
Input Audio
  -> v01_analyzer.analyze()        [spectrum + metrics]
  -> v01_diagnostics.diagnose()    [rule-based report]
  -> v01_pipeline.process_audio()  [preset DSP chain]
  -> v01_exporter.export()         [16-bit WAV output]
```

### Legacy Flow (Research Path)

```
Input Audio
  -> Phase 0: Emotion resolution
  -> Phase 1: Diagnosis + defect classification
  -> Phase 1.5: Strength search / RAG recommendation
  -> Phase 2: Audio loading
  -> Phase 3: Spectral enhancement (HPSS)
  -> Phase 4: Spatial reconstruction
  -> Phase 5: (reserved)
  -> Phase 6: Mastering (loudness norm + limiter + export)
```

## Key Design Decisions

1. **Dual mainline**: v01 is the stable product; legacy is the lab. No merging.
2. **No GUI in v0.1.x**: CLI and API only.
3. **Matched-loudness listening**: All A/B comparisons use loudness-matched audio.
4. **Treatment records as engineering memory**: JSON records with human feedback.
5. **Presets over parameters**: Users pick presets, not 15 individual DSP knobs.
