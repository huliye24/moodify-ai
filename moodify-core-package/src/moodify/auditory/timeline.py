"""Timeline window measurements (DSK-MFY-AUDITORY-SCAN-001).

Track-level averages hide local problems; windowed JSONL exposes them.
"""

from __future__ import annotations

import json

import numpy as np


def compute_timeline(
    samples: np.ndarray,
    sr: int,
    window_seconds: float,
    hop_seconds: float,
) -> list[dict]:
    win = int(window_seconds * sr)
    hop = int(hop_seconds * sr)
    mono = samples.mean(axis=1) if samples.ndim > 1 else samples
    n_fft = 8192
    freqs = np.fft.rfftfreq(n_fft, 1 / sr)

    rows: list[dict] = []
    idx = 0
    window_index = 0
    while idx < len(mono):
        seg = mono[idx: idx + win]
        if len(seg) < int(0.25 * sr):
            break  # trailing tail shorter than a quarter window is dropped
        rms_db = float(20 * np.log10(np.sqrt(np.mean(seg ** 2)) + 1e-12))
        peak_db = float(20 * np.log10(np.max(np.abs(seg)) + 1e-12))
        n_fft_used = min(n_fft, len(seg))
        if n_fft_used < 256:
            idx += hop
            window_index += 1
            continue
        # window (1 s) may exceed n_fft (8192); average sub-frames for the window spectrum
        sub_hop = n_fft // 2
        frames = []
        for j in range(0, len(seg) - n_fft + 1, sub_hop):
            frames.append(np.abs(np.fft.rfft(seg[j:j + n_fft] * np.hanning(n_fft))))
        if not frames:
            frames = [np.abs(np.fft.rfft(seg[:n_fft] * np.hanning(n_fft)))]
        spec = np.mean(frames, axis=0)
        power = spec ** 2
        if power.sum() > 1e-12:
            centroid = float(np.sum(freqs * power) / power.sum())
        else:
            centroid = 0.0
        # flux needs the previous frame; approximated as local std of spectrum
        flux = float(np.std(spec))
        lo = power[(freqs >= 20) & (freqs < 250)].sum()
        mid = power[(freqs >= 250) & (freqs < 2000)].sum()
        hi = power[(freqs >= 2000) & (freqs < 16000)].sum()
        total = lo + mid + hi + 1e-12

        row = {
            "window_index": window_index,
            "start_seconds": round(idx / sr, 3),
            "end_seconds": round((idx + len(seg)) / sr, 3),
            "rms_dbfs": round(rms_db, 2),
            "sample_peak_dbfs": round(peak_db, 2),
            "spectral_centroid_hz": round(centroid, 1),
            "spectral_flux": round(flux, 4),
            "low_band_ratio": round(lo / total, 6),
            "mid_band_ratio": round(mid / total, 6),
            "high_band_ratio": round(hi / total, 6),
            "silence_flag": bool(rms_db < -60.0),
            "clipping_flag": bool(np.any(np.abs(seg) >= 0.999)),
        }
        if samples.ndim > 1 and samples.shape[1] >= 2:
            lch = samples[idx: idx + win, 0]
            rch = samples[idx: idx + win, 1]
            if np.std(lch) > 0 and np.std(rch) > 0:
                row["stereo_correlation"] = round(float(np.corrcoef(lch, rch)[0, 1]), 4)
            else:
                row["stereo_correlation"] = None
        rows.append(row)
        idx += hop
        window_index += 1
    return rows


def write_timeline_jsonl(rows: list[dict], path) -> None:
    with open(path, "w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")
