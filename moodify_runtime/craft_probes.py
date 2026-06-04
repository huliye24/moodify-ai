"""MHP-149→153: Craft Probe Experiments — overbright, transient, stereo, vocal warmth, failure case library.

Each probe produces quantitative metrics that can be turned into gate rules in Build NEM.
"""

from __future__ import annotations

import json
import math
import wave
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import numpy as np


# ═══════════════════════════════════════════════════════════════════════
# MHP-149: Over-Bright Probe
# ═══════════════════════════════════════════════════════════════════════


def detect_over_bright(
    before_path: str,
    after_path: str,
    high_freq: float = 8000.0,
    threshold_db: float = 3.0,
) -> Dict[str, Any]:
    """Detect excessive high-frequency boost in processed audio.

    Uses FFT to compare energy above `high_freq` between before/after.
    Returns: level (none/mild/severe), delta_db, recommendation.
    """
    def _hf_energy(path: str) -> Tuple[float, int]:
        with wave.open(path, "rb") as wf:
            sr = wf.getframerate()
            sw = wf.getsampwidth()
            nf = wf.getnframes()
            raw = wf.readframes(nf)
        if sw == 2:
            samples = np.frombuffer(raw[:nf * 2], dtype=np.int16).astype(np.float64)
        else:
            return 0.0, sr

        n = len(samples)
        window = np.hanning(n)
        fft = np.fft.rfft(samples * window)
        mag = np.abs(fft)
        freqs = np.fft.rfftfreq(n, d=1.0 / sr)

        hf_mask = freqs >= high_freq
        total_mask = freqs >= 20
        hf_e = float(np.sum(mag[hf_mask] ** 2))
        total_e = float(np.sum(mag[total_mask] ** 2))
        return hf_e / max(total_e, 1e-12), sr

    if not Path(before_path).exists() or not Path(after_path).exists():
        return {"level": "none", "delta_db": 0.0, "recommendation": "pass", "error": "file_missing"}

    before_hf, _ = _hf_energy(before_path)
    after_hf, _ = _hf_energy(after_path)

    if before_hf < 1e-12:
        return {"level": "none", "delta_db": 0.0, "recommendation": "pass"}

    ratio = after_hf / before_hf
    delta_db = 10.0 * math.log10(max(ratio, 1e-12))

    if delta_db > threshold_db * 2:
        level = "severe"
        recommendation = "reject"
    elif delta_db > threshold_db:
        level = "mild"
        recommendation = "review"
    else:
        level = "none"
        recommendation = "pass"

    return {
        "level": level,
        "delta_db": round(delta_db, 2),
        "hf_ratio": round(ratio, 4),
        "recommendation": recommendation,
    }


# ═══════════════════════════════════════════════════════════════════════
# MHP-150: Transient Damage Probe
# ═══════════════════════════════════════════════════════════════════════


def detect_transient_damage(
    before_path: str,
    after_path: str,
    crest_drop_threshold: float = 0.30,
) -> Dict[str, Any]:
    """Detect if processing has softened transients excessively.

    Transient damage = crest factor drops >30% after processing.
    """
    def _crest(path: str) -> Optional[float]:
        with wave.open(path, "rb") as wf:
            sw = wf.getsampwidth()
            nf = wf.getnframes()
            raw = wf.readframes(nf)
        if sw != 2:
            return None
        samples = np.frombuffer(raw[:nf * 2], dtype=np.int16).astype(np.float64)
        rms = float(np.sqrt(np.mean(samples ** 2)))
        peak = float(np.max(np.abs(samples)))
        if rms < 1e-12:
            return None
        return peak / rms

    if not Path(before_path).exists() or not Path(after_path).exists():
        return {"level": "none", "crest_drop": 0.0, "recommendation": "pass", "error": "file_missing"}

    before_crest = _crest(before_path)
    after_crest = _crest(after_path)

    if before_crest is None or after_crest is None:
        return {"level": "none", "crest_drop": 0.0, "recommendation": "pass", "error": "crest_calc_failed"}

    crest_drop = (before_crest - after_crest) / before_crest if before_crest > 0 else 0.0

    if crest_drop > crest_drop_threshold * 2:
        level = "severe"
        recommendation = "reject"
    elif crest_drop > crest_drop_threshold:
        level = "mild"
        recommendation = "review"
    else:
        level = "none"
        recommendation = "pass"

    return {
        "level": level,
        "crest_before": round(before_crest, 2),
        "crest_after": round(after_crest, 2),
        "crest_drop": round(crest_drop, 4),
        "recommendation": recommendation,
    }


# ═══════════════════════════════════════════════════════════════════════
# MHP-151: Stereo Width Probe
# ═══════════════════════════════════════════════════════════════════════


