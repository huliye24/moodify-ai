# 00_IMPLEMENTATION_AUDIT.md — DSK-MFY-STUDIO-PREP-004

**Generated:** 2026-07-31T17:10:00Z (approx)
**Worker:** DeepSeek (Claude A role)
**Branch:** `codex/mainline-cloud-dev-20260603`
**HEAD:** `df3a8a3` — docs(dsk-aux-002): normalize final acceptance evidence

## 1. Environment Fact Record

| Item | Value |
|---|---|
| Python | 3.11.9 (C:\Program Files\Python311\python.exe) |
| numpy | 2.4.4 |
| scipy | 1.17.1 |
| soundfile | 0.13.1 |
| pydantic | 2.13.2 |
| pyarrow | NOT INSTALLED |
| pyloudnorm | installed (no `__version__`) |
| moodify core | 0.1.0 (editable install) |
| moodify-bridge | NOT INSTALLED (requires Python 3.12) |

**Working tree status:** Many modified tracked files (all user assets, NOT to be touched). Target directories `tools/studio_session_prep/` and `tests/studio_session_prep/` do not exist yet and will be created.

## 2. Available vs Unavailable Capabilities

### 2.1 Real Metrics (available via numpy/scipy/pyloudnorm or moodify core)

| Metric | Source | Implementation Approach |
|---|---|---|
| Peak (linear) | Direct numpy | `np.max(np.abs(x))` |
| RMS (linear) | Direct numpy | `np.sqrt(np.mean(x**2))` |
| Crest factor | Derived | peak / rms |
| Spectral entropy | numpy FFT | Same formula as bridge `spectral_metrics` |
| Spectral centroid (Hz) | numpy FFT | Same formula as bridge |
| Spectral flux | numpy FFT | Same formula as bridge |
| Band fractions | numpy FFT | Configurable bands, same as bridge |
| L/R correlation | numpy | `np.corrcoef(L, R)[0,1]` |
| Waveform correlation | numpy | `np.corrcoef(a, b)[0,1]` |
| Fitted scalar gain | numpy | `dot(a,b) / dot(a,a)` |
| Relative residual | numpy | `norm(b - gain*a) / norm(b)` |
| Difference SNR (dB) | numpy | `10*log10(signal_power / noise_power)` |
| Integrated LUFS | pyloudnorm | `pyln.Meter(sr).integrated_loudness(x)` |

### 2.2 Explicitly NULL Metrics (with warnings)

| Metric | Reason |
|---|---|
| LRA (Loudness Range) | pyloudnorm does not provide LRA; bridge also marks it null |
| True peak (dBTP) | No BS.1770 true peak meter; bridge also marks it null |
| Phase rotation (degrees) | No phase analysis backend |
| Frequency-dependent masking | Experimental; no validated model |
| Section-level evolution (MSE-aligned) | Planned in WSE architecture; needs MSE section IDs |

### 2.3 Not Available (constraints)

| Item | Impact |
|---|---|
| pyarrow / Parquet | Cannot write Parquet; will use JSON + CSV instead |
| moodify-bridge imports | Cannot reuse bridge Python code directly (3.12 vs 3.11); will implement same formulas |
| moodify-bridge DuckDB | No case ledger; will use JSON manifest files |

## 3. Design: Tool Data Flow and Write Boundaries

```
Session Init (YAML brief)
    │
    ▼
session_dir/
  ├── manifest.json          ← SessionBrief + AssetEntry list
  ├── RECORDING_DAY_CHECKLIST.md
  └── delivery_contract.json

Asset Verify (read-only)
    │
    ▼
Updates manifest with SHA-256, size, codec info per asset

WSE Analyze (read-only on source audio)
    │
    ▼
--output-dir/
  ├── wse_profile.json       ← Versioned WseProfile
  ├── wse_evolution.csv      ← Per-window time series
  └── wse_warnings.json      ← null metrics with reasons

Candidate Plan (reads WSE profile)
    │
    ▼
--output-dir/
  ├── candidate_plans.json   ← 2-3 CandidatePlan objects
  └── plan_warnings.json

Candidate Generate (reads plan + source, calls v01_pipeline)
    │
    ▼
--output-dir/
  ├── candidate_<id>/
  │     ├── output.wav
  │     ├── report.json
  │     └── run_info.json    ← params, exit code, timing, hashes
  └── ...

Candidate Compare (reads candidates)
    │
    ▼
--output-dir/
  ├── comparison.json
  └── human_review.md        ← human_review = PENDING

Report Build
    │
    ▼
--output-dir/
  ├── report.md
  └── report.html
```

