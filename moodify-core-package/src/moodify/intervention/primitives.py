"""Versioned, bypassable intervention primitives (MFY_PRESERVE_IDENTITY_INTERVENTION_001).

Each primitive is a pure function (audio, sr, params) -> processed audio plus
detectors that classify *limitations* before any processing is proposed.
Primitives never exceed their declared max strength and always report a
defined failure state (no silent processing).

A primitive only fires when its detector reports a limitation; otherwise the
pipeline bypasses it. Identity risk is declared per primitive; anything above
NONE must pass the identity gate before selection.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

import numpy as np

# ---------------------------------------------------------------- contracts

DETECT_THRESHOLD_DC = 1e-4  # ~ -80 dBFS mean offset triggers DC repair
CLIP_LEVEL = 0.999          # |x| above this counts as clipped flat segment
CLIP_MIN_SEGMENT = 3        # minimum consecutive samples to call it clipping
CLIP_MAX_REPAIR_SEGMENT = 16  # segments longer than this are reported, not repaired
TONAL_MAX_SHELF_DB = 0.5    # hard ceiling for the conservative tonal primitive


@dataclass(frozen=True)
class PrimitiveContract:
    """Declared, versioned contract of one intervention primitive."""

    primitive_id: str
    version: str
    scope: str
    max_strength: str
    identity_risk: str  # NONE | LOW | MEDIUM
    failure_state: str
    default_enabled: bool
    notes: str = ""


@dataclass(frozen=True)
class InterventionPrimitive:
    contract: PrimitiveContract
    detect: Callable[[np.ndarray, int], dict[str, float]]
    apply: Callable[[np.ndarray, int, dict[str, float]], np.ndarray]


def _validate_audio(audio: np.ndarray) -> None:
    if audio.size == 0:
        raise ValueError("empty audio")
    if not np.isfinite(audio).all():
        raise ValueError("audio contains NaN/Inf; refusing silent processing")


def _to_2d(audio: np.ndarray) -> np.ndarray:
    return audio if audio.ndim == 2 else audio[:, None]


def _from_2d(audio: np.ndarray, orig_shape: tuple[int, ...]) -> np.ndarray:
    return audio[:, 0] if len(orig_shape) == 1 else audio


# ------------------------------------------------------------ dc offset fix

def detect_dc_offset(audio: np.ndarray, sr: int) -> dict[str, float]:
    """Mean offset per channel; returns dc_db (worst channel) and active flag."""
    x = _to_2d(audio)
    dc = float(np.mean(x, axis=0).max() if x.shape[1] > 1 else float(np.mean(x)))
    dc_db = 20.0 * np.log10(abs(dc)) if abs(dc) > 1e-12 else -300.0
    return {"dc": dc, "dc_db": float(dc_db), "active": float(abs(dc) > DETECT_THRESHOLD_DC)}


def apply_dc_offset_fix(audio: np.ndarray, sr: int, params: dict[str, float]) -> np.ndarray:
    _validate_audio(audio)
    shape = audio.shape
    x = _to_2d(audio)
    dc = np.mean(x, axis=0, keepdims=True)
    out = x - dc
    return _from_2d(out, shape)


# ----------------------------------------------------------- clip peak repair

def detect_clip_segments(audio: np.ndarray, sr: int) -> dict[str, float]:
    """Count clipped flat segments and the longest one; repair candidates are short ones."""
    x = _to_2d(audio)
    total_segments = 0
    repairable = 0
    longest = 0
    for ch in range(x.shape[1]):
        mask = np.abs(x[:, ch]) >= CLIP_LEVEL
        if not mask.any():
            continue
        changes = np.diff(mask.astype(np.int8))
        starts = np.where(changes == 1)[0] + 1
        if mask[0]:
            starts = np.concatenate(([0], starts))
        ends = np.where(changes == -1)[0] + 1
        if mask[-1]:
            ends = np.concatenate((ends, [mask.size]))
        for s, e in zip(starts, ends):
            length = int(e - s)
            total_segments += 1
            longest = max(longest, length)
            if length <= CLIP_MAX_REPAIR_SEGMENT:
                repairable += 1
    return {
        "clip_segments": float(total_segments),
        "clip_repairable": float(repairable),
        "clip_longest_segment": float(longest),
        "active": float(repairable > 0),
    }


def apply_clip_peak_repair(audio: np.ndarray, sr: int, params: dict[str, float]) -> np.ndarray:
    """Linear-transition repair of short clipped flat segments (<= CLIP_MAX_REPAIR_SEGMENT).

    Long segments are left untouched (reported via measurements). The repair
    never exceeds the neighbouring sample magnitudes, keeping the identity
    impact low.
    """
    _validate_audio(audio)
    shape = audio.shape
    x = _to_2d(audio).copy()
    for ch in range(x.shape[1]):
        mask = np.abs(x[:, ch]) >= CLIP_LEVEL
        if not mask.any():
            continue
        changes = np.diff(mask.astype(np.int8))
        starts = np.where(changes == 1)[0] + 1
        if mask[0]:
            starts = np.concatenate(([0], starts))
        ends = np.where(changes == -1)[0] + 1
        if mask[-1]:
            ends = np.concatenate(([ends, [mask.size]]))
        for s, e in zip(starts, ends):
            length = int(e - s)
            if length > CLIP_MAX_REPAIR_SEGMENT or length < CLIP_MIN_SEGMENT:
                continue
            left = x[s - 1, ch] if s > 0 else 0.0
            right = x[e, ch] if e < x.shape[0] else 0.0
            x[s:e, ch] = np.linspace(left, right, length + 2)[1:-1]
    return _from_2d(x, shape)


# ----------------------------------------------- tonal balance (conservative)

def _band_energy_db(x: np.ndarray, sr: int, lo: float, hi: float) -> float:
    spec = np.fft.rfft(x, axis=0)
    freqs = np.fft.rfftfreq(x.shape[0], 1.0 / sr)
    band = (freqs >= lo) & (freqs <= hi)
    if not band.any():
        return -300.0
    power = (np.abs(spec[band]) ** 2).mean()
    return float(20.0 * np.log10(power + 1e-12))


def detect_tonal_imbalance(audio: np.ndarray, sr: int) -> dict[str, float]:
    """Low (20-120 Hz) and high (10-20 kHz) energy share relative to full band.

    Fires only when a band's share of total energy is below the threshold —
    i.e. the band has content in a healthy mix but is missing here. A signal
    that simply has no low-frequency content by design is not a defect we can
    claim, so the detector is conservative about it.
    """
    x = _to_2d(audio)
    spec = np.abs(np.fft.rfft(x, axis=0)) ** 2
    freqs = np.fft.rfftfreq(x.shape[0], 1.0 / sr)
    total = float(spec.sum()) + 1e-12
    low = float(spec[(freqs >= 20.0) & (freqs <= 120.0)].sum())
    high = float(spec[(freqs >= 10000.0) & (freqs <= 20000.0)].sum())
    low_ratio = low / total
    high_ratio = high / total
    return {
        "low_band_share": low_ratio,
        "high_band_share": high_ratio,
        "low_band_share_db": float(20.0 * np.log10(low_ratio + 1e-12)),
        "high_band_share_db": float(20.0 * np.log10(high_ratio + 1e-12)),
        "active": float(low_ratio < 0.005 or high_ratio < 0.005),
    }


def apply_tonal_balance_conservative(audio: np.ndarray, sr: int, params: dict[str, float]) -> np.ndarray:
    """Very conservative shelf correction, hard-capped at ±TONAL_MAX_SHELF_DB.

    The correction magnitude is derived from the *detected deficit* and
    clamped to the declared max strength; the pipeline never picks arbitrary
    values. MEDIUM identity risk: selection requires the identity gate.
    """
    _validate_audio(audio)
    low_gain = float(np.clip(params.get("low_gain_db", 0.0), -TONAL_MAX_SHELF_DB, TONAL_MAX_SHELF_DB))
    high_gain = float(np.clip(params.get("high_gain_db", 0.0), -TONAL_MAX_SHELF_DB, TONAL_MAX_SHELF_DB))
    if abs(low_gain) < 1e-9 and abs(high_gain) < 1e-9:
        return audio
    from moodify.processing.operators import apply_eq

    shape = audio.shape
    x = audio if audio.ndim == 2 else audio[:, None]
    out = apply_eq(
        x,
        sr,
        low_shelf_gain_db=low_gain,
        low_shelf_freq=90.0,
        high_shelf_gain_db=high_gain,
        high_shelf_freq=12000.0,
    )
    return out[:, 0] if len(shape) == 1 else out


# ------------------------------------------------------------------- registry

DC_OFFSET_FIX = InterventionPrimitive(
    contract=PrimitiveContract(
        primitive_id="dc_offset_fix",
        version="v1",
        scope="full-mix, any format; removes constant per-channel offset",
        max_strength="full DC removal (|dc| > 1e-4 fires); no gain change",
        identity_risk="NONE",
        failure_state="NaN/Inf input -> ValueError (never silent)",
        default_enabled=True,
        notes="DC is not musical content; spectrum impact at 0 Hz only",
    ),
    detect=detect_dc_offset,
    apply=apply_dc_offset_fix,
)

CLIP_PEAK_REPAIR = InterventionPrimitive(
    contract=PrimitiveContract(
        primitive_id="clip_peak_repair",
        version="v1",
        scope="full-mix; short clipped flat segments (<= 16 samples)",
        max_strength="linear transition over repaired segment; never exceeds neighbours",
        identity_risk="LOW",
        failure_state="long/edge segments reported, not repaired; NaN input -> ValueError",
        default_enabled=True,
        notes="long clipping is a mastering defect signal, not auto-fixed",
    ),
    detect=detect_clip_segments,
    apply=apply_clip_peak_repair,
)

TONAL_BALANCE_CONSERVATIVE = InterventionPrimitive(
    contract=PrimitiveContract(
        primitive_id="tonal_balance_very_conservative",
        version="v1",
        scope="full-mix; low band (20-120 Hz) or high band (10-20 kHz) deficit",
        max_strength="±0.5 dB shelf correction (hard cap)",
        identity_risk="MEDIUM",
        failure_state="FFT failure -> ValueError; imbalance below threshold -> bypassed",
        default_enabled=False,  # registered; default OFF until human listening approval
        notes="not a modern-master template; never generic brightness",
    ),
    detect=detect_tonal_imbalance,
    apply=apply_tonal_balance_conservative,
)

PRIMITIVES: dict[str, InterventionPrimitive] = {
    p.contract.primitive_id: p for p in (DC_OFFSET_FIX, CLIP_PEAK_REPAIR, TONAL_BALANCE_CONSERVATIVE)
}
