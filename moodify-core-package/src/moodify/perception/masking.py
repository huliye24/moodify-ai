"""
masking.py — Psychoacoustic Masking Prototype (AEP-ACU-007)
=============================================================

Lightweight frequency-domain simultaneous masking model built on top of
AEP-ACU-006 Bark/ERB perceptual spectrum output.

What this does (and doesn't):
  - Estimates masking threshold via simplified spreading function
  - Computes audible residual (energy above masking threshold)
  - Provides sharpness proxy, sibilance risk, fatigue index
  - All thresholds are CONFIGURABLE — not hardcoded as truth
  - Does NOT implement full PEAQ (ITU-R BS.1387)
  - Does NOT claim to replace formal listening tests

Reference:
  Zwicker, E. & Fastl, H. (2007). Psychoacoustics: Facts and Models, Ch.7-8.
  ITU-R BS.1387-2 — PEAQ (conceptual reference only).
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import List, Optional

import numpy as np


# ═══════════════════════════════════════════════════════════════════
# Configurable thresholds — ALL can be overridden
# ═══════════════════════════════════════════════════════════════════

@dataclass
class MaskingConfig:
    """Configurable masking model parameters."""
    # Spreading function slopes (dB/Bark)
    spreading_slope_low: float = 27.0    # dB/Bark for upward spread (masker→higher freq)
    spreading_slope_high: float = -10.0  # dB/Bark for downward spread (masker→lower freq,
                                          # less efficient — asymmetry of masking)

    # Absolute threshold of hearing (dB relative to signal max, simplified)
    absolute_threshold_db: float = -60.0  # Min audible level relative to loudest component

    # Sibilance detection (5-8 kHz in Bark bands ~15-20)
    sibilance_bark_start: int = 15
    sibilance_bark_end: int = 20
    sibilance_risk_threshold_db: float = -15.0  # Energy above this → flagged

    # Sharpness proxy (Zwicker sharpness: weighted by high-freq content)
    sharpness_high_weight_start_bark: int = 14  # ~3 kHz

    # Fatigue index thresholds
    fatigue_presence_threshold_db: float = -10.0   # 2-5 kHz
    fatigue_sibilance_threshold_db: float = -18.0   # 5-8 kHz
    fatigue_air_threshold_db: float = -25.0         # 8 kHz+

    # Post-masking temporal window (ms)
    temporal_window_ms: float = 5.0


# ═══════════════════════════════════════════════════════════════════
# PsychoacousticFeatures dataclass
# ═══════════════════════════════════════════════════════════════════


@dataclass
class PsychoacousticFeatures:
    """Complete psychoacoustic masking analysis output (AEP-ACU-007).

    All fields marked 'risk proxy / hypothesis' are perceptual indicators,
    not objective quality measurements.
    """
    feature_version: str = "psychoacoustic_v0.1"
    sample_rate: int = 44100
    n_bark_bands: int = 24

    # ── Input reference ──
    bark_band_centers_hz: List[float] = field(default_factory=list)
    bark_band_energies_db: List[float] = field(default_factory=list)

    # ── Masking threshold ──
    masking_threshold_db: List[float] = field(default_factory=list)
    audible_residual_db: List[float] = field(default_factory=list)
    residual_above_threshold_bands: int = 0

    # ── Risk proxies ──
    sharpness_proxy: float = 0.0         # risk proxy / hypothesis
    fatigue_index: float = 0.0           # risk proxy / hypothesis
    sibilance_risk: float = 0.0          # risk proxy / hypothesis
    sibilance_band_energy_db: float = -120.0
    sibilance_audible_residual_db: float = 0.0

    # ── Temporal ──
    post_masking_flags: List[int] = field(default_factory=list)

    # ── Config snapshot ──
    config: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "feature_version": self.feature_version,
            "sample_rate": self.sample_rate,
            "n_bark_bands": self.n_bark_bands,
            "input": {
                "bark_band_centers_hz": [round(c, 1) for c in self.bark_band_centers_hz],
                "bark_band_energies_db": [round(e, 2) for e in self.bark_band_energies_db],
            },
            "masking": {
                "threshold_db": [round(t, 2) for t in self.masking_threshold_db],
                "audible_residual_db": [round(r, 2) for r in self.audible_residual_db],
                "residual_above_threshold_bands": self.residual_above_threshold_bands,
            },
            "risk_proxies": {
                "sharpness_proxy": round(self.sharpness_proxy, 3),
                "sharpness_note": "risk proxy / hypothesis — weighted high-frequency audible residual",
                "fatigue_index": round(self.fatigue_index, 3),
                "fatigue_note": "risk proxy / hypothesis — aggregate of presence + sibilance + air residual",
                "sibilance_risk": round(self.sibilance_risk, 3),
                "sibilance_note": "risk proxy / hypothesis — 5-8 kHz Bark bands audible residual",
                "sibilance_band_energy_db": round(self.sibilance_band_energy_db, 2),
                "sibilance_audible_residual_db": round(self.sibilance_audible_residual_db, 2),
            },
            "temporal": {
                "post_masking_flags_count": sum(self.post_masking_flags),
            },
            "config": self.config,
        }

    def to_json(self, path: str = "") -> str:
        data = self.to_dict()
        if path:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        return json.dumps(data, indent=2, ensure_ascii=False)


# ═══════════════════════════════════════════════════════════════════
# Spreading function
# ═══════════════════════════════════════════════════════════════════


def _spreading_function(
    n_bands: int, masker_band: int, masker_level_db: float,
    config: MaskingConfig,
) -> np.ndarray:
    """Simplified spreading function: estimate masking contribution from
    one masker band to all other Bark bands.

    Asymmetry: low frequencies mask high frequencies more efficiently
    than the reverse (upward spread is steeper).

    Returns array of shape (n_bands,) with masking level in dB contributed
    by this masker to each band.
    """
    spread = np.zeros(n_bands, dtype=np.float64)
    masker_bark = float(masker_band)

    for b in range(n_bands):
        delta_bark = float(b) - masker_bark
        if delta_bark >= 0:
            # Upward spread: masker → higher Bark (lower freq → higher freq)
            spread[b] = masker_level_db - config.spreading_slope_low * delta_bark
        else:
            # Downward spread: masker → lower Bark (higher freq → lower freq)
            # Much less efficient → steeper negative slope
            spread[b] = masker_level_db + config.spreading_slope_high * delta_bark

    return spread


def _compute_masking_threshold(
    band_energies_db: np.ndarray,
    band_centers_hz: np.ndarray,
    config: MaskingConfig,
) -> np.ndarray:
    """Compute per-band masking threshold using simplified spreading function.

    For each Bark band:
    1. Identify the band as a potential masker (its own energy)
    2. Spread its masking contribution to all other bands
    3. Take the maximum masking level at each band
    4. Floor to absolute threshold of hearing
    """
    n_bands = len(band_energies_db)
    thresholds = np.full(n_bands, config.absolute_threshold_db, dtype=np.float64)

    # Each band acts as a masker; its masking spreads to other bands
    for m in range(n_bands):
        masker_level = float(band_energies_db[m])
        if masker_level < config.absolute_threshold_db:
            continue  # below hearing threshold → doesn't mask
        spread = _spreading_function(n_bands, m, masker_level, config)
        thresholds = np.maximum(thresholds, spread)

    return thresholds


# ═══════════════════════════════════════════════════════════════════
# Risk proxies
# ═══════════════════════════════════════════════════════════════════


def _compute_sharpness_proxy(
    audible_residual_db: np.ndarray, config: MaskingConfig,
) -> float:
    """Sharpness proxy: weighted sum of high-frequency audible residual.

    Zwicker sharpness weights increase with Bark number.
    This is a simplified proxy — NOT the full Zwicker sharpness model.
    """
    n = len(audible_residual_db)
    weights = np.ones(n, dtype=np.float64)
    start = config.sharpness_high_weight_start_bark
    for b in range(start, n):
        # Weight increases linearly from 1.0 to 4.0 from Bark 14→24
        weights[b] = 1.0 + 3.0 * (b - start) / max(n - start - 1, 1)

    # Only positive residual contributes (audible content)
    residual_pos = np.maximum(audible_residual_db, 0.0)
    return float(np.average(residual_pos, weights=weights))


def _compute_fatigue_index(
    band_energies_db: np.ndarray,
    audible_residual_db: np.ndarray,
    band_centers_hz: np.ndarray,
    config: MaskingConfig,
) -> float:
    """Fatigue index: aggregate risk from presence (2-5k), sibilance (5-8k), air (8k+).

    Each region contributes if its energy + residual exceeds threshold.
    Returns 0.0–1.0, where higher = more potential listening fatigue.
    """
    presence_mask = (band_centers_hz >= 2000) & (band_centers_hz <= 5000)
    sibilance_mask = (band_centers_hz >= 5000) & (band_centers_hz <= 8000)
    air_mask = band_centers_hz > 8000

    def _region_score(mask, threshold_db):
        if not np.any(mask):
            return 0.0
        energy = float(np.max(band_energies_db[mask]))
        residual = float(np.max(np.maximum(audible_residual_db[mask], 0.0)))
        excess = max(0.0, energy - threshold_db) + max(0.0, residual)
        return min(1.0, excess / 30.0)  # Normalize: 30 dB excess → 1.0

    p_score = _region_score(presence_mask, config.fatigue_presence_threshold_db)
    s_score = _region_score(sibilance_mask, config.fatigue_sibilance_threshold_db)
    a_score = _region_score(air_mask, config.fatigue_air_threshold_db)

    # Weighted combination (sibilance weighted higher — most fatiguing)
    return float(min(1.0, 0.25 * p_score + 0.45 * s_score + 0.30 * a_score))


def _compute_sibilance_risk(
    band_energies_db: np.ndarray,
    audible_residual_db: np.ndarray,
    config: MaskingConfig,
) -> float:
    """Sibilance risk: 0.0–1.0 based on energy and audible residual in 5-8 kHz Bark bands."""
    start = config.sibilance_bark_start
    end = min(config.sibilance_bark_end, len(band_energies_db))
    if end <= start:
        return 0.0

    sib_energy = float(np.max(band_energies_db[start:end]))
    sib_residual = float(np.max(np.maximum(audible_residual_db[start:end], 0.0)))

    # Risk increases as energy exceeds threshold and residual is present
    energy_excess = max(0.0, sib_energy - config.sibilance_risk_threshold_db)
    risk = min(1.0, (energy_excess / 15.0) * 0.6 + (sib_residual / 10.0) * 0.4)
    return float(risk)


# ═══════════════════════════════════════════════════════════════════
# Temporal post-masking flags
# ═══════════════════════════════════════════════════════════════════


def _detect_post_masking(
    band_energies_db: np.ndarray,
    config: MaskingConfig,
) -> List[int]:
    """Detect bands where post-masking may be active (strong transient followed by
    temporal masking window).

    Simplified: flag bands with energy > -6 dB (strong masker) as potential
    temporal masker sources. Returns list of band indices.
    """
    flags = []
    threshold = -6.0  # dB — strong signal
    for b, energy in enumerate(band_energies_db):
        if energy > threshold:
            flags.append(int(b))
    return flags


# ═══════════════════════════════════════════════════════════════════
# Main model class
# ═══════════════════════════════════════════════════════════════════


class MaskingModel:
    """Psychoacoustic masking analysis (AEP-ACU-007).

    Takes Bark band energies from AEP-ACU-006 and computes:
      - Frequency masking threshold (simplified spreading function)
      - Audible residual (signal above masking threshold)
      - Sharpness proxy, fatigue index, sibilance risk
      - Post-masking temporal flags

    Usage:
        model = MaskingModel()
        pf = model.analyze(bark_energies_db, bark_centers_hz)
        pf.to_json("masking_features.json")
    """

    def __init__(self, config: Optional[MaskingConfig] = None):
        self.config = config or MaskingConfig()

    def analyze(
        self,
        bark_band_energies_db: List[float],
        bark_band_centers_hz: List[float],
        sr: int = 44100,
    ) -> PsychoacousticFeatures:
        """Run full psychoacoustic analysis on Bark band energies.

        Args:
            bark_band_energies_db: Per-band energy in dB (from ACU-006).
            bark_band_centers_hz: Per-band center frequencies in Hz.
            sr: Sample rate (for metadata only).

        Returns:
            PsychoacousticFeatures dataclass.
        """
        energies_raw = np.array(bark_band_energies_db, dtype=np.float64)
        centers = np.array(bark_band_centers_hz, dtype=np.float64)
        n_bands = len(energies_raw)

        # Normalize: shift so that max energy = 0 dB (relative reference)
        # This makes masking thresholds comparable across different audio levels
        max_energy = float(np.max(energies_raw))
        energies = energies_raw - max_energy  # Now max = 0 dB

        # ── 1. Masking threshold ──
        threshold = _compute_masking_threshold(energies, centers, self.config)

        # ── 2. Audible residual ──
        residual = energies - threshold

        # ── 3. Risk proxies ──
        sharpness = _compute_sharpness_proxy(residual, self.config)
        fatigue = _compute_fatigue_index(energies, residual, centers, self.config)
        sibilance = _compute_sibilance_risk(energies, residual, self.config)

        # ── 4. Sibilance band energy ──
        sib_start = self.config.sibilance_bark_start
        sib_end = min(self.config.sibilance_bark_end, n_bands)
        sib_energy = float(np.max(energies[sib_start:sib_end])) if sib_end > sib_start else -120.0
        sib_residual = float(np.max(np.maximum(residual[sib_start:sib_end], 0.0))) if sib_end > sib_start else 0.0

        # ── 5. Temporal flags ──
        post_mask = _detect_post_masking(energies, self.config)

        # ── 6. Count bands above threshold ──
        above = int(np.sum(residual > 0.0))

        return PsychoacousticFeatures(
            sample_rate=sr,
            n_bark_bands=n_bands,
            bark_band_centers_hz=list(bark_band_centers_hz),
            bark_band_energies_db=list(bark_band_energies_db),
            masking_threshold_db=threshold.tolist(),
            audible_residual_db=residual.tolist(),
            residual_above_threshold_bands=above,
            sharpness_proxy=sharpness,
            fatigue_index=fatigue,
            sibilance_risk=sibilance,
            sibilance_band_energy_db=sib_energy,
            sibilance_audible_residual_db=sib_residual,
            post_masking_flags=post_mask,
            config={
                "spreading_slope_low": self.config.spreading_slope_low,
                "spreading_slope_high": self.config.spreading_slope_high,
                "absolute_threshold_db": self.config.absolute_threshold_db,
                "sibilance_bark_bands": f"{self.config.sibilance_bark_start}-{self.config.sibilance_bark_end}",
                "sibilance_risk_threshold_db": self.config.sibilance_risk_threshold_db,
            },
        )


# ═══════════════════════════════════════════════════════════════════
# Convenience API
# ═══════════════════════════════════════════════════════════════════


def compute_masking(
    bark_energies_db: List[float],
    bark_centers_hz: List[float],
    sr: int = 44100,
    config: Optional[MaskingConfig] = None,
) -> PsychoacousticFeatures:
    """One-shot psychoacoustic masking analysis."""
    model = MaskingModel(config)
    return model.analyze(bark_energies_db, bark_centers_hz, sr)
