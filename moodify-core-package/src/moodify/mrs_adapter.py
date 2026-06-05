"""mrs_adapter.py — MAP v0.2 MRS Adapter (MHP-854 / MHP-869).

Thin bridge between v01 pipeline types and the moodify_runtime MRS engine.
Replaces the inline mrs_proxy_v01 with calibrated MRS when available.

Consumers MUST check QualityGate.mrs_version before interpreting MRS values:
  - "mrs_proxy_v01"          = inline fallback (always available)
  - "mrs_proxy_v01_fallback" = MRS engine failed, using proxy
  - "mrs_calibrated_v02"     = calibrated MRS Open v0.3.1 + over-dark + gate
"""

from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger(__name__)

# Lazy-loaded MRS engine reference
_MRS_ENGINE: Any = None
_MRS_ENGINE_ERROR: str | None = None


def _try_load_mrs_engine() -> bool:
    """Attempt to import mrs_engine.score_audio. Returns True on success."""
    global _MRS_ENGINE, _MRS_ENGINE_ERROR
    if _MRS_ENGINE is not None:
        return True
    if _MRS_ENGINE_ERROR is not None:
        return False
    try:
        from moodify_runtime.mrs_engine import score_audio as _score_audio

        _MRS_ENGINE = _score_audio
        return True
    except Exception as exc:
        _MRS_ENGINE_ERROR = f"mrs_engine_import_failed: {exc}"
        logger.warning("MRS engine unavailable, using proxy fallback: %s", exc)
        return False


def score_for_quality_gate(
    before_path: str,
    after_path: str,
    genre: str = "",
    preset: str = "",
    sample_id: str = "",
) -> "QualityGate":
    """Score a before/after pair and return a QualityGate for v01 pipeline.

    Uses calibrated MRS engine when available; falls back to inline proxy.

    Args:
        before_path: Path to the original (pre-processing) audio file.
        after_path: Path to the processed audio file.
        genre: Genre hint for per-genre thresholds.
        preset: DSP preset name for metadata.
        sample_id: Optional sample identifier.

    Returns:
        QualityGate with appropriate mrs_version and all fields populated.
    """
    from moodify.v01_types import QualityGate

    # Compute inline deltas and warnings (always needed)
    deltas, warnings_ = _compute_deltas_and_warnings(before_path, after_path)

    # Try calibrated MRS
    if _try_load_mrs_engine():
        try:
            result = _MRS_ENGINE(
                before_path=before_path,
                after_path=after_path,
                genre=genre,
                preset=preset,
                sample_id=sample_id,
            )
            if result.error is None:
                # Map MRSScoreResult → QualityGate
                mrs_before = (
                    result.mrs_open_before
                    if result.mrs_open_before is not None
                    else (result.pseudo_mrs_before or 0.0)
                )
                mrs_after = (
                    result.mrs_open_after
                    if result.mrs_open_after is not None
                    else (result.pseudo_mrs_after or 0.0)
                )
                mrs_delta = (
                    result.mrs_open_delta
                    if result.mrs_open_delta is not None
                    else (result.pseudo_mrs_delta or 0.0)
                )

                damage_loss = result.over_dark_score
                risk_flags = _map_engine_risk(result, mrs_delta, damage_loss)

                # Merge engine warnings with inline warnings
                all_warnings = list(warnings_)
                if result.gate_reasons:
                    all_warnings.extend(result.gate_reasons)

                mrs_version = (
                    "mrs_calibrated_v02"
                    if result.mrs_open_available
                    else "mrs_proxy_v01_fallback"
                )

                passed = result.gate_decision == "pass" and damage_loss < 0.25

                return QualityGate(
                    passed=passed,
                    warnings=all_warnings,
                    deltas=deltas,
                    mrs_version=mrs_version,
                    mrs_before=round(mrs_before, 2),
                    mrs_after=round(mrs_after, 2),
                    mrs_delta=round(mrs_delta, 2),
                    damage_loss=round(damage_loss, 3),
                    risk_flags=risk_flags,
                )
        except Exception as exc:
            logger.warning("MRS engine call failed, using proxy fallback: %s", exc)

    # Fallback: use inline proxy
    mrs_before = _mrs_proxy_inline(before_path)
    mrs_after = _mrs_proxy_inline(after_path)
    mrs_delta = round(mrs_after - mrs_before, 2)
    damage_loss = _damage_loss_inline(deltas, warnings_)
    risk_flags = _risk_flags_inline(deltas, warnings_, mrs_delta, damage_loss)

    if mrs_delta < -1.0:
        warnings_.append("MRS proxy decreased after processing.")

    passed = not warnings_ and damage_loss < 0.25

    return QualityGate(
        passed=passed,
        warnings=warnings_,
        deltas=deltas,
        mrs_version="mrs_proxy_v01",
        mrs_before=round(mrs_before, 2),
        mrs_after=round(mrs_after, 2),
        mrs_delta=mrs_delta,
        damage_loss=round(damage_loss, 3),
        risk_flags=risk_flags,
    )


