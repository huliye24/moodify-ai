"""pedalboard_providers.py — The four v0.1 mix_graph node providers.

EQ / Compressor wrap pedalboard primitives; Stereo is a numpy mid/side matrix
(pedalboard has no width plugin); Limiter is a hard ceiling implemented with
pedalboard.Clipping. Rationale for the Limiter: pedalboard.Limiter applies an
auto-makeup gain that normalizes output to full scale (spotify/pedalboard#282),
which breaks ceiling semantics — the same decision documented in
processing/pedalboard_chain.py and used by the data factory LUFS fix.
"""

from __future__ import annotations

import numpy as np
import pedalboard

from moodify.mix_graph.providers.base import NodeProvider, ProviderError


def _num(parameters: dict, key: str, default: float) -> float:
    value = parameters.get(key, default)
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ProviderError(f"{key} must be a number")
    return float(value)


def _num_range(parameters: dict, key: str, default: float,
               low: float, high: float) -> float:
    value = _num(parameters, key, default)
    if not low <= value <= high:
        raise ProviderError(f"{key} must be within [{low}, {high}], got {value}")
    return value


def _run_board(audio: np.ndarray, sr: int, board: pedalboard.Pedalboard) -> np.ndarray:
    """Run a pedalboard on (n,) or (n, ch) audio, preserving the input layout."""
    is_stereo = audio.ndim > 1 and audio.shape[1] > 1
    x = (audio.T if is_stereo else audio.reshape(1, -1)).astype(np.float32)
    y = board(x, sr)
    return (y.T if is_stereo else y[0]).astype(audio.dtype)


class EQProvider(NodeProvider):
    """Parametric EQ: up to 8 bands of peak / lowshelf / highshelf filters."""

    node_type = "eq"
    summary = "parametric EQ (peak/lowshelf/highshelf bands)"

    MAX_BANDS = 8

    def validate_parameters(self, parameters: dict) -> dict:
        if not isinstance(parameters, dict) or "bands" not in parameters:
            raise ProviderError("eq parameters must contain 'bands'")
        bands = parameters["bands"]
        if not isinstance(bands, list) or not 1 <= len(bands) <= self.MAX_BANDS:
            raise ProviderError(f"bands must be a list of 1..{self.MAX_BANDS} entries")
        canonical = []
        for i, band in enumerate(bands):
            if not isinstance(band, dict):
                raise ProviderError(f"band {i} must be an object")
            unknown = set(band) - {"type", "freq_hz", "gain_db", "q"}
            if unknown:
                raise ProviderError(f"band {i} has unknown keys: {sorted(unknown)}")
            btype = band.get("type")
            if btype not in ("peak", "lowshelf", "highshelf"):
                raise ProviderError(f"band {i} type must be peak|lowshelf|highshelf")
            freq = _num_range(band, "freq_hz", 0.0, 20.0, 20000.0)
            gain = _num_range(band, "gain_db", 0.0, -24.0, 24.0)
            entry: dict = {"type": btype, "freq_hz": freq, "gain_db": gain}
            if btype == "peak":
                entry["q"] = _num_range(band, "q", 0.7, 0.1, 10.0)
            canonical.append(entry)
        return {"bands": canonical}

    def render(self, audio: np.ndarray, sr: int, parameters: dict) -> np.ndarray:
        parameters = self.validate_parameters(parameters)
        board = pedalboard.Pedalboard([])
        for band in parameters["bands"]:
            if band["type"] == "peak":
                board.append(pedalboard.PeakFilter(
                    cutoff_frequency_hz=band["freq_hz"],
                    gain_db=band["gain_db"], q=band["q"]))
            elif band["type"] == "lowshelf":
                board.append(pedalboard.LowShelfFilter(
                    cutoff_frequency_hz=band["freq_hz"], gain_db=band["gain_db"]))
            else:
                board.append(pedalboard.HighShelfFilter(
                    cutoff_frequency_hz=band["freq_hz"], gain_db=band["gain_db"]))
        return _run_board(audio, sr, board)