def detect_stereo_collapse(
    before_path: str,
    after_path: str,
    collapse_threshold: float = 0.20,
) -> Dict[str, Any]:
    """Detect if processing collapses stereo width.

    Stereo collapse = mid/side ratio increases significantly.
    """
    def _stereo_width(path: str) -> Optional[float]:
        with wave.open(path, "rb") as wf:
            nch = wf.getnchannels()
            sw = wf.getsampwidth()
            nf = wf.getnframes()
            raw = wf.readframes(nf)
        if nch < 2:
            return None  # mono input
        if sw != 2:
            return None

        samples = np.frombuffer(raw[:nf * nch * 2], dtype=np.int16).astype(np.float64)
        samples = samples.reshape(-1, nch)
        left = samples[:, 0]
        right = samples[:, 1]

        mid = (left + right) / 2.0
        side = (left - right) / 2.0

        mid_rms = float(np.sqrt(np.mean(mid ** 2)))
        side_rms = float(np.sqrt(np.mean(side ** 2)))

        if mid_rms < 1e-12:
            return None
        # Width = side/mid ratio. Higher = wider.
        return side_rms / mid_rms

    if not Path(before_path).exists() or not Path(after_path).exists():
        return {"level": "none", "width_drop": 0.0, "recommendation": "pass"}

    before_w = _stereo_width(before_path)
    after_w = _stereo_width(after_path)

    if before_w is None:
        return {"level": "none", "width_drop": 0.0, "recommendation": "pass", "note": "mono_input"}

    if after_w is None:
        return {"level": "severe", "width_drop": 1.0, "recommendation": "reject", "note": "stereo_output_lost"}

    width_drop = (before_w - after_w) / before_w if before_w > 0 else 0.0

    if width_drop > collapse_threshold * 2:
        level = "severe"
        recommendation = "reject"
    elif width_drop > collapse_threshold:
        level = "mild"
        recommendation = "review"
    else:
        level = "none"
        recommendation = "pass"

    return {
        "level": level,
        "width_before": round(before_w, 4),
        "width_after": round(after_w, 4),
        "width_drop": round(width_drop, 4),
        "recommendation": recommendation,
    }


# ═══════════════════════════════════════════════════════════════════════
# MHP-152: Vocal Warmth Probe
# ═══════════════════════════════════════════════════════════════════════


def detect_vocal_thinning(
    before_path: str,
    after_path: str,
    vocal_range: Tuple[float, float] = (200.0, 500.0),
    rms_drop_threshold: float = 0.15,
) -> Dict[str, Any]:
    """Detect if processing thins vocal body by reducing energy in 200-500Hz.

    Vocal thinning = RMS in vocal range drops >15% after processing.
    """
    def _band_rms(path: str, low: float, high: float) -> Tuple[float, int]:
        with wave.open(path, "rb") as wf:
            sr = wf.getframerate()
            sw = wf.getsampwidth()
            nf = wf.getnframes()
            raw = wf.readframes(nf)
        if sw != 2:
            return 0.0, sr

        samples = np.frombuffer(raw[:nf * 2], dtype=np.int16).astype(np.float64)
        n = len(samples)
        window = np.hanning(n)
        fft = np.fft.rfft(samples * window)
        mag = np.abs(fft)
        freqs = np.fft.rfftfreq(n, d=1.0 / sr)

        mask = (freqs >= low) & (freqs <= high)
        if not mask.any():
            return 0.0, sr
        return float(np.sqrt(np.mean(mag[mask] ** 2))), sr

    if not Path(before_path).exists() or not Path(after_path).exists():
        return {"level": "none", "rms_drop": 0.0, "recommendation": "pass", "error": "file_missing"}

    before_rms, _ = _band_rms(before_path, *vocal_range)
    after_rms, _ = _band_rms(after_path, *vocal_range)

    if before_rms < 1e-12:
        return {"level": "none", "rms_drop": 0.0, "recommendation": "pass"}

    rms_drop = (before_rms - after_rms) / before_rms

    if rms_drop > rms_drop_threshold * 2:
        level = "severe"
        recommendation = "reject"
    elif rms_drop > rms_drop_threshold:
        level = "mild"
        recommendation = "review"
    else:
        level = "none"
        recommendation = "pass"

    return {
        "level": level,
        "vocal_rms_before": round(before_rms, 6),
        "vocal_rms_after": round(after_rms, 6),
        "rms_drop": round(rms_drop, 4),
        "recommendation": recommendation,
    }


# ═══════════════════════════════════════════════════════════════════════
# MHP-153: Failure Case Library Probe
# ═══════════════════════════════════════════════════════════════════════


@dataclass
class FailureCase:
    case_id: str
    preset: str
    genre: str
    sample_id: str
    defect_type: str          # over_dark, over_bright, transient_smear, etc.
    severity: str             # mild, severe
    before_path: str = ""
    after_path: str = ""
    metrics: Dict[str, Any] = field(default_factory=dict)
    notes: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def build_failure_case_library(
    output_dir: Path,
    cases: List[FailureCase],
) -> Dict[str, Any]:
    """Write failure cases to a searchable JSONL library."""
    output_dir.mkdir(parents=True, exist_ok=True)
    path = output_dir / "failure_cases.jsonl"

    count = 0
    with path.open("a", encoding="utf-8") as f:
        for case in cases:
            f.write(json.dumps(case.to_dict(), ensure_ascii=False) + "\n")
            count += 1

    return {"path": str(path), "cases_written": count}


def query_failure_cases(
    library_dir: Path,
    defect_type: Optional[str] = None,
    preset: Optional[str] = None,
    genre: Optional[str] = None,
    severity: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """Query the failure case library by filter criteria."""
    path = library_dir / "failure_cases.jsonl"
    if not path.exists():
        return []

    results = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            case = json.loads(line)
            if defect_type and case.get("defect_type") != defect_type:
                continue
            if preset and case.get("preset") != preset:
                continue
            if genre and case.get("genre") != genre:
                continue
            if severity and case.get("severity") != severity:
                continue
            results.append(case)
    return results
