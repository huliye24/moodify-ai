# PROJECT SNAPSHOT — Moodify v0.1.0-alpha.1

> Auto-generated snapshot. Updated at each MHP full handoff.
> Target audience: Claude / ChatGPT / future agents needing rapid context recovery.

---

## 1. Current Identity

Moodify v0.1.0 is an **AI music post-processing engine** — not a lyric generator.

```text
import audio → spectrum analysis → diagnosis → DSP preset → export WAV
```

## 2. Version & Tag

- **Version**: 0.1.0
- **Git tag**: `v0.1.0-alpha.1`
- **Python**: 3.10+
- **Repository**: https://github.com/huliye24/moodify-o3is

## 3. Completed MHP Chain

| MHP | Task | Date |
|-----|------|------|
| MHP-001 | Code audit — discovered 60+ files, dual type systems, overgrowth | 2026-05-28 |
| MHP-002 | v01 minimal mainline — 6 new v01_*.py files, E2E verified | 2026-05-28 |
| MHP-003-A | API `/process` switched to `v01_pipeline` | 2026-05-30 |
| MHP-003-B | CLI defaults `analyze`/`process` switched to v01 | 2026-05-30 |
| MHP-004-A | v01 pytest coverage — 20 new tests, markers configured | 2026-05-30 |
| MHP-004-B | README updated to runnable project manual | 2026-05-30 |
| MHP-004-C | Project snapshot created | 2026-05-30 |

## 4. v01 Mainline Files

```
moodify-core-package/src/moodify/

v01_types.py        ( 92 lines) — AudioMetrics / DiagnosisReport / ProcessResult
v01_presets.py      ( 99 lines) — 3 presets × 15 pedalboard DSP params
v01_analyzer.py     (169 lines) — FFT 6-band spectrum → AudioMetrics + PNG
v01_diagnostics.py  ( 84 lines) — rule-based DiagnosisReport
v01_exporter.py     ( 41 lines) — 16-bit WAV export + peak clamp
v01_pipeline.py     ( 98 lines) — import→analyze→diagnose→process→export

Shared infra:
audio_io.py         ( 26 lines) — universal audio loader (soundfile + librosa)
cli.py              — 15 subcommands, default analyze/process → v01
api/main.py         — /health /presets /process (→ v01_pipeline)
```

## 5. CLI Command Map

```
Default (v01 mainline):
  moodify analyze <file>              → v01_analyzer
  moodify process <file> --preset X   → v01_pipeline
  moodify presets                     → list 3 presets

Legacy (preserved):
  moodify legacy-analyze <file>       → DiagnosisEngine (18-param, 5D)
  moodify legacy-process <file> <em>  → WorkflowOrchestrator (6-phase)
  moodify emotions / crafts           → old knowledge system

Infra:
  moodify serve                       → uvicorn API server

Experimental:
  moodify evaluate-run / evaluate-single / evaluate-status
```

## 6. API Endpoints

| Endpoint | Method | Handler | Status |
|----------|--------|---------|--------|
| `/health` | GET | inline | version=0.1.0, mode=v01 |
| `/presets` | GET | inline | 3 presets listed |
| `/process` | POST | `v01_pipeline.process_audio()` | preset + emotion compat |

Removed from registration (files preserved):
- `/sessions` — depends on `memory.db`
- `/calibration` — depends on `calibration.online`

## 7. Test Status

```
pytest -m v01   → 20 passed, 84 deselected
pytest (full)   → 104 passed

Breakdown:
  v01_types         3 tests
  v01_presets       4 tests
  v01_analyzer      1 test
  v01_diagnostics   4 tests
  v01_exporter      1 test
  v01_pipeline      7 tests
  legacy + exp     84 tests
  ─────────────────────────
  TOTAL           104 tests, all green
```

Markers in `pyproject.toml`:
- `v01` — v0.1.0 mainline
- `legacy` — old system kept for compatibility
- `experimental` — future/research modules

## 8. Architecture Decisions (DO NOT OVERTURN)

1. **Layer freeze, not mass deletion** — legacy system fully preserved, not called by v0.1.0
2. **Bypass strategy** — v01_* is a clean new path, no dependency on old `data_types.py`
3. **API dual-parameter** — accepts `preset` (canonical) and `emotion` (legacy compat)
4. **CLI defaults to v01** — `moodify analyze`/`process` use v01, old system via `legacy-*`
5. **Three-tier test markers** — v01 / legacy / experimental; `pytest` still runs full suite

## 9. Immutable Rules

- Do NOT delete legacy system (diagnosis / orchestration / knowledge / physics / calibration / llm / optimizer / safety / memory)
- Do NOT reconnect `WorkflowOrchestrator` to v0.1.0 `/process`
- Do NOT change v01 API contract (3 presets, not 8 emotions)
- Do NOT merge `baseline/` into pytest
- Do NOT build a GUI in v0.1.0 phase
- Do NOT add new presets without quality calibration first

## 10. Known Issues

1. **baseline broken import** (`tests/baseline/run_baseline.py:53`):
   ```python
   from moodify.llm.offline_fallback import offline_fallback
   ```
   Module does not exist. baseline/ is excluded from pytest collection. No impact on CI.
   Scheduled for MHP-006.

2. **CLI/API smoke tests not in pytest**: v01 pipeline has pytest coverage, but CLI and API
   entry points were verified manually. Could be added in a future MHP.

3. **matplotlib tight_layout warning**: `v01_analyzer.py:166` emits `UserWarning` on
   tight_layout. Does not affect output. Low priority.

## 11. Next Steps

```
MHP-005   Preset quality calibration & DSP parameter tuning
          (NOT adding new presets — verify the 3 existing ones first)

MHP-006   baseline/ tool cleanup
          (fix broken import, decide whether to keep or archive)
```

Later (not v0.1.0):
```
Real audio regression tests
GUI (desktop or web)
Cloud deployment iteration
```