**Write boundary rule:** All tool output goes into explicit `--output-dir`. Source files are read-only. Existing output directories with content are rejected by default.

## 4. Tomorrow Commercial Risks

| # | Risk | Mitigation |
|---|---|---|
| 1 | Digital clipping on input | Pre-scan peak before recording; set safe headroom (-6 dBFS target) |
| 2 | Sample rate mismatch (44.1k vs 48k vs 96k) | Explicit spec in RecordingSpec; verify before first take |
| 3 | File naming inconsistency | Enforce naming template in SessionBrief; validate on asset-verify |
| 4 | Single backup point of failure | Dual backup to different physical paths; verify both before leaving |
| 5 | Take loss (overwrite, corruption) | Sequential take numbering; sha256 after each take; no overwrite |
| 6 | Loudness bias in A/B listening | Always loudness-match before human review; flag RMS deltas > 0.5 dB |
| 7 | Phase issues (mono fold-down) | L/R correlation check; warn if < 0.3; note mono compatibility risk |
| 8 | Client scope creep | Freeze DeliverableContract before recording starts; changes = new contract |
| 9 | Missing metadata (BPM, key, genre) | Record in SessionBrief at session-init; flag missing fields at asset-verify |
| 10 | Tool failure mid-session | Runbook includes fallback: manual checklist + offline sha256 + note-taking |

## 5. Implementation Design (per batch)

### Batch A: Models + Session Init + Asset Verify
- **models.py**: Pydantic v2 models — SessionBrief, RecordingSpec, DeliverableContract, AssetEntry
- **studio_prep.py**: CLI entry with subparsers for all 6 commands
- `session-init`: Read YAML brief, create session dir, write manifest.json, checklist.md
- `asset-verify`: Read-only SHA-256 + soundfile info probe; update manifest
- Templates: YAML example files in templates/

### Batch B: WSE Analysis + Candidate Plans
- **wse_profile.py**: Call metric functions; produce WseProfile with version, warnings, null tracking
- Section/window evolution: Fixed frame/hop sliding window, output CSV
- **candidate_plan.py**: Threshold-based rules generating 2-3 plans (conservative, balanced, exploratory)
- Each plan: evidence list, risk list, allowed parameter ranges, human checkpoints
- Synthetic tests: silence, unit sine, stereo in-phase, stereo out-of-phase, gain, frequency combos, short audio

### Batch C: Candidate Generation + Comparison + Reports
- **adapter**: Thin wrapper around `moodify.v01_pipeline.process_audio()`
- Dry-run default; `--execute-candidates` flag required for actual processing
- Each candidate in isolated directory with run_info.json (params, exit code, timing, hashes)
- **candidate_compare**: Reuse comparison metrics; require same SR; output tech diff + human review placeholder
- **reporting.py**: Markdown + HTML report generation

### Batch D: Full Validation + Runbook + Handoff
- Run all new tests
- Run existing bridge/core smoke (read-only, no modifications)
- CLI smoke on all 6 commands
- Generate synthetic demo output
- git diff audit (only allowed dirs)
- Write TOMORROW_STUDIO_RUNBOOK.md, VALIDATION_REPORT.md, HANDOFF.md

## 6. Import/Dependency Verification

All planned imports are verified available:
- `numpy` (2.4.4) — all metric computation
- `scipy` (1.17.1) — optional, for signal processing
- `soundfile` (0.13.1) — audio file I/O
- `pydantic` (2.13.2) — data models
- `pyloudnorm` — integrated LUFS measurement
- `moodify.audio_io` — audio loading
- `moodify.v01_pipeline` — candidate generation
- `moodify.v01_presets` — preset list for candidate plans
- `hashlib` (stdlib) — SHA-256
- `pathlib` (stdlib) — path operations
- `json`, `csv`, `argparse`, `datetime` (stdlib)

**No new dependencies required. No network access needed.**

## 7. Batch Gate Decision

- [x] All import/dependency paths verified
- [x] No requirement to modify core DSP
- [x] Output boundaries clearly defined (explicit --output-dir)
- [x] All null metrics identified with warnings
- [x] Scientific boundaries documented
- [x] Source file read-only guarantee designed

**Gate: PASS** — proceed to Batch A.
