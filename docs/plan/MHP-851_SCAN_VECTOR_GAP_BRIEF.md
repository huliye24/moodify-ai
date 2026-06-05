# MHP-851: Scan Vector Gap Brief

**Status**: done
**Direction**: ECHAIN-MOODIFY-MAP-CHAIN-015 / NEM-MOODIFY-MAP-PROBE-045 / Probe Plan-6B: Vector Definitions / E1
**Depends on**: MHP-845 (Current State Audit)
**Protocol**: AWJ Stack + E-Chain 54

## Context

MHP-845 found ScanResult at 29% readiness — only 2 of 7 target MAP fields exist. The current `ScanResult` dataclass is file-level only: `exists`, `readable`, `extension`, `file_size_bytes`, `warnings`. None of the acoustic-surface fields (loudness, transient, space, texture, reality) are computed during scan.

## Gap: Current vs Target

| MAP Field | Current | Source | Gap |
|-----------|---------|--------|-----|
| `loudness_lufs` | None | `AudioMetrics` has peak_db, crest — no LUFS | Need ITU-R BS.1770 loudness |
| `transient_ratio` | None | Not computed | Need peak-to-RMS ratio or attack envelope |
| `stereo_width` | None | `AudioMetrics.correlation_lr` exists in Analyze | Move to Scan or duplicate |
| `spectral_centroid_hz` | None | FFT computed but not stored | Add to analyzer output |
| `dc_offset` | None | Not computed | Trivial — numpy mean of signal |
| `clip_count` | None | Not computed | Count samples at ±1.0 |

## Recommended ScanResult v0.2

```python
@dataclass
class ScanResult:
    # -- existing (v0.1) --
    input_path: str
    exists: bool
    extension: str
    file_size_bytes: int
    readable: bool
    warnings: list[str]

    # -- MAP v0.2 acoustic surface --
    loudness_lufs: float | None = None       # ITU-R BS.1770 integrated
    transient_ratio: float | None = None      # peak-to-moving-RMS ratio
    stereo_width: float | None = None         # side-to-mid energy ratio (0-1)
    spectral_centroid_hz: float | None = None # weighted mean frequency
    dc_offset: float | None = None            # signal mean / full-scale
    clip_count: int = 0                       # samples at ±1.0
```

## Implementation Strategy

| Field | Complexity | Implementation |
|-------|-----------|---------------|
| `loudness_lufs` | Medium | Use `pyloudnorm` or simple RMS→LUFS mapping. Architect must approve formula. |
| `transient_ratio` | Low | `max(|signal|) / moving_rms_mean` — already have peak and crest |
| `stereo_width` | Low | `sqrt(1 - correlation_lr^2)` or side/mid ratio from existing FFT |
| `spectral_centroid_hz` | Low | Already have FFT in `_compute_band_rms()` — just store centroid |
| `dc_offset` | Trivial | `float(np.mean(signal))` |
| `clip_count` | Trivial | `int(np.sum(np.abs(signal) >= 0.999))` |

All six fields can be computed in a single audio pass. No new external dependencies required.

## Decision

**Build NEM scope**. These fields are low-risk Worker tasks (MHP-863/864). Probe scope is to define the gap — no implementation.

## Acceptance Criteria

- [x] Each missing field has a source mapping.
- [x] Each field has an estimated implementation complexity.
- [x] Build NEM task boundary is clear: Worker implements in `scan_audio()`.
