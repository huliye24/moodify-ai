# Fix Log — NEM-MOODIFY-MRS-002 / Harden-6

| # | Issue | Severity | Root Cause | Fix | Verified |
|---|-------|----------|------------|-----|----------|
| 1 | over_dark 100% severe | P0 | Time-domain moving average measured total energy, not per-band energy | Rewrote `_band_energy_fft()` using numpy FFT + Hann window; added `MIN_BAND_ENERGY` floor to skip silent bands | ✅ 145/145 tests, real piano: level=none |
| 2 | pseudo_mrs all negative | P0 | Reference values (rms=0.12, crest=8.0) mismatched real audio distribution | Recalibrated from 61-sample dataset: rms_target=0.15, crest_target=5.0, peak_target=0.78 | ✅ Backward compatible, scores now data-driven |
| 3 | No unified MRS entry point | P1 | MRS scoring spread across metrics.py, over_dark.py, operator_console.py | Created `mrs_engine.py:score_audio()` as single entry point | ✅ All callers updated |
