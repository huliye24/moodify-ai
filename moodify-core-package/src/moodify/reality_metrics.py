"""Moodify Reality Score computation module.

MRS = 100 * exp(-D_R): distance-to-real metric.
Lower D_R means closer to real audio distribution.
"""
from __future__ import annotations

import math
from typing import Optional

import numpy as np
import soundfile as sf

from moodify.bands import DEFAULT_EDGES as BANDS
from moodify.mrs_robust import select_reference_stats


def load_audio(path: str, always_2d: bool = True) -> tuple[np.ndarray, int]:
    """Load audio file, return (numpy_array, sample_rate)."""
    audio, sr = sf.read(path, always_2d=True)
    return audio.astype(np.float32), sr

EPS = 1e-12

# Default component weights (sum to 1.0)
DEFAULT_WEIGHTS = {
    "spectrum": 0.20,
    "dynamic": 0.15,
    "transient": 0.10,
    "space": 0.15,
    "texture": 0.20,
    "temporal": 0.15,
    "artifact": 0.05,
}


# ── Audio loading helpers ──────────────────────────────────

def _load_mono_stereo(path: str) -> tuple[np.ndarray, np.ndarray, int]:
    """Return (mono, stereo_or_mono, sr)."""
    audio, sr = load_audio(path, always_2d=True)
    if audio.ndim == 1:
        audio = audio.reshape(-1, 1)
    if audio.shape[1] >= 2:
        stereo = audio[:, :2].T
    else:
        stereo = np.array([audio[:, 0], audio[:, 0]])
    mono = np.mean(stereo, axis=0).astype(np.float32)
    return mono, stereo, sr


def _amp_to_db(x: np.ndarray) -> np.ndarray:
    return 20.0 * np.log10(np.maximum(np.abs(x), EPS))


# ── Spectrum features ──────────────────────────────────────

def _spectrum_features(mono: np.ndarray, sr: int) -> dict:
    n = len(mono)
    fft = np.abs(np.fft.rfft(mono * np.hanning(n)))
    freqs = np.fft.rfftfreq(n, 1.0 / sr)
    total = np.sum(fft ** 2) + EPS

    bands = {}
    for name, f1, f2 in BANDS:
        mask = (freqs >= f1) & (freqs <= f2)
        bands[name] = np.sum(fft[mask] ** 2) / total

    centroid = np.sum(freqs * fft) / (np.sum(fft) + EPS)
    cumsum = np.cumsum(fft)
    rolloff_idx = np.searchsorted(cumsum, 0.95 * cumsum[-1])
    rolloff = freqs[min(rolloff_idx, len(freqs) - 1)]

    flatness_num = np.exp(np.mean(np.log(fft + EPS)))
    flatness_den = np.mean(fft) + EPS
    spectral_flatness = float(flatness_num / flatness_den)

    return {
        "centroid_norm": float(centroid / (sr / 2)),
        "rolloff_norm": float(rolloff / (sr / 2)),
        "flatness": float(np.clip(spectral_flatness, 0, 1)),
        "band_sub": float(bands["sub"]),
        "band_bass": float(bands["bass"]),
        "band_low_mid": float(bands["low_mid"]),
        "band_mid": float(bands["mid"]),
        "band_presence": float(bands["presence"]),
        "band_brilliance": float(bands.get("brilliance", 0.0)),
        "band_air": float(bands["air"]),
    }


# ── Dynamic features ───────────────────────────────────────

def _dynamic_features(mono: np.ndarray, sr: int) -> dict:
    rms_total = float(np.sqrt(np.mean(mono ** 2)))
    peak = float(np.max(np.abs(mono)))
    crest = peak / (rms_total + EPS)

    win_len = int(0.1 * sr)
    hop = win_len // 2
    rms_windows = []
    if len(mono) >= win_len:
        for i in range(0, len(mono) - win_len, hop):
            w = mono[i:i + win_len]
            rms_windows.append(float(np.sqrt(np.mean(w ** 2))))

    if len(rms_windows) >= 3:
        rms_arr = np.array(rms_windows)
        dyn_range = float(np.percentile(rms_arr, 95) - np.percentile(rms_arr, 5))
        rms_std = float(np.std(rms_arr))
    else:
        dyn_range = 0.0
        rms_std = 0.0

    return {
        "rms": rms_total,
        "peak": peak,
        "crest_factor": float(crest),
        "dynamic_range": dyn_range,
        "short_time_rms_std": rms_std,
    }


# ── Transient features ─────────────────────────────────────

