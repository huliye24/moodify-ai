"""
pedalboard_chain.py — MoodifyDSPChain
=====================================
Maps 15 craft-chain parameters to pedalboard effects and processes audio.

Param mapping (from craft_chains.py PARAM_KEYS):
  P01-P03: PeakFilter (vocal presence)
  P04-P05: LowShelfFilter (low warmth)
  P06-P09: Compressor (dynamics)
  P10-P12: Reverb (space)
  P13:     Distortion (harmonic drive)
  P14-P15: HighShelfFilter (air)

Safety: Gain + Limiter at end of chain.
"""

from __future__ import annotations

import numpy as np
import pedalboard


class MoodifyDSPChain:
    """Builds and applies a pedalboard effect chain from craft-card parameters."""

    def __init__(self, params: dict | None = None):
        self.params = params or {}

    def build_chain(self, params: dict) -> pedalboard.Pedalboard:
        """Construct a pedalboard.Pedalboard from a 15-param craft dict."""

        def _get(key, default=0.0):
            return float(params.get(key, default))

        board = pedalboard.Pedalboard([])

        # P01-P03: Vocal presence (PeakFilter)
        p01 = _get("P01_vocal_presence_freq", 3000)
        p02 = _get("P02_vocal_presence_gain", 0)
        p03 = _get("P03_vocal_presence_q", 0.7)
        if abs(p02) > 0.01:
            board.append(pedalboard.PeakFilter(
                cutoff_frequency_hz=p01, gain_db=p02, q=p03,
            ))

        # P04-P05: Low warmth (LowShelfFilter)
        p04 = _get("P04_proximity_low_freq", 200)
        p05 = _get("P05_proximity_low_gain", 0)
        if abs(p05) > 0.01:
            board.append(pedalboard.LowShelfFilter(
                cutoff_frequency_hz=p04, gain_db=p05,
            ))

        # P06-P09: Dynamics (Compressor)
        p06 = _get("P06_compression_ratio", 2)
        p07 = _get("P07_compression_attack", 15)
        p08 = _get("P08_compression_release", 150)
        p09 = _get("P09_compression_threshold", -24)
        board.append(pedalboard.Compressor(
            threshold_db=p09, ratio=p06,
            attack_ms=p07, release_ms=p08,
        ))

        # P10-P12: Space (Reverb)
        p11 = _get("P11_reverb_dry_wet", 0.2)
        p12 = _get("P12_reverb_width", 0.8)
        if p11 > 0.005:
            board.append(pedalboard.Reverb(
                room_size=p11, damping=0.5,
                wet_level=p11, dry_level=1.0 - p11,
                width=p12,
            ))

        # P13: Harmonic drive (Distortion)
        p13 = _get("P13_harmonic_drive", 0)
        if p13 > 0.002:
            drive_db = p13 * 20.0
            board.append(pedalboard.Distortion(drive_db=drive_db))

        # P14-P15: Air (HighShelfFilter)
        p14 = _get("P14_high_shelf_freq", 10000)
        p15 = _get("P15_high_shelf_gain", 0)
        if abs(p15) > 0.01:
            board.append(pedalboard.HighShelfFilter(
                cutoff_frequency_hz=p14, gain_db=p15,
            ))

        # Output gain staging
        board.append(pedalboard.Gain())

        # Safety limiter
        board.append(pedalboard.Limiter())

        return board

    def process(self, audio: np.ndarray, sr: int, params: dict | None = None) -> np.ndarray:
        """Process audio through the pedalboard chain.

        Args:
            audio: numpy array, shape (samples,) or (samples, channels)
            sr: sample rate in Hz
            params: optional override params dict

        Returns:
            numpy array with same shape and sample rate as input.
        """
        if params is None:
            params = self.params

        board = self.build_chain(params)

        # pedalboard expects float32, (channels, samples)
        is_stereo = audio.ndim > 1 and audio.shape[1] > 1

        if is_stereo:
            # Convert (samples, 2) -> (2, samples) for pedalboard
            audio_t = audio.T.astype(np.float32).copy()
        else:
            # Convert (samples,) -> (1, samples)
            audio_t = audio.reshape(1, -1).astype(np.float32).copy()

        processed = board(audio_t, sr)

        if is_stereo:
            # Convert back (2, samples) -> (samples, 2)
            result = processed.T
        else:
            # Convert back (1, samples) -> (samples,)
            result = processed[0]

        return result.astype(audio.dtype)


def create_chain_from_code(emotion_code: str) -> MoodifyDSPChain:
    """Factory: create a MoodifyDSPChain from an emotion code (GA, SE, etc.)."""
    from moodify.knowledge.craft_chains import get_recommended_params

    params = get_recommended_params(emotion_code)
    return MoodifyDSPChain(params)
