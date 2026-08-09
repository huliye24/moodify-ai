"""Window measurements and P0 event detectors (MFY-PHASE1-DEPTH-002).

One pass per analysis domain produces windowed measurements; detectors
consume those shared measurements (no repeated full-track transforms).
Every detector is a deterministic versioned rule over the profile
thresholds and never claims musical meaning.
"""

from __future__ import annotations

import numpy as np

from moodify.auditory.events.models import EventCandidate, WindowMeasurement
from moodify.auditory.events.temporal_profile import TemporalProfile

_DOMAIN_KEYS = {
    "integrity": ("clipping_ratio", "near_clipping_ratio", "rms_db", "peak_db", "silent"),
    "level": ("rms_db", "peak_db"),
    "spectrum": ("hf_ratio", "hf_cutoff_estimate"),
    "stereo": ("correlation", "phase_risk"),
}


def compute_domain_measurements(
    samples: np.ndarray, sr: int, domain: str, profile: TemporalProfile
) -> list[WindowMeasurement]:
    """Windowed measurements for one analysis domain (deterministic)."""
    cfg = profile.domains[domain]
    win = int(cfg.window_ms * sr / 1000)
    hop = int(cfg.hop_ms * sr / 1000)
    if samples.ndim == 1:
        samples = samples[:, None]
    mono = samples.mean(axis=1)
    n = len(mono)
    n_windows = max(0, (n - win) // hop + 1)

    rows: list[WindowMeasurement] = []
    for idx in range(n_windows):
        start = idx * hop
        seg = mono[start: start + win]
        start_ms = int(start * 1000 / sr)
        end_ms = int((start + len(seg)) * 1000 / sr)
        values = _domain_values(domain, seg, samples[start: start + win], sr, win)
        rows.append(WindowMeasurement(
            domain=domain, window_index=idx, start_ms=start_ms, end_ms=end_ms, values=values,
        ))
    return rows


def _domain_values(domain: str, mono: np.ndarray, stereo_block: np.ndarray,
                   sr: int, win: int) -> dict[str, float]:
    if domain == "integrity":
        absx = np.abs(mono)
        return {
            "clipping_ratio": float(np.mean(absx >= 0.999)),
            "near_clipping_ratio": float(np.mean((absx >= 0.95) & (absx < 0.999))),
            "rms_db": float(20 * np.log10(np.sqrt(np.mean(mono ** 2)) + 1e-12)),
            "peak_db": float(20 * np.log10(np.max(absx) + 1e-12)),
            "silent": float(np.sqrt(np.mean(mono ** 2)) < 10 ** (-60 / 20)),
        }
    if domain == "level":
        return {
            "rms_db": float(20 * np.log10(np.sqrt(np.mean(mono ** 2)) + 1e-12)),
            "peak_db": float(20 * np.log10(np.max(np.abs(mono)) + 1e-12)),
        }
    if domain == "spectrum":
        spectrum = np.abs(np.fft.rfft(mono * np.hanning(len(mono))))
        freqs = np.fft.rfftfreq(len(mono), 1 / sr)
        total = np.sum(spectrum ** 2) + 1e-12
        hf_mask = freqs >= 8000
        hf_ratio = float(np.sum(spectrum[hf_mask] ** 2) / total)
        cum = np.cumsum(spectrum ** 2)
        cutoff_idx = int(np.searchsorted(cum, cum[-1] * 0.995))
        return {
            "hf_ratio": hf_ratio,
            "hf_cutoff_estimate": float(freqs[min(cutoff_idx, len(freqs) - 1)]),
            # silence exclusion for dropout semantics
            "rms_db": float(20 * np.log10(np.sqrt(np.mean(mono ** 2)) + 1e-12)),
        }
    # stereo
    left = stereo_block[:, 0]
    right = stereo_block[:, 1] if stereo_block.shape[1] > 1 else left
    if np.std(left) < 1e-9 or np.std(right) < 1e-9:
        corr = 0.0  # silence: correlation undefined, report neutral
    else:
        corr = float(np.corrcoef(left, right)[0, 1]) if len(left) > 2 else 0.0
    mid = (left + right) / 2.0
    side = (left - right) / 2.0
    mid_energy = np.mean(mid ** 2) + 1e-12
    side_energy = np.mean(side ** 2) + 1e-12
    phase_risk = float(side_energy > 4.0 * mid_energy)
    return {"correlation": corr, "phase_risk": phase_risk}


def detect_candidates(
    measurements: dict[str, list[WindowMeasurement]], profile: TemporalProfile
) -> list[EventCandidate]:
    """Run all P0 detectors over shared window measurements."""
    candidates: list[EventCandidate] = []
    t = profile.thresholds

    integrity = measurements.get("integrity", [])
    clipping = _threshold_run(integrity, "clipping_ratio", "CLIPPING_CLUSTER",
                              t["clipping_ratio_min"], int(t["clipping_min_windows"]))
    candidates.extend(clipping)
    near = _threshold_run(integrity, "near_clipping_ratio", "NEAR_CLIPPING_CLUSTER",
                          t["near_clipping_ratio_min"], int(t["near_clipping_min_windows"]))
    candidates.extend(near)
    silence = _threshold_run(integrity, "silent", "SILENCE_GAP", 0.5,
                             min_windows=int(t["silence_min_duration_ms"] / 100))
    candidates.extend(silence)

    level = measurements.get("level", [])
    candidates.extend(_level_events(level, t))

    spectrum = measurements.get("spectrum", [])
    candidates.extend(_hf_dropout(spectrum, t))

    stereo = measurements.get("stereo", [])
    candidates.extend(_stereo_events(stereo, t))

    return candidates


def _threshold_run(rows: list[WindowMeasurement], key: str, event_type: str,
                   threshold: float, min_windows: int,
                   comparison: str = "gte", domain: str = "integrity") -> list[EventCandidate]:
    candidates: list[EventCandidate] = []
    run: list[int] = []
    magnitudes: list[float] = []
    for idx, row in enumerate(rows):
        value = float(row.values.get(key, 0.0))
        active = value >= threshold if comparison == "gte" else value <= threshold
        if active:
            run.append(idx)
            magnitudes.append(value)
        else:
            if len(run) >= min_windows:
                candidates.append(_candidate(event_type, run, domain, magnitudes))
            run, magnitudes = [], []
    if len(run) >= min_windows:
        candidates.append(_candidate(event_type, run, domain, magnitudes))
    return candidates


def _level_events(rows: list[WindowMeasurement], t: dict[str, float]) -> list[EventCandidate]:
    spikes: list[EventCandidate] = []
    drops: list[EventCandidate] = []
    spike_run: list[int] = []
    drop_run: list[int] = []
    spike_mag: list[float] = []
    drop_mag: list[float] = []
    for idx, row in enumerate(rows):
        rms = row.values.get("rms_db", -120.0)
        baseline = _median_before(rows, idx, 3, "rms_db")
        if baseline <= -120.0:
            baseline = rms
        if rms - baseline >= t["level_spike_db"]:
            spike_run.append(idx)
            spike_mag.append(rms)
            if drop_run:
                if len(drop_run) >= int(t["level_drop_min_windows"]):
                    drops.append(_candidate("LEVEL_DROP", drop_run, "level", drop_mag))
                drop_run, drop_mag = [], []
        elif baseline - rms >= t["level_drop_db"]:
            drop_run.append(idx)
            drop_mag.append(rms)
            if spike_run:
                if len(spike_run) >= int(t["level_spike_min_windows"]):
                    spikes.append(_candidate("LEVEL_SPIKE", spike_run, "level", spike_mag))
                spike_run, spike_mag = [], []
        else:
            if spike_run and len(spike_run) >= int(t["level_spike_min_windows"]):
                spikes.append(_candidate("LEVEL_SPIKE", spike_run, "level", spike_mag))
            if drop_run and len(drop_run) >= int(t["level_drop_min_windows"]):
                drops.append(_candidate("LEVEL_DROP", drop_run, "level", drop_mag))
            spike_run, drop_run, spike_mag, drop_mag = [], [], [], []
    if spike_run and len(spike_run) >= int(t["level_spike_min_windows"]):
        spikes.append(_candidate("LEVEL_SPIKE", spike_run, "level", spike_mag))
    if drop_run and len(drop_run) >= int(t["level_drop_min_windows"]):
        drops.append(_candidate("LEVEL_DROP", drop_run, "level", drop_mag))
    return spikes + drops


def _hf_dropout(rows: list[WindowMeasurement], t: dict[str, float]) -> list[EventCandidate]:
    """HF energy falls >= threshold relative to the local baseline median."""
    min_windows = int(t["hf_dropout_min_windows"])
    candidates: list[EventCandidate] = []
    run: list[int] = []
    magnitudes: list[float] = []
    for idx, row in enumerate(rows):
        baseline = _median_before(rows, idx, 4, "hf_ratio")
        ratio = row.values.get("hf_ratio", 0.0)
        # Silence is a separate event; dropout applies to non-silent content.
        non_silent = row.values.get("rms_db", -120.0) > -60.0
        dropped = non_silent and baseline > 0 and ratio <= baseline * t["hf_dropout_ratio_threshold"]
        if dropped:
            run.append(idx)
            magnitudes.append(ratio)
        else:
            if len(run) >= min_windows:
                candidates.append(_candidate("HIGH_FREQUENCY_DROPOUT", run, "spectrum", magnitudes))
            run, magnitudes = [], []
    if len(run) >= min_windows:
        candidates.append(_candidate("HIGH_FREQUENCY_DROPOUT", run, "spectrum", magnitudes))
    return candidates


def _stereo_events(rows: list[WindowMeasurement], t: dict[str, float]) -> list[EventCandidate]:
    neg = _threshold_run(rows, "correlation", "NEGATIVE_CORRELATION_REGION",
                         -abs(t["negative_correlation_max"]),  # correlation <= -0.5
                         int(t["negative_corr_min_windows"]),
                         comparison="lte", domain="stereo")
    risk = _threshold_run(rows, "phase_risk", "PHASE_RISK_REGION", 0.5,
                          int(t["phase_risk_min_windows"]), domain="stereo")
    return neg + risk


def _median_before(rows: list[WindowMeasurement], idx: int, lookback: int, key: str) -> float:
    values = [rows[j].values.get(key, 0.0) for j in range(max(0, idx - lookback), idx)]
    return float(np.median(values)) if values else 0.0


def _candidate(event_type: str, window_indices: list[int], domain: str,
               magnitudes: list[float]) -> EventCandidate:
    return EventCandidate(
        event_type=event_type,
        window_indices=tuple(window_indices),
        domain=domain,
        peak_magnitude=float(max(magnitudes)) if magnitudes else 0.0,
    )