def _transient_features(mono: np.ndarray, sr: int) -> dict:
    hop = max(1, int(0.01 * sr))
    n_frames = max(1, (len(mono) - hop) // hop)

    if n_frames < 2:
        return {"spectral_flux_mean": 0.0, "spectral_flux_std": 0.0,
                "short_time_energy_change": 0.0}

    fluxes = []
    energies = []
    for i in range(n_frames):
        frame = mono[i * hop:i * hop + hop]
        fft = np.abs(np.fft.rfft(frame))
        if i > 0:
            prev_fft = np.abs(np.fft.rfft(mono[(i - 1) * hop:(i - 1) * hop + hop]))
            min_len = min(len(fft), len(prev_fft))
            flux = float(np.sum(np.abs(fft[:min_len] - prev_fft[:min_len])) / (np.sum(prev_fft[:min_len]) + EPS))
            fluxes.append(flux)
        energies.append(float(np.mean(frame ** 2)))

    return {
        "spectral_flux_mean": float(np.mean(fluxes)) if fluxes else 0.0,
        "spectral_flux_std": float(np.std(fluxes)) if fluxes else 0.0,
        "short_time_energy_change": float(np.std(energies) / (np.mean(energies) + EPS)),
    }


# ── Space features ─────────────────────────────────────────

def _space_features(stereo: np.ndarray) -> dict:
    left, right = stereo[0], stereo[1]
    std_l, std_r = np.std(left), np.std(right)
    if std_l < EPS or std_r < EPS:
        return {"lr_correlation": 1.0, "mid_side_ratio": 0.0,
                "stereo_width": 0.0, "phase_anomaly": 0.0}

    corr = float(np.corrcoef(left, right)[0, 1])
    mid = (left + right) / 2
    side = (left - right) / 2
    ms_ratio = float(np.mean(side ** 2) / (np.mean(mid ** 2) + EPS))
    width = float(np.std(side) / (np.std(mid) + EPS))

    # Phase anomaly: excessive anti-correlation
    phase_anomaly = float(max(0.0, -corr))

    return {
        "lr_correlation": float(np.clip(corr, -1, 1)),
        "mid_side_ratio": float(np.clip(ms_ratio, 0, 10)),
        "stereo_width": float(np.clip(width, 0, 10)),
        "phase_anomaly": phase_anomaly,
    }


# ── Texture features ───────────────────────────────────────

def _texture_features(mono: np.ndarray, sr: int) -> dict:
    n = len(mono)
    fft = np.abs(np.fft.rfft(mono * np.hanning(n)))

    # Spectral roughness proxy: vectorized local variance of spectrum.
    if len(fft) > 10:
        kernel5 = np.ones(5, dtype=np.float64) / 5.0
        local_mean = np.convolve(fft, kernel5, mode="valid")
        local_sq_mean = np.convolve(fft ** 2, kernel5, mode="valid")
        local_var = np.maximum(local_sq_mean - local_mean ** 2, 0.0)
        roughness = float(np.mean(local_var) / (np.mean(fft ** 2) + EPS))
    else:
        roughness = 0.0

    # High frequency smoothness: energy rolloff in highest octave.
    freqs = np.fft.rfftfreq(n, 1.0 / sr)
    hf_mask = freqs > sr / 4
    if np.sum(hf_mask) > 10:
        hf_energy = fft[hf_mask]
        hf_smoothness = 1.0 - float(np.std(hf_energy) / (np.mean(hf_energy) + EPS))
        hf_smoothness = max(0.0, min(1.0, hf_smoothness))
    else:
        hf_smoothness = 0.5

    # Spectral spike score: vectorized count of narrow peaks in spectrum.
    if len(fft) > 20:
        kernel11 = np.ones(11, dtype=np.float64) / 11.0
        local_env = np.convolve(fft, kernel11, mode="valid")
        center = fft[5:-5]
        spike_count = int(np.count_nonzero((local_env > EPS) & (center > 3.0 * local_env)))
        spike_score = float(spike_count / max(1, len(fft)))
    else:
        spike_score = 0.0

    return {
        "roughness_proxy": float(roughness),
        "hf_smoothness": hf_smoothness,
        "spike_score": spike_score,
    }


# ── Temporal stability features ────────────────────────────

def _temporal_features(mono: np.ndarray, sr: int) -> dict:
    """Segment analysis: detect late-section degradation."""
    n = len(mono)
    if n < sr * 4:  # need at least 4 seconds
        return {"segment_mrs_variance": 0.0, "late_vs_early_delta": 0.0,
                "rms_drift": 0.0, "centroid_drift": 0.0, "space_drift": 0.0,
                "artifact_drift": 0.0}

    n_segments = 3  # early, middle, late
    seg_len = n // n_segments
    segments = []
    for i in range(n_segments):
        seg = mono[i * seg_len:(i + 1) * seg_len]
        segments.append(seg)

    seg_features = []
    for seg in segments:
        s = _spectrum_features(seg, sr)
        d = _dynamic_features(seg, sr)
        t = _transient_features(seg, sr)
        seg_features.append({**s, "rms": d["rms"], "crest": d["crest_factor"],
                             "dyn_range": d["dynamic_range"],
                             "flux": t["spectral_flux_mean"],
                             "energy_change": t["short_time_energy_change"]})

    # RMS drift across segments
    rms_vals = [f["rms"] for f in seg_features]
    rms_drift = float(np.std(rms_vals) / (np.mean(rms_vals) + EPS))

    # Centroid drift
    centroid_vals = [f["centroid_norm"] for f in seg_features]
    centroid_drift = float(np.std(centroid_vals) / (np.mean(centroid_vals) + EPS))

    # Variance of segment distances
    if len(seg_features) >= 3:
        early = np.array([seg_features[0][k] for k in ["rms", "centroid_norm", "flux"]])
        late = np.array([seg_features[-1][k] for k in ["rms", "centroid_norm", "flux"]])
        late_vs_early_delta = float(np.linalg.norm(late - early) / (np.linalg.norm(early) + EPS))
    else:
        late_vs_early_delta = 0.0

    return {
        "segment_rms_variance": rms_drift,
        "late_vs_early_delta": late_vs_early_delta,
        "rms_drift": rms_drift,
        "centroid_drift": centroid_drift,
        "space_drift": 0.0,  # requires stereo segment analysis
        "artifact_drift": 0.0,  # requires artifact segment analysis
    }


# ── Artifact detection ─────────────────────────────────────

def _artifact_features(mono: np.ndarray, sr: int) -> dict:
    """Detect processing artifacts: clipping, abnormal peaks, spikes."""
    if len(mono) == 0:
        return {"clipping_ratio": 0.0, "abnormal_peak_ratio": 0.0,
                "spectral_spike_score": 0.0, "phase_anomaly_score": 0.0}

    # Clipping: samples at ±1.0
    clip_count = np.sum(np.abs(mono) > 0.999)
    clipping_ratio = float(clip_count / len(mono))

    # Abnormal peaks: samples > 6 sigma from mean
    std_val = float(np.std(mono))
    if std_val > EPS:
        abnormal = np.sum(np.abs(mono) > 6.0 * std_val)
        abnormal_peak_ratio = float(abnormal / len(mono))
    else:
        abnormal_peak_ratio = 0.0

    # Spectral spike score from texture
    tex = _texture_features(mono, sr)
    spike_score = tex["spike_score"]

    return {
        "clipping_ratio": clipping_ratio,
        "abnormal_peak_ratio": abnormal_peak_ratio,
        "spectral_spike_score": spike_score,
        "phase_anomaly_score": 0.0,  # requires stereo
    }


# ── Full feature extraction ────────────────────────────────

def extract_reality_features(audio_path: str) -> dict:
    """Extract all reality-relevant features from an audio file."""
    mono, stereo, sr = _load_mono_stereo(audio_path)

    spec = _spectrum_features(mono, sr)
    dyn = _dynamic_features(mono, sr)
    trans = _transient_features(mono, sr)
    space = _space_features(stereo)
    tex = _texture_features(mono, sr)
    temp = _temporal_features(mono, sr)
    art = _artifact_features(mono, sr)

    return {
        "path": audio_path,
        "sample_rate": sr,
        "duration_s": len(mono) / sr,
        "spectrum": spec,
        "dynamic": dyn,
        "transient": trans,
        "space": space,
        "texture": tex,
        "temporal": temp,
        "artifact": art,
    }


# ── Reference stats ────────────────────────────────────────

def build_reference_stats(features_list: list[dict]) -> dict:
    """Build mu/sigma reference from a list of feature dicts."""
    if not features_list:
        return {"mu": {}, "sigma": {}}

    def _flatten(feats: dict) -> dict:
        out = {}
        for group in ["spectrum", "dynamic", "transient", "space", "texture", "temporal", "artifact"]:
            g = feats.get(group, {})
            for k, v in g.items():
                out[f"{group}__{k}"] = v
        return out

    flat_list = [_flatten(f) for f in features_list]
    keys = flat_list[0].keys()

    mu = {}
    sigma = {}
    for k in keys:
        vals = [f[k] for f in flat_list if k in f]
        mu[k] = float(np.mean(vals))
        sigma[k] = float(max(np.std(vals), 0.01))

    return {"mu": mu, "sigma": sigma, "n": len(flat_list), "method": "standard"}


# ── Distance computation ───────────────────────────────────

FEATURE_GROUPS = {
    "spectrum": ["centroid_norm", "rolloff_norm", "flatness",
                 "band_sub", "band_bass", "band_low_mid", "band_mid",
                 "band_presence", "band_brilliance", "band_air"],
    "dynamic": ["crest_factor", "dynamic_range", "short_time_rms_std"],
    "transient": ["spectral_flux_mean", "spectral_flux_std", "short_time_energy_change"],
    "space": ["lr_correlation", "mid_side_ratio", "stereo_width", "phase_anomaly"],
    "texture": ["roughness_proxy", "hf_smoothness", "spike_score"],
    "temporal": ["segment_rms_variance", "late_vs_early_delta",
                 "rms_drift", "centroid_drift"],
    "artifact": ["clipping_ratio", "abnormal_peak_ratio", "spectral_spike_score"],
}


def calculate_reality_distance(features: dict, ref_stats: dict) -> dict:
    """Compute component distances to reference distribution."""
    use_robust = ref_stats.get("method") == "mad"
    mu = ref_stats.get("median", {}) if use_robust else ref_stats.get("mu", {})
    sigma = ref_stats.get("mad", {}) if use_robust else ref_stats.get("sigma", {})

    components = {}
    for group, keys in FEATURE_GROUPS.items():
        group_features = features.get(group, {})
        dists = []
        for k in keys:
            val = group_features.get(k, 0.0)
            ref_mu = mu.get(f"{group}__{k}", val)
            ref_sigma = sigma.get(f"{group}__{k}", 0.01)
            d = ((val - ref_mu) / ref_sigma) ** 2
            dists.append(float(d))
        components[group] = float(np.sqrt(np.mean(dists)))

    return components


def calculate_mrs(
    audio_path: str,
    ref_stats: dict,
    weights: Optional[dict] = None,
    reference_by_genre: dict[str, dict] | None = None,
    genre: str | None = None,
) -> dict:
    """Calculate MRS for a single audio file."""
    if weights is None:
        weights = DEFAULT_WEIGHTS

    selected_ref = select_reference_stats(ref_stats, reference_by_genre, genre)
    features = extract_reality_features(audio_path)
    distances = calculate_reality_distance(features, dict(selected_ref))

    total_distance = 0.0
    for group, w in weights.items():
        total_distance += w * distances.get(group, 0.0)

    mrs = 100.0 * math.exp(-total_distance)

    return {
        "mrs": round(mrs, 2),
        "distance_total": round(total_distance, 4),
        "components": {k: round(v, 4) for k, v in distances.items()},
        "features": features,
        "reference_n": selected_ref.get("n", 0),
        "reference_genre": genre if selected_ref is not ref_stats else None,
        "reference_method": selected_ref.get("method", "standard"),
    }


def compare_mrs(before_path: str, after_path: str, ref_stats: dict,
                weights: Optional[dict] = None,
                label: str = "",
                reference_by_genre: dict[str, dict] | None = None,
                genre: str | None = None) -> dict:
    """Compare MRS of before vs after_matched audio."""
    mrs_before = calculate_mrs(
        before_path, ref_stats, weights, reference_by_genre, genre
    )
    mrs_after = calculate_mrs(
        after_path, ref_stats, weights, reference_by_genre, genre
    )

    delta_mrs = round(mrs_after["mrs"] - mrs_before["mrs"], 2)

    component_deltas = {}
    for group in DEFAULT_WEIGHTS:
        component_deltas[group] = round(
            mrs_after["components"][group] - mrs_before["components"][group], 4
        )

    main_gain = min(component_deltas, key=component_deltas.get)
    main_penalty = max(component_deltas, key=component_deltas.get)

    return {
        "label": label,
        "before_path": before_path,
        "after_path": after_path,
        "mrs_before": mrs_before["mrs"],
        "mrs_after": mrs_after["mrs"],
        "delta_mrs": delta_mrs,
        "components_before": mrs_before["components"],
        "components_after": mrs_after["components"],
        "component_deltas": component_deltas,
        "main_gain": main_gain,
        "main_penalty": main_penalty,
    }
