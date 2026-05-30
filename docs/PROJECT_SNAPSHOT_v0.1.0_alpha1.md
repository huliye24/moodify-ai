# Moodify v0.1.0-alpha.1 — Project Snapshot

> Generated: 2026-05-30
> Tag: `v0.1.0-alpha.1`
> Status: v0.1.0 mainline verified, all tests green

---

## What This Is

Moodify is an AI music post-processing engine. It takes raw AI-generated
audio and applies spectral analysis, audio diagnosis, and DSP preset
processing to produce a more polished result.

v0.1.0-alpha.1 is the first prototype with both CLI and API entry points
verified end-to-end.

---

## What Works (Verified)

| Capability | CLI | API |
|------------|-----|-----|
| Spectrum analysis → PNG | `moodify analyze` | — |
| Process with preset → WAV | `moodify process --preset X` | `POST /process` |
| Diagnosis report → JSON | included in process | included in response |
| List presets | `moodify presets` | `GET /presets` |
| Health check | — | `GET /health` |

### Three Processing Presets

| Key | Name | Character |
|-----|------|-----------|
| `warm_vocal` | Warm Vocal | Gentle vocal enhancement: warmth, presence, light compression |
| `clean_master` | Clean Master | Transparent mastering: subtle compression, clean spectrum |
| `wide_space` | Wide Space | Spatial enhancement: wide reverb, stereo width |

Each preset = 15 DSP parameters (peak EQ, low shelf, compressor, reverb,
harmonic drive, high shelf) applied via the pedalboard library.

---

## Source Code Map

### v0.1.0 Mainline (6 files, 577 lines)

| File | Lines | Purpose |
|------|-------|---------|
| `v01_types.py` | 91 | AudioMetrics, DiagnosisReport, ProcessResult |
| `v01_presets.py` | 98 | 3 presets × 15 DSP params |
| `v01_analyzer.py` | 168 | FFT spectrum → metrics + PNG |
| `v01_diagnostics.py` | 83 | Rule-based audio diagnosis |
| `v01_exporter.py` | 40 | 16-bit WAV export + peak clamp |
| `v01_pipeline.py` | 97 | Main pipeline orchestrator |

### Shared Infrastructure

| File | Purpose |
|------|---------|
| `audio_io.py` | Universal audio loader (soundfile + librosa) |
| `cli.py` | CLI entry (15 subcommands) |
| `api/main.py` | FastAPI server (3 endpoints) |

### Legacy System (preserved, not wired to v0.1.0)

| Directory | Files | Purpose |
|-----------|-------|---------|
| `diagnosis/` | 6 | 18-parameter diagnosis engine |
| `processing/` | 3 | Pedalboard DSP chain + spectral chain |
| `knowledge/` | 5 | 8-emotion craft cards + risk model |
| `orchestration/` | 2 | 6-phase workflow engine (938 lines) |

### Experimental (preserved for v1.x+)

`physics/`, `calibration/`, `evaluation/`, `llm/`, `optimizer/`, `safety/`,
`memory/`, `protocol.py`, `fingerprint.py`, `conservation.py`, `icc.py`,
`uncertainty.py`

---

## Test Suite

| Scope | Tests | Command |
|-------|-------|---------|
| v0.1.0 mainline | 20 | `pytest -m v01` |
| All (v01 + legacy + experimental) | 104 | `pytest` |

All 104 tests pass.

---

## Dependencies

```
python>=3.10
numpy, scipy, librosa, soundfile, pyloudnorm
pydantic, pedalboard
fastapi, uvicorn, python-multipart
```

No GPU required. No torch, no demucs.

---

## Known Issues

1. `v01_analyzer.py` — tight_layout UserWarning on spectrum PNG (cosmetic, PNG still renders correctly)
2. `tests/baseline/run_baseline.py` — broken import `moodify.llm.offline_fallback` (baseline is not in pytest, tracked as MHP-006)

---

## Architecture Decisions

1. **Bypass, not delete** — legacy system fully preserved but not called by v0.1.0 mainline
2. **v01_* is the clean path** — does not depend on old `data_types.py` ParameterWithUncertainty
3. **API backward-compatible** — accepts both `preset` (canonical) and `emotion` (legacy)
4. **CLI defaults to v01** — `moodify analyze` and `moodify process` go to v0.1.0; legacy via `legacy-*` subcommands
5. **Three-tier test markers** — `v01`, `legacy`, `experimental`

---

## Next Steps (Planned)

- MHP-004-B: README rewritten as quickstart (~120 lines) — **DONE**
- MHP-004-C: This snapshot document — **DONE**
- MHP-005: DSP parameter tuning on existing 3 presets
- MHP-006: baseline/ tool cleanup
- MHP-004-D: Real audio regression tests (deferred)

---

## Repository

https://github.com/huliye24/moodify-o3is

```bash
git clone https://github.com/huliye24/moodify-o3is.git
cd moodify-o3is/moodify-core-package
pip install -e .
moodify presets
```