# ═══════════════════════════════════════════════════════════════════════════
# Inline helpers (fallback when MRS engine unavailable)
# ═══════════════════════════════════════════════════════════════════════════


def _mrs_proxy_inline(wav_path: str) -> float:
    """Compute the v0.1 inline MRS proxy from a WAV file directly."""
    import math

    import numpy as np

    try:
        from moodify.audio_io import load_audio

        audio, sr = load_audio(wav_path, always_2d=False)
        if audio.ndim > 1 and audio.shape[1] >= 2:
            mono = audio.mean(axis=1)
            corr = float(np.corrcoef(audio[:, 0], audio[:, 1])[0, 1])
        else:
            mono = audio if audio.ndim == 1 else audio[:, 0]
            corr = 1.0

        mono = mono.astype(np.float32)
        rms = float(np.sqrt(np.mean(mono ** 2)) + 1e-12)
        peak = float(20.0 * math.log10(np.max(np.abs(mono)) + 1e-12))
        crest = float(np.max(np.abs(mono)) / (rms + 1e-12))

        # Dynamic range: P95 – P05 in 100ms windows
        win_len = int(0.1 * sr)
        if win_len >= 4 and len(mono) >= win_len:
            hop = max(1, win_len // 2)
            rms_vals = []
            for i in range(0, len(mono) - win_len, hop):
                w = mono[i: i + win_len]
                rms_vals.append(
                    float(20.0 * math.log10(np.sqrt(np.mean(w ** 2)) + 1e-12))
                )
            if len(rms_vals) >= 3:
                dyn_range = float(
                    np.percentile(rms_vals, 95) - np.percentile(rms_vals, 5)
                )
            else:
                dyn_range = 12.0
        else:
            dyn_range = 12.0

        # Band RMS via FFT
        n = len(mono)
        fft = np.abs(np.fft.rfft(mono * np.hanning(n)))
        freqs = np.fft.rfftfreq(n, 1.0 / sr)
        total = np.sum(fft ** 2) + 1e-12

        def _band_rms(f1: float, f2: float) -> float:
            mask = (freqs >= f1) & (freqs <= f2)
            e = np.sum(fft[mask] ** 2) / total
            return float(20.0 * math.log10(np.sqrt(e + 1e-12)))

        rms_air_val = _band_rms(8000, 16000)
        rms_presence_val = _band_rms(2000, 5000)
        rms_bass_val = _band_rms(60, 250)

        # Same formula as v01_pipeline._mrs_proxy()
        def _clamp(v: float, lo: float = 0.0, hi: float = 1.0) -> float:
            return max(lo, min(hi, v))

        dynamic = _clamp(1.0 - abs(dyn_range - 10.0) / 20.0)
        crest_norm = _clamp(1.0 - abs(crest - 5.0) / 8.0)
        stereo = (
            _clamp(1.0 - abs(corr - 0.6) / 0.8)
            if audio.ndim > 1 and audio.shape[1] >= 2
            else 0.7
        )
        air_norm = _clamp(1.0 - abs(rms_air_val + 18.0) / 22.0)
        presence_norm = _clamp(1.0 - abs(rms_presence_val + 12.0) / 22.0)
        peak_norm = _clamp(1.0 - max(0.0, peak + 0.2) / 6.0)

        score = 800.0 + 400.0 * (
            (dynamic + crest_norm + stereo + air_norm + presence_norm + peak_norm) / 6.0
        )
        return round(score, 2)
    except Exception:
        return 800.0


def _compute_deltas_and_warnings(
    before_path: str, after_path: str
) -> tuple[dict, list[str]]:
    """Compute before/after deltas and warnings from audio files."""
    import math

    import numpy as np

    from moodify.audio_io import load_audio

    warnings_: list[str] = []
    deltas: dict[str, float] = {}

    try:
        audio_b, sr_b = load_audio(before_path, always_2d=False)
        audio_a, sr_a = load_audio(after_path, always_2d=False)
    except Exception:
        return deltas, warnings_

    if audio_b.ndim > 1 and audio_b.shape[1] >= 2:
        mono_b = audio_b.mean(axis=1)
        corr_b = float(np.corrcoef(audio_b[:, 0], audio_b[:, 1])[0, 1])
    else:
        mono_b = audio_b if audio_b.ndim == 1 else audio_b[:, 0]
        corr_b = 1.0

    if audio_a.ndim > 1 and audio_a.shape[1] >= 2:
        mono_a = audio_a.mean(axis=1)
        corr_a = float(np.corrcoef(audio_a[:, 0], audio_a[:, 1])[0, 1])
        channels_a = 2
    else:
        mono_a = audio_a if audio_a.ndim == 1 else audio_a[:, 0]
        corr_a = 1.0
        channels_a = 1

    mono_b = mono_b.astype(np.float32)
    mono_a = mono_a.astype(np.float32)

    # Basic metrics
    peak_b = float(20.0 * math.log10(np.max(np.abs(mono_b)) + 1e-12))
    peak_a = float(20.0 * math.log10(np.max(np.abs(mono_a)) + 1e-12))
    crest_b = float(np.max(np.abs(mono_b)) / (np.sqrt(np.mean(mono_b ** 2)) + 1e-12))
    crest_a = float(np.max(np.abs(mono_a)) / (np.sqrt(np.mean(mono_a ** 2)) + 1e-12))

    def _dyn_range(mono: np.ndarray, sr: int) -> float:
        win_len = int(0.1 * sr)
        if win_len < 4 or len(mono) < win_len:
            return 12.0
        hop = max(1, win_len // 2)
        rms_vals = []
        for i in range(0, len(mono) - win_len, hop):
            w = mono[i : i + win_len]
            rms_vals.append(
                float(20.0 * math.log10(np.sqrt(np.mean(w ** 2)) + 1e-12))
            )
        if len(rms_vals) < 3:
            return 12.0
        return float(np.percentile(rms_vals, 95) - np.percentile(rms_vals, 5))

    dr_b = _dyn_range(mono_b, sr_b)
    dr_a = _dyn_range(mono_a, sr_a)

    # Band energy (air)
    def _band_energy(mono: np.ndarray, sr: int, f1: float, f2: float) -> float:
        n = len(mono)
        fft = np.abs(np.fft.rfft(mono * np.hanning(n)))
        freqs = np.fft.rfftfreq(n, 1.0 / sr)
        total = np.sum(fft ** 2) + 1e-12
        mask = (freqs >= f1) & (freqs <= f2)
        e = np.sum(fft[mask] ** 2) / total
        return float(20.0 * math.log10(np.sqrt(e + 1e-12)))

    air_b = _band_energy(mono_b, sr_b, 8000, 16000)
    air_a = _band_energy(mono_a, sr_a, 8000, 16000)
    presence_b = _band_energy(mono_b, sr_b, 2000, 5000)
    presence_a = _band_energy(mono_a, sr_a, 2000, 5000)
    bass_b = _band_energy(mono_b, sr_b, 60, 250)
    bass_a = _band_energy(mono_a, sr_a, 60, 250)

    deltas = {
        "peak_db": round(peak_a - peak_b, 2),
        "crest_factor": round(crest_a - crest_b, 2),
        "dynamic_range_db": round(dr_a - dr_b, 2),
        "correlation_lr": round(corr_a - corr_b, 3),
        "air": round(air_a - air_b, 2),
        "presence": round(presence_a - presence_b, 2),
        "bass": round(bass_a - bass_b, 2),
    }

    # Warnings
    if peak_a > -0.1:
        warnings_.append("Output peak is too close to 0 dBFS.")
    if deltas["dynamic_range_db"] < -4.0:
        warnings_.append("Processing reduced dynamic range by more than 4 dB.")
    if channels_a == 2 and corr_a < 0.05:
        warnings_.append(
            "Output stereo correlation is very low; check mono compatibility."
        )
    if deltas["air"] < -6.0:
        warnings_.append("Processing removed substantial air-band energy.")

    return deltas, warnings_


def _map_engine_risk(
    result: Any, mrs_delta: float, damage_loss: float
) -> list[str]:
    """Map MRSScoreResult fields to risk flags."""
    flags: list[str] = []
    if result.over_dark_level in ("mild", "severe"):
        flags.append("over_dark")
    if result.over_dark_level == "severe":
        flags.append("dynamic_damage")
    if mrs_delta < -1.0:
        flags.append("mrs_regression")
    if damage_loss >= 0.25:
        flags.append("damage_loss_high")
    return flags


def _damage_loss_inline(deltas: dict, warnings: list[str]) -> float:
    """Compute damage loss from deltas (fallback)."""
    loss = 0.04 * len(warnings)
    loss += max(0.0, -deltas.get("dynamic_range_db", 0.0) - 2.0) * 0.03
    loss += max(0.0, -deltas.get("air", 0.0) - 3.0) * 0.025
    loss += max(0.0, -deltas.get("crest_factor", 0.0) - 1.5) * 0.025
    return round(min(loss, 1.0), 3)


def _risk_flags_inline(
    deltas: dict, warnings: list[str], mrs_delta: float, damage_loss: float
) -> list[str]:
    """Compute risk flags from deltas (fallback)."""
    flags = []
    if any("peak" in w.lower() for w in warnings):
        flags.append("peak_risk")
    if deltas.get("air", 0.0) < -6.0:
        flags.append("over_dark")
    if deltas.get("dynamic_range_db", 0.0) < -4.0:
        flags.append("dynamic_damage")
    if mrs_delta < -1.0:
        flags.append("mrs_regression")
    if damage_loss >= 0.25:
        flags.append("damage_loss_high")
    return flags
