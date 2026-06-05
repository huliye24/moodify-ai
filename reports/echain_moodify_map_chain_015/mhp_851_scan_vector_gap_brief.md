# MHP-851: Scan Vector Gap Brief — Completion Report

**Generated**: 2026-06-05
**Status**: done
**E-Chain**: ECHAIN-MOODIFY-MAP-CHAIN-015 / NEM-MOODIFY-MAP-PROBE-045 / Probe Plan-6B

## Key Finding

Current `ScanResult` (v01_types.py:62-80) has 6 fields — all file-level. Zero acoustic-surface fields. MAP requires 6 additional fields: `loudness_lufs`, `transient_ratio`, `stereo_width`, `spectral_centroid_hz`, `dc_offset`, `clip_count`.

## Evidence: Current ScanResult

```python
# v01_types.py:62-80
@dataclass
class ScanResult:
    input_path: str = ""
    exists: bool = False
    extension: str = ""
    file_size_bytes: int = 0
    readable: bool = False
    warnings: list[str] = field(default_factory=list)
```

## Gap Analysis

| Field | Computation | Complexity | Deps |
|-------|------------|-----------|------|
| loudness_lufs | RMS→LUFS mapping | Medium | numpy |
| transient_ratio | max_abs / moving_rms_mean | Low | numpy |
| stereo_width | sqrt(1 - corr^2) or side/mid ratio | Low | numpy |
| spectral_centroid_hz | sum(freq * magnitude) / sum(magnitude) | Low | FFT already computed |
| dc_offset | float(np.mean(signal)) | Trivial | numpy |
| clip_count | int(np.sum(np.abs(signal) >= 0.999)) | Trivial | numpy |

## Implementation

All 6 fields computable in single audio pass. No new pip packages needed. Build NEM MHP-864 (Implement Scan Result Contract).

## Decision: Build NEM Scope

Worker implements in `scan_audio()` (v01_pipeline.py:176-196). Architect approves field additions to `ScanResult` dataclass.