class CompressorProvider(NodeProvider):
    """Dynamics compressor (pedalboard.Compressor)."""

    node_type = "compressor"
    summary = "dynamics compressor (threshold/ratio/attack/release)"

    def validate_parameters(self, parameters: dict) -> dict:
        if not isinstance(parameters, dict):
            raise ProviderError("compressor parameters must be an object")
        unknown = set(parameters) - {"threshold_db", "ratio", "attack_ms", "release_ms"}
        if unknown:
            raise ProviderError(f"unknown keys: {sorted(unknown)}")
        return {
            "threshold_db": _num_range(parameters, "threshold_db", -12.0, -60.0, 0.0),
            "ratio": _num_range(parameters, "ratio", 1.2, 1.0, 20.0),
            "attack_ms": _num_range(parameters, "attack_ms", 25.0, 0.1, 500.0),
            "release_ms": _num_range(parameters, "release_ms", 250.0, 1.0, 2000.0),
        }

    def render(self, audio: np.ndarray, sr: int, parameters: dict) -> np.ndarray:
        parameters = self.validate_parameters(parameters)
        board = pedalboard.Pedalboard([pedalboard.Compressor(
            threshold_db=parameters["threshold_db"],
            ratio=parameters["ratio"],
            attack_ms=parameters["attack_ms"],
            release_ms=parameters["release_ms"])])
        return _run_board(audio, sr, board)


class StereoProvider(NodeProvider):
    """Stereo width via mid/side matrix. width=1.0 is a bitwise identity fast path."""

    node_type = "stereo"
    summary = "stereo width (mid/side matrix; mono input is a no-op)"

    def validate_parameters(self, parameters: dict) -> dict:
        if not isinstance(parameters, dict):
            raise ProviderError("stereo parameters must be an object")
        unknown = set(parameters) - {"width"}
        if unknown:
            raise ProviderError(f"unknown keys: {sorted(unknown)}")
        return {"width": _num_range(parameters, "width", 1.0, 0.0, 2.0)}

    def render(self, audio: np.ndarray, sr: int, parameters: dict) -> np.ndarray:
        parameters = self.validate_parameters(parameters)
        width = parameters["width"]
        if width == 1.0 or audio.ndim == 1 or audio.shape[1] < 2:
            return audio  # identity fast path (also covers mono inputs)
        mid = (audio[:, 0] + audio[:, 1]) / 2.0
        side = (audio[:, 0] - audio[:, 1]) / 2.0
        left = mid + width * side
        right = mid - width * side
        return np.column_stack([left, right]).astype(audio.dtype)


class LimiterProvider(NodeProvider):
    """Hard ceiling limiter: optional input gain + Clipping at the ceiling (dBFS)."""

    node_type = "limiter"
    summary = "hard ceiling (Clipping at ceiling_db; Limiter auto-makeup-gain avoided)"

    def validate_parameters(self, parameters: dict) -> dict:
        if not isinstance(parameters, dict):
            raise ProviderError("limiter parameters must be an object")
        unknown = set(parameters) - {"ceiling_db", "input_gain_db"}
        if unknown:
            raise ProviderError(f"unknown keys: {sorted(unknown)}")
        return {
            "ceiling_db": _num_range(parameters, "ceiling_db", -1.0, -12.0, 0.0),
            "input_gain_db": _num_range(parameters, "input_gain_db", 0.0, -12.0, 12.0),
        }

    def render(self, audio: np.ndarray, sr: int, parameters: dict) -> np.ndarray:
        parameters = self.validate_parameters(parameters)
        gain_db = parameters["input_gain_db"]
        ceiling_db = parameters["ceiling_db"]
        board = pedalboard.Pedalboard([])
        if gain_db != 0.0:
            board.append(pedalboard.Gain(gain_db=gain_db))
        board.append(pedalboard.Clipping(threshold_db=ceiling_db))
        return _run_board(audio, sr, board)
