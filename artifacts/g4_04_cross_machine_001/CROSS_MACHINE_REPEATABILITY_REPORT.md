# MFY-G4-04-CROSS-MACHINE-001 — Cross-Machine Repeatability Report

**Date:** 2026-08-11
**Protocol reference:** MOODIFY_AUGUST_2026_FREEZE_PROTOCOL Gate 4 — Cross-machine repeatability

## Setup

| | Local dev machine | Aliyun data node |
|---|---|---|
| OS | Windows 10 Enterprise | Ubuntu 26.04 (kernel 7.0) |
| Python | 3.11 (CPython) | 3.14 (CPython) |
| Scan profile | MFY-WSE-SCAN-PROFILE-001 | MFY-WSE-SCAN-PROFILE-001 |
| Profile hash | f0ff177ddc7b05d3a934848b9fd55d79a453b908707231360e772850afde45f1 | same |

**Source:** `10_viens_chez_moi.wav` (pilot-10), sha256 `c3886611711d6e657e2180eec16ca6b54e0c3e9afcf908c3dff0d83010c16c63`, 188.52 s, 48 kHz stereo.
The node copy was downloaded to the local machine and its hash verified byte-identical before scanning.

## Result

- **52 metrics compared, 52 identical (abs diff = 0.0)**
- Exact-match metrics (sample_rate, channels, duration, clipping_sample_count, invalid_sample_count, finite_sample_ratio): all equal.
- Continuous metrics (LUFS, spectral, band-energy, stereo descriptors): identical to full displayed precision, e.g. integrated_lufs = -18.26 both, air_10000_16000_hz = 0.00557336 both, spectral_flux = 1307.25 both.
- Largest abs diff across all metrics: 0.0.

## Tolerances

No tolerance slack is needed for the before-scan path as of 2026-08-11:

- **Exact-match metrics:** tolerance 0 (must be identical; a nonzero diff is a regression).
- **Continuous metrics:** observed 0 diff; define tolerance as `<= 0.01` relative OR `<= 1e-6` absolute as a guard against future bit-rot, whichever is larger, to absorb non-deterministic library changes without breaking production.

## Interpretation

The before-scan measurement chain (decode → STFT → BS1770 loudness → band energy → descriptors) is deterministic across OS and Python versions at full displayed precision. This supports Gate 2's cross-check requirement: metrics produced on the node are directly comparable to local metrics without normalization.

## Artifacts

- `local_scan/metrics.json` — local scan (reproduce: `scan_audio` with MFY-WSE-SCAN-PROFILE-001)
- `node_metrics.json` — node scan from case_8d6f040454f147f09edbcc3a60994bc9/01_source_scan
- `10_viens_chez_moi.wav` — byte-identical source (sha256 c3886611...)
- `compare_g4_04.py` — comparison script (reproducible)
