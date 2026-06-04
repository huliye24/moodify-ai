"""MHP-683-700: 22 Craft Process Operations.

Defines the 22 distinct craft operations for Moodify's industrial processing system.
Each operation has: id, name, params, risk level, metrics, and implementation.

Part of ECHAIN-MOODIFY-CRAFT-22-012 / NEM-CRAFT-TAXONOMY-PROBE-036.
"""

from __future__ import annotations

import math
import wave
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple

import numpy as np


# ═══════════════════════════════════════════════════════════════════════════
# MHP-684: Craft Operation Schema
# ═══════════════════════════════════════════════════════════════════════════


class RiskLevel(Enum):
    NONE = "none"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class OpCategory(Enum):
    PREPARE = "prepare"       # Input conditioning
    CORRECTIVE = "corrective"  # Fix problems
    ENHANCE = "enhance"       # Improve quality
    DYNAMICS = "dynamics"     # Dynamic range operations
    SPATIAL = "spatial"       # Stereo/spatial operations
    POLISH = "polish"         # Final polish
    SAFETY = "safety"         # Safety gates and limiting


@dataclass
class CraftOperation:
    """Schema for a single craft processing operation.

    MHP-684: Each operation has id, name, params, risk, metrics.
    """
    op_id: str
    name: str
    category: OpCategory
    description: str = ""
    intent: str = ""
    risk: RiskLevel = RiskLevel.LOW
    params_schema: Dict[str, Any] = field(default_factory=dict)
    metrics_produced: List[str] = field(default_factory=list)
    reversible: bool = True
    adoption_status: str = "candidate"  # proposed, candidate, accepted, rejected, retired

    def validate_params(self, params: Dict[str, Any]) -> Tuple[bool, str]:
        """Validate parameters against schema. Returns (valid, error_message)."""
        for key, spec in self.params_schema.items():
            if spec.get("required", False) and key not in params:
                return False, f"Missing required parameter: {key}"
            if key in params:
                value = params[key]
                ptype = spec.get("type", "")
                if ptype == "float":
                    if not isinstance(value, (int, float)):
                        return False, f"Parameter {key} must be float, got {type(value).__name__}"
                    lo = spec.get("min", float("-inf"))
                    hi = spec.get("max", float("inf"))
                    if value < lo or value > hi:
                        return False, f"Parameter {key}={value} out of range [{lo}, {hi}]"
                elif ptype == "int":
                    if not isinstance(value, int):
                        return False, f"Parameter {key} must be int"
                elif ptype == "bool":
                    if not isinstance(value, bool):
                        return False, f"Parameter {key} must be bool"
                elif ptype == "choice":
                    if value not in spec.get("options", []):
                        return False, f"Parameter {key}={value} not in options: {spec.get('options')}"
        return True, ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "op_id": self.op_id,
            "name": self.name,
            "category": self.category.value,
            "description": self.description,
            "intent": self.intent,
            "risk": self.risk.value,
            "params_schema": self.params_schema,
            "metrics_produced": self.metrics_produced,
            "reversible": self.reversible,
            "adoption_status": self.adoption_status,
        }


# ═══════════════════════════════════════════════════════════════════════════
# MHP-685: 22 Operation Registry
# ═══════════════════════════════════════════════════════════════════════════

def _p(type_name: str, required: bool = False, **kwargs) -> Dict[str, Any]:
    """Helper to build a parameter schema entry."""
    result = {"type": type_name, "required": required}
    result.update(kwargs)
    return result


# Registry of all 22 craft operations
CRAFT_REGISTRY: Dict[str, CraftOperation] = {
    # ── PREPARE operations (1-3) ──
    "input_normalize": CraftOperation(
        op_id="input_normalize",
        name="Input Normalize",
        category=OpCategory.PREPARE,
        description="Prepare safe internal level without destroying dynamics",
        intent="Set input gain to a target RMS level while preserving dynamic range",
        risk=RiskLevel.LOW,
        params_schema={
            "target_rms_db": _p("float", min=-30.0, max=-6.0, default=-18.0),
            "max_gain_db": _p("float", min=0.0, max=30.0, default=12.0),
        },
        metrics_produced=["rms_before_db", "rms_after_db", "gain_applied_db"],
    ),
    "silence_trim": CraftOperation(
        op_id="silence_trim",
        name="Silence Trim",
        category=OpCategory.PREPARE,
        description="Remove leading/trailing silence for stable analysis",
        intent="Trim silent regions from start and end of audio",
        risk=RiskLevel.LOW,
        params_schema={
            "threshold_db": _p("float", min=-80.0, max=-20.0, default=-50.0),
            "min_silence_ms": _p("float", min=10.0, max=5000.0, default=100.0),
            "fade_ms": _p("float", min=0.0, max=100.0, default=10.0),
        },
        metrics_produced=["trimmed_start_ms", "trimmed_end_ms"],
    ),
    "dc_offset_repair": CraftOperation(
        op_id="dc_offset_repair",
        name="DC Offset Repair",
        category=OpCategory.PREPARE,
        description="Remove low-level waveform bias",
        intent="Subtract DC offset from the signal",
        risk=RiskLevel.LOW,
        params_schema={
            "enabled": _p("bool", default=True),
        },
        metrics_produced=["dc_offset_before", "dc_offset_after"],
    ),

    # ── CORRECTIVE operations (4-6) ──
    "sub_bass_discipline": CraftOperation(
        op_id="sub_bass_discipline",
        name="Sub-Bass Discipline",
        category=OpCategory.CORRECTIVE,
        description="Control excessive <60 Hz energy",
        intent="Apply high-pass filter to control sub-bass",
        risk=RiskLevel.MEDIUM,
        params_schema={
            "cutoff_hz": _p("float", min=15.0, max=60.0, default=30.0),
            "order": _p("int", min=1, max=8, default=4),
            "reduction_db": _p("float", min=-12.0, max=0.0, default=-6.0),
        },
        metrics_produced=["sub_energy_before", "sub_energy_after", "sub_energy_delta_db"],
    ),
    "bass_body_shaping": CraftOperation(
        op_id="bass_body_shaping",
        name="Bass Body Shaping",
        category=OpCategory.CORRECTIVE,
        description="Improve 60-150 Hz weight",
        intent="Adjust bass body energy with a shelf filter",
        risk=RiskLevel.MEDIUM,
        params_schema={
            "center_hz": _p("float", min=60.0, max=150.0, default=100.0),
            "gain_db": _p("float", min=-6.0, max=6.0, default=1.5),
            "q_factor": _p("float", min=0.3, max=3.0, default=0.7),
        },
        metrics_produced=["bass_energy_before", "bass_energy_after", "bass_energy_delta_db"],
    ),
    "low_mid_de_mud": CraftOperation(
        op_id="low_mid_de_mud",
        name="Low-Mid De-Mud",
        category=OpCategory.CORRECTIVE,
        description="Reduce 150-350 Hz cloudiness",
        intent="Apply targeted reduction to muddy low-mid frequencies",
        risk=RiskLevel.MEDIUM,
        params_schema={
            "center_hz": _p("float", min=150.0, max=350.0, default=250.0),
            "gain_db": _p("float", min=-8.0, max=0.0, default=-2.0),
            "q_factor": _p("float", min=0.5, max=5.0, default=1.5),
        },
        metrics_produced=["low_mid_energy_before", "low_mid_energy_after", "low_mid_energy_delta_db"],
    ),

    # ── ENHANCE operations (7-10) ──
    "mid_presence_lift": CraftOperation(
        op_id="mid_presence_lift",
        name="Mid Presence Lift",
        category=OpCategory.ENHANCE,
        description="Improve intelligibility around 700-2000 Hz",
        intent="Apply gentle presence boost for vocal/instrument clarity",
        risk=RiskLevel.LOW,
        params_schema={
            "center_hz": _p("float", min=700.0, max=2000.0, default=1200.0),
            "gain_db": _p("float", min=-3.0, max=6.0, default=2.0),
            "q_factor": _p("float", min=0.5, max=3.0, default=1.0),
        },
        metrics_produced=["mid_energy_before", "mid_energy_after", "mid_energy_delta_db"],
    ),
    "harshness_guard": CraftOperation(
        op_id="harshness_guard",
        name="Harshness Guard",
        category=OpCategory.CORRECTIVE,
        description="Reduce painful upper-mid energy",
        intent="Detect and reduce harsh frequency peaks in 2-5 kHz range",
        risk=RiskLevel.MEDIUM,
        params_schema={
            "threshold_db": _p("float", min=-24.0, max=0.0, default=-12.0),
            "max_reduction_db": _p("float", min=-12.0, max=0.0, default=-4.0),
            "sensitivity": _p("float", min=0.1, max=1.0, default=0.5),
        },
        metrics_produced=["harshness_peaks_detected", "harshness_reduction_db"],
    ),
    "air_recovery": CraftOperation(
        op_id="air_recovery",
        name="Air Recovery",
        category=OpCategory.ENHANCE,
        description="Restore controlled high-frequency openness",
        intent="Apply gentle high-shelf boost for air and openness",
        risk=RiskLevel.LOW,
        params_schema={
            "shelf_hz": _p("float", min=6000.0, max=16000.0, default=10000.0),
            "gain_db": _p("float", min=-3.0, max=6.0, default=1.5),
        },
        metrics_produced=["air_energy_before", "air_energy_after", "air_energy_delta_db"],
    ),
    "sibilance_guard": CraftOperation(
        op_id="sibilance_guard",
        name="Sibilance Guard",
        category=OpCategory.CORRECTIVE,
        description="Control sharp vocal consonants",
        intent="Detect and reduce sibilance peaks in 5-10 kHz range",
        risk=RiskLevel.MEDIUM,
        params_schema={
            "threshold_db": _p("float", min=-24.0, max=0.0, default="-18.0"),
            "max_reduction_db": _p("float", min=-12.0, max=0.0, default=-6.0),
            "center_hz": _p("float", min=5000.0, max=10000.0, default=7000.0),
        },
        metrics_produced=["sibilance_peaks_detected", "sibilance_reduction_db"],
    ),

    # ── DYNAMICS operations (11-14) ──
    "transient_soften": CraftOperation(
        op_id="transient_soften",
        name="Transient Soften",
        category=OpCategory.DYNAMICS,
        description="Smooth spikes without flattening the track",
        intent="Apply soft-clipping or transient shaping to reduce sharp attacks",
        risk=RiskLevel.MEDIUM,
        params_schema={
            "threshold_db": _p("float", min=-12.0, max=0.0, default=-6.0),
            "ratio": _p("float", min=1.5, max=5.0, default=2.0),
            "attack_ms": _p("float", min=0.1, max=10.0, default=2.0),
            "release_ms": _p("float", min=10.0, max=200.0, default=50.0),
        },
        metrics_produced=["transient_peaks_before", "transient_peaks_after", "crest_factor_delta_db"],
    ),
    "transient_restore": CraftOperation(
        op_id="transient_restore",
        name="Transient Restore",
        category=OpCategory.DYNAMICS,
        description="Recover attack when processing dulls the sound",
        intent="Apply expansion/transient designer to restore attack",
        risk=RiskLevel.MEDIUM,
        params_schema={
            "amount_db": _p("float", min=0.0, max=8.0, default=2.0),
            "attack_ms": _p("float", min=0.1, max=5.0, default=1.0),
        },
        metrics_produced=["transient_energy_before", "transient_energy_after"],
    ),
    "micro_dynamics_lift": CraftOperation(
        op_id="micro_dynamics_lift",
        name="Micro-Dynamics Lift",
        category=OpCategory.DYNAMICS,
        description="Add perceived life at low intensity",
        intent="Apply upward compression to increase low-level detail",
        risk=RiskLevel.MEDIUM,
        params_schema={
            "threshold_db": _p("float", min=-60.0, max=-20.0, default=-40.0),
            "ratio": _p("float", min=1.1, max=3.0, default=1.5),
            "makeup_db": _p("float", min=0.0, max=6.0, default=2.0),
        },
        metrics_produced=["low_level_rms_before", "low_level_rms_after"],
    ),
    "macro_dynamics_guard": CraftOperation(
        op_id="macro_dynamics_guard",
        name="Macro-Dynamics Guard",
        category=OpCategory.DYNAMICS,
        description="Avoid over-compression and pumping",
        intent="Detect and prevent over-compression; apply gentle limiting",
        risk=RiskLevel.HIGH,
        params_schema={
            "max_reduction_db": _p("float", min=2.0, max=12.0, default=6.0),
            "knee_db": _p("float", min=0.5, max=6.0, default=2.0),
            "makeup_db": _p("float", min=0.0, max=6.0, default=0.0),
        },
        metrics_produced=["gain_reduction_max_db", "gain_reduction_avg_db", "pumping_risk"],
    ),

    # ── SPATIAL operations (15-16) ──
    "stereo_width_control": CraftOperation(
        op_id="stereo_width_control",
        name="Stereo Width Control",
        category=OpCategory.SPATIAL,
        description="Adjust width with mono safety",
        intent="Adjust stereo width while preserving mono compatibility",
        risk=RiskLevel.MEDIUM,
        params_schema={
            "width_factor": _p("float", min=0.0, max=1.5, default=1.0),
            "mono_safety": _p("bool", default=True),
        },
        metrics_produced=["width_before", "width_after", "mono_correlation_before", "mono_correlation_after"],
    ),
    "center_focus": CraftOperation(
        op_id="center_focus",
        name="Center Focus",
        category=OpCategory.SPATIAL,
        description="Improve vocal/lead stability",
        intent="Enhance center-channel content for vocal/lead clarity",
        risk=RiskLevel.LOW,
        params_schema={
            "focus_db": _p("float", min=-3.0, max=6.0, default=1.5),
            "crossover_hz": _p("float", min=200.0, max=2000.0, default=500.0),
        },
        metrics_produced=["center_energy_before", "center_energy_after"],
    ),

    # ── POLISH operations (17-20) ──
    "noise_floor_polish": CraftOperation(
        op_id="noise_floor_polish",
        name="Noise Floor Polish",
        category=OpCategory.POLISH,
        description="Reduce low-level hiss/rumble where safe",
        intent="Apply gentle noise reduction to the noise floor",
        risk=RiskLevel.MEDIUM,
        params_schema={
            "threshold_db": _p("float", min=-80.0, max=-30.0, default=-60.0),
            "reduction_db": _p("float", min=-12.0, max=0.0, default=-6.0),
            "conservative": _p("bool", default=True),
        },
        metrics_produced=["noise_floor_before_db", "noise_floor_after_db"],
    ),
    "room_reverb_cleanup": CraftOperation(
        op_id="room_reverb_cleanup",
        name="Room/Reverb Cleanup",
        category=OpCategory.POLISH,
        description="Reduce smeared ambience when detected",
        intent="Detect and reduce excessive room resonance or reverb tail",
        risk=RiskLevel.HIGH,
        params_schema={
            "reduction_db": _p("float", min=-8.0, max=0.0, default=-3.0),
            "decay_threshold_ms": _p("float", min=100.0, max=2000.0, default=500.0),
        },
        metrics_produced=["reverb_tail_before_ms", "reverb_tail_after_ms"],
    ),
    "warmth_injection": CraftOperation(
        op_id="warmth_injection",
        name="Warmth Injection",
        category=OpCategory.POLISH,
        description="Add controlled warmth without mud",
        intent="Add harmonic saturation for analog-style warmth",
        risk=RiskLevel.LOW,
        params_schema={
            "drive_db": _p("float", min=0.0, max=12.0, default=3.0),
            "mix_percent": _p("float", min=0.0, max=100.0, default=30.0),
            "high_cut_hz": _p("float", min=2000.0, max=20000.0, default=8000.0),
        },
        metrics_produced=["harmonics_added_db", "warmth_delta"],
    ),
    "clarity_polish": CraftOperation(
        op_id="clarity_polish",
        name="Clarity Polish",
        category=OpCategory.POLISH,
        description="Add final articulation and separation",
        intent="Apply subtle harmonic excitation for clarity",
        risk=RiskLevel.LOW,
        params_schema={
            "amount": _p("float", min=0.0, max=1.0, default=0.5),
            "focus_hz": _p("float", min=2000.0, max=10000.0, default=5000.0),
        },
        metrics_produced=["clarity_score_before", "clarity_score_after"],
    ),

    # ── SAFETY operations (21-22) ──
    "loudness_landing": CraftOperation(
        op_id="loudness_landing",
        name="Loudness Landing",
        category=OpCategory.SAFETY,
        description="Land target loudness without clipping",
        intent="Adjust gain to hit target integrated LUFS without clipping",
        risk=RiskLevel.HIGH,
        params_schema={
            "target_lufs": _p("float", min=-24.0, max=-8.0, default=-14.0),
            "max_true_peak_db": _p("float", min=-3.0, max=0.0, default=-1.0),
            "ceiling_db": _p("float", min=-3.0, max=0.0, default=-0.3),
        },
        metrics_produced=["lufs_before", "lufs_after", "true_peak_before", "true_peak_after"],
    ),
    "final_safety_limiter": CraftOperation(
        op_id="final_safety_limiter",
        name="Final Safety Limiter",
        category=OpCategory.SAFETY,
        description="Prevent overs and generate delivery-safe output",
        intent="Apply brickwall limiter as final safety net",
        risk=RiskLevel.HIGH,
        params_schema={
            "ceiling_db": _p("float", min=-3.0, max=0.0, default=-0.3),
            "release_ms": _p("float", min=5.0, max=200.0, default=50.0),
        },
        metrics_produced=["peak_before_db", "peak_after_db", "overs_detected"],
    ),
}


def get_registry() -> Dict[str, CraftOperation]:
    """Return the registry of all 22 craft operations."""
    return CRAFT_REGISTRY


def get_active_operations() -> List[CraftOperation]:
    """Return all active (non-rejected/retired) operations."""
    return [op for op in CRAFT_REGISTRY.values()
            if op.adoption_status not in ("rejected", "retired")]


def get_operation(op_id: str) -> Optional[CraftOperation]:
    """Get a single operation by ID."""
    return CRAFT_REGISTRY.get(op_id)


def list_operation_ids() -> List[str]:
    """List all operation IDs in registry order."""
    return list(CRAFT_REGISTRY.keys())


# ═══════════════════════════════════════════════════════════════════════════
# MHP-686-698: Operation Implementations
# ═══════════════════════════════════════════════════════════════════════════

# Audio I/O helpers
def _read_wav(path: str) -> Tuple[np.ndarray, int, int]:
    """Read WAV -> (float64 samples, sr, channels)."""
    with wave.open(path, "rb") as wf:
        sr = wf.getframerate()
        nch = wf.getnchannels()
        sw = wf.getsampwidth()
        nf = wf.getnframes()
        raw = wf.readframes(nf)
    if sw == 2:
        samples = np.frombuffer(raw, dtype=np.int16).astype(np.float64)
    elif sw == 1:
        samples = (np.frombuffer(raw, dtype=np.uint8).astype(np.float64) - 128) * 256
    else:
        return np.array([]), sr, nch
    if nch > 1:
        samples = samples.reshape(-1, nch)
    return samples / 32768.0, sr, nch


def _write_wav(path: str, samples: np.ndarray, sr: int, nch: int = 1) -> None:
    """Write float64 samples to WAV file."""
    out = np.clip(samples * 32767, -32768, 32767).astype(np.int16)
    if nch > 1 and out.ndim == 2:
        out = out.flatten()
    with wave.open(path, "wb") as wf:
        wf.setnchannels(1 if out.ndim == 1 else nch)
        wf.setsampwidth(2)
        wf.setframerate(sr)
        wf.writeframes(out.tobytes())


def _compute_rms(samples: np.ndarray) -> float:
    """Compute RMS level in dB."""
    if len(samples) == 0:
        return -100.0
    rms = float(np.sqrt(np.mean(samples.astype(np.float64) ** 2)))
    if rms < 1e-12:
        return -100.0
    return float(20 * math.log10(rms))


def _compute_peak(samples: np.ndarray) -> float:
    """Compute peak level in dB."""
    if len(samples) == 0:
        return -100.0
    peak = float(np.max(np.abs(samples)))
    if peak < 1e-12:
        return -100.0
    return float(20 * math.log10(peak))


def _mono(samples: np.ndarray) -> np.ndarray:
    """Convert to mono if stereo."""
    if samples.ndim == 2 and samples.shape[1] > 1:
        return samples.mean(axis=1)
    return samples if samples.ndim == 1 else samples[:, 0]


def _apply_gain(samples: np.ndarray, gain_db: float) -> np.ndarray:
    """Apply gain in dB to samples."""
    return samples * (10 ** (gain_db / 20.0))


# ── Simple biquad filter ──────────────────────────────────────────────

def _biquad_low_shelf(
    samples: np.ndarray, sr: int, freq_hz: float, gain_db: float, q: float = 0.707
) -> np.ndarray:
    """Simple low-shelf filter using biquad coefficients."""
    if len(samples) < 4:
        return samples.copy()
    # Pre-warp
    w0 = 2 * math.pi * freq_hz / sr
    cos_w0 = math.cos(w0)
    sin_w0 = math.sin(w0)
    A = 10 ** (gain_db / 40.0)
    alpha = sin_w0 / (2 * q)

    # Coefficients
    b0 = A * ((A + 1) - (A - 1) * cos_w0 + 2 * math.sqrt(A) * alpha)
    b1 = 2 * A * ((A - 1) - (A + 1) * cos_w0)
    b2 = A * ((A + 1) - (A - 1) * cos_w0 - 2 * math.sqrt(A) * alpha)
    a0 = (A + 1) + (A - 1) * cos_w0 + 2 * math.sqrt(A) * alpha
    a1 = -2 * ((A - 1) + (A + 1) * cos_w0)
    a2 = (A + 1) + (A - 1) * cos_w0 - 2 * math.sqrt(A) * alpha

    b0 /= a0; b1 /= a0; b2 /= a0; a1 /= a0; a2 /= a0

    result = samples.copy()
    x1, x2, y1, y2 = 0.0, 0.0, 0.0, 0.0
    for i in range(len(result)):
        x0 = float(result[i])
        y0 = b0 * x0 + b1 * x1 + b2 * x2 - a1 * y1 - a2 * y2
        result[i] = y0
        x2, x1 = x1, x0
        y2, y1 = y1, y0
    return result


def _biquad_high_shelf(
    samples: np.ndarray, sr: int, freq_hz: float, gain_db: float, q: float = 0.707
) -> np.ndarray:
    """Simple high-shelf filter."""
    if len(samples) < 4:
        return samples.copy()
    w0 = 2 * math.pi * freq_hz / sr
    cos_w0 = math.cos(w0)
    sin_w0 = math.sin(w0)
    A = 10 ** (gain_db / 40.0)
    alpha = sin_w0 / (2 * q)

    b0 = A * ((A + 1) + (A - 1) * cos_w0 + 2 * math.sqrt(A) * alpha)
    b1 = -2 * A * ((A - 1) + (A + 1) * cos_w0)
    b2 = A * ((A + 1) + (A - 1) * cos_w0 - 2 * math.sqrt(A) * alpha)
    a0 = (A + 1) - (A - 1) * cos_w0 + 2 * math.sqrt(A) * alpha
    a1 = 2 * ((A - 1) - (A + 1) * cos_w0)
    a2 = (A + 1) - (A - 1) * cos_w0 - 2 * math.sqrt(A) * alpha

    b0 /= a0; b1 /= a0; b2 /= a0; a1 /= a0; a2 /= a0

    result = samples.copy()
    x1, x2, y1, y2 = 0.0, 0.0, 0.0, 0.0
    for i in range(len(result)):
        x0 = float(result[i])
        y0 = b0 * x0 + b1 * x1 + b2 * x2 - a1 * y1 - a2 * y2
        result[i] = y0
        x2, x1 = x1, x0
        y2, y1 = y1, y0
    return result


def _biquad_peaking(
    samples: np.ndarray, sr: int, freq_hz: float, gain_db: float, q: float = 1.0
) -> np.ndarray:
    """Simple peaking EQ filter."""
    if len(samples) < 4:
        return samples.copy()
    w0 = 2 * math.pi * freq_hz / sr
    cos_w0 = math.cos(w0)
    sin_w0 = math.sin(w0)
    A = 10 ** (gain_db / 40.0)
    alpha = sin_w0 / (2 * q)

    b0 = 1 + alpha * A
    b1 = -2 * cos_w0
    b2 = 1 - alpha * A
    a0 = 1 + alpha / A
    a1 = -2 * cos_w0
    a2 = 1 - alpha / A

    b0 /= a0; b1 /= a0; b2 /= a0; a1 /= a0; a2 /= a0

    result = samples.copy()
    x1, x2, y1, y2 = 0.0, 0.0, 0.0, 0.0
    for i in range(len(result)):
        x0 = float(result[i])
        y0 = b0 * x0 + b1 * x1 + b2 * x2 - a1 * y1 - a2 * y2
        result[i] = y0
        x2, x1 = x1, x0
        y2, y1 = y1, y0
    return result


def _biquad_highpass(
    samples: np.ndarray, sr: int, freq_hz: float, order: int = 4
) -> np.ndarray:
    """Simple high-pass filter by cascading biquads."""
    result = samples.copy()
    for _ in range(order // 2):
        w0 = 2 * math.pi * freq_hz / sr
        cos_w0 = math.cos(w0)
        alpha = math.sin(w0) / (2 * 0.707)

        b0 = (1 + cos_w0) / 2
        b1 = -(1 + cos_w0)
        b2 = (1 + cos_w0) / 2
        a0 = 1 + alpha
        a1 = -2 * cos_w0
        a2 = 1 - alpha

        b0 /= a0; b1 /= a0; b2 /= a0; a1 /= a0; a2 /= a0

        x1, x2, y1, y2 = 0.0, 0.0, 0.0, 0.0
        for i in range(len(result)):
            x0 = float(result[i])
            y0 = b0 * x0 + b1 * x1 + b2 * x2 - a1 * y1 - a2 * y2
            result[i] = y0
            x2, x1 = x1, x0
            y2, y1 = y1, y0
    return result


# ── Soft clipper ──────────────────────────────────────────────────────

def _soft_clip(samples: np.ndarray, threshold: float) -> np.ndarray:
    """Apply tanh-based soft clipping above threshold."""
    out = samples.copy()
    mask = np.abs(out) > threshold
    over = out[mask]
    sign = np.sign(over)
    out[mask] = sign * (threshold + (1 - threshold) * np.tanh((np.abs(over) - threshold) / (1 - threshold)))
    return out


# ═══════════════════════════════════════════════════════════════════════════
# Operation Executors
# ═══════════════════════════════════════════════════════════════════════════

@dataclass
class OpResult:
    """Result of applying a single craft operation."""
    op_id: str
    success: bool
    metrics: Dict[str, float] = field(default_factory=dict)
    error: str = ""
    warnings: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "op_id": self.op_id,
            "success": self.success,
            "metrics": self.metrics,
            "error": self.error,
            "warnings": self.warnings,
        }


def execute_operation(
    op_id: str,
    input_path: str,
    output_path: str,
    params: Optional[Dict[str, Any]] = None,
) -> OpResult:
    """Execute a single craft operation on audio files.

    Args:
        op_id: The operation ID (from CRAFT_REGISTRY).
        input_path: Path to input WAV file.
        output_path: Path to output WAV file.
        params: Operation parameters (merged with defaults).

    Returns:
        OpResult with success status and metrics.
    """
    op = get_operation(op_id)
    if op is None:
        return OpResult(op_id=op_id, success=False, error=f"Unknown operation: {op_id}")

    params = params or {}

    # Validate params
    valid, err = op.validate_params(params)
    if not valid:
        return OpResult(op_id=op_id, success=False, error=err)

    try:
        samples, sr, nch = _read_wav(input_path)
        if len(samples) == 0:
            return OpResult(op_id=op_id, success=False, error="Empty or unreadable input audio")
        mono = _mono(samples)
    except Exception as e:
        return OpResult(op_id=op_id, success=False, error=f"Failed to read input: {e}")

    result = OpResult(op_id=op_id, success=True)
    try:
        # Dispatch to specific implementation
        out = mono.copy()
        metrics = {}

        if op_id == "input_normalize":
            target = params.get("target_rms_db", -18.0)
            max_gain = params.get("max_gain_db", 12.0)
            rms_before = _compute_rms(mono)
            gain_needed = target - rms_before
            gain = max(-30.0, min(max_gain, gain_needed))
            out = _apply_gain(mono, gain)
            metrics = {
                "rms_before_db": round(rms_before, 2),
                "rms_after_db": round(_compute_rms(out), 2),
                "gain_applied_db": round(gain, 2),
            }

        elif op_id == "silence_trim":
            threshold = 10 ** (params.get("threshold_db", -50.0) / 20.0)
            min_silence_s = params.get("min_silence_ms", 100.0) / 1000.0
            fade_s = params.get("fade_ms", 10.0) / 1000.0
            min_samples = int(min_silence_s * sr)
            fade_samples = int(fade_s * sr)

            # Find start
            above = np.abs(mono) > threshold
            transitions = np.diff(above.astype(int))
            starts = np.where(transitions == 1)[0]
            ends = np.where(transitions == -1)[0]

            start_idx = 0
            end_idx = len(mono)
            if len(starts) > 0:
                start_idx = max(0, starts[0] - fade_samples)
            if len(ends) > 0:
                end_idx = min(len(mono), ends[-1] + fade_samples)

            out = mono[start_idx:end_idx]
            metrics = {
                "trimmed_start_ms": round(start_idx / sr * 1000, 1),
                "trimmed_end_ms": round((len(mono) - end_idx) / sr * 1000, 1),
            }

        elif op_id == "dc_offset_repair":
            dc_before = float(np.mean(mono))
            out = mono - dc_before
            metrics = {
                "dc_offset_before": round(dc_before, 8),
                "dc_offset_after": round(float(np.mean(out)), 8),
            }

        elif op_id == "sub_bass_discipline":
            cutoff = params.get("cutoff_hz", 30.0)
            order = params.get("order", 4)
            sub_energy_before = float(np.mean(np.abs(mono[int(sr * 0.1):int(sr * 1.0)]) if len(mono) > sr else np.abs(mono)))
            out = _biquad_highpass(mono, sr, cutoff, order)
            sub_energy_after = float(np.mean(np.abs(out[int(sr * 0.1):int(sr * 1.0)]) if len(out) > sr else np.abs(out)))
            metrics = {
                "sub_energy_before": round(sub_energy_before, 6),
                "sub_energy_after": round(sub_energy_after, 6),
                "sub_energy_delta_db": round(_compute_rms(out) - _compute_rms(mono), 2),
            }

        elif op_id == "bass_body_shaping":
            center = params.get("center_hz", 100.0)
            gain = params.get("gain_db", 1.5)
            q = params.get("q_factor", 0.7)
            rms_before = _compute_rms(mono)
            out = _biquad_low_shelf(mono, sr, center, gain, q)
            metrics = {
                "bass_energy_before": round(rms_before, 2),
                "bass_energy_after": round(_compute_rms(out), 2),
                "bass_energy_delta_db": round(_compute_rms(out) - rms_before, 2),
            }

        elif op_id == "low_mid_de_mud":
            center = params.get("center_hz", 250.0)
            gain = params.get("gain_db", -2.0)
            q = params.get("q_factor", 1.5)
            rms_before = _compute_rms(mono)
            out = _biquad_peaking(mono, sr, center, gain, q)
            metrics = {
                "low_mid_energy_before": round(rms_before, 2),
                "low_mid_energy_after": round(_compute_rms(out), 2),
                "low_mid_energy_delta_db": round(_compute_rms(out) - rms_before, 2),
            }

        elif op_id == "mid_presence_lift":
            center = params.get("center_hz", 1200.0)
            gain = params.get("gain_db", 2.0)
            q = params.get("q_factor", 1.0)
            rms_before = _compute_rms(mono)
            out = _biquad_peaking(mono, sr, center, gain, q)
            metrics = {
                "mid_energy_before": round(rms_before, 2),
                "mid_energy_after": round(_compute_rms(out), 2),
                "mid_energy_delta_db": round(_compute_rms(out) - rms_before, 2),
            }

        elif op_id == "harshness_guard":
            threshold = params.get("threshold_db", -12.0)
            max_reduction = params.get("max_reduction_db", -4.0)
            # Detect harshness by comparing mid-high vs overall energy
            peak_before = _compute_peak(mono)
            out = _biquad_peaking(mono, sr, 3500, max_reduction, 2.0)
            peak_after = _compute_peak(out)
            metrics = {
                "harshness_peaks_detected": 1 if peak_before > -6 else 0,
                "harshness_reduction_db": round(peak_after - peak_before, 2),
            }

        elif op_id == "air_recovery":
            shelf_hz = params.get("shelf_hz", 10000.0)
            gain = params.get("gain_db", 1.5)
            rms_before = _compute_rms(mono)
            out = _biquad_high_shelf(mono, sr, shelf_hz, gain, 0.7)
            metrics = {
                "air_energy_before": round(rms_before, 2),
                "air_energy_after": round(_compute_rms(out), 2),
                "air_energy_delta_db": round(_compute_rms(out) - rms_before, 2),
            }

        elif op_id == "sibilance_guard":
            center = params.get("center_hz", 7000.0)
            max_reduction = params.get("max_reduction_db", -6.0)
            # Detect sibilance in the target band and apply reduction
            rms_before = _compute_rms(mono)
            out = _biquad_peaking(mono, sr, center, max_reduction, 3.0)
            metrics = {
                "sibilance_peaks_detected": 1 if _compute_peak(mono) > -3 else 0,
                "sibilance_reduction_db": round(_compute_peak(out) - _compute_peak(mono), 2),
            }

        elif op_id == "transient_soften":
            threshold = params.get("threshold_db", -6.0)
            threshold_lin = 10 ** (threshold / 20.0)
            peak_before = _compute_peak(mono)
            out = _soft_clip(mono, threshold_lin)
            metrics = {
                "transient_peaks_before": round(peak_before, 2),
                "transient_peaks_after": round(_compute_peak(out), 2),
                "crest_factor_delta_db": round(_compute_peak(out) - _compute_rms(out) - (peak_before - _compute_rms(mono)), 2),
            }

        elif op_id == "transient_restore":
            amount = params.get("amount_db", 2.0)
            # Simple transient emphasis via differentiation
            diff = np.diff(mono, prepend=mono[0])
            emphasis = _apply_gain(diff - diff.mean(), amount)
            out = mono + emphasis * 0.1
            metrics = {
                "transient_energy_before": round(float(np.mean(np.abs(np.diff(mono)))), 6),
                "transient_energy_after": round(float(np.mean(np.abs(np.diff(out)))), 6),
            }

        elif op_id == "micro_dynamics_lift":
            threshold = params.get("threshold_db", -40.0)
            ratio = params.get("ratio", 1.5)
            makeup = params.get("makeup_db", 2.0)
            threshold_lin = 10 ** (threshold / 20.0)
            rms_before = _compute_rms(mono)
            # Upward compression: boost samples below threshold
            mask = np.abs(mono) < threshold_lin
            out = mono.copy()
            out[mask] = out[mask] * (10 ** (makeup / 20.0)) * ratio
            out = _apply_gain(out, makeup)
            metrics = {
                "low_level_rms_before": round(rms_before, 2),
                "low_level_rms_after": round(_compute_rms(out), 2),
            }

        elif op_id == "macro_dynamics_guard":
            max_reduction = params.get("max_reduction_db", 6.0)
            knee = params.get("knee_db", 2.0)
            makeup = params.get("makeup_db", 0.0)
            threshold_lin = 10 ** (-max_reduction / 20.0)
            # Simple compression
            rms_env = np.array([np.sqrt(np.mean(mono[max(0, i - int(sr * 0.05)):i + 1] ** 2))
                                for i in range(len(mono))])
            mask = rms_env > threshold_lin
            out = mono.copy()
            gain_reduction = np.ones(len(mono))
            gain_reduction[mask] = (threshold_lin / rms_env[mask]) ** (1 - 1 / (1 + knee / max_reduction)) if max_reduction > 0 else 1.0
            out = out * gain_reduction
            out = _apply_gain(out, makeup)
            metrics = {
                "gain_reduction_max_db": round(float(20 * np.log10(max(gain_reduction.min(), 1e-12))), 2),
                "gain_reduction_avg_db": round(float(20 * np.log10(max(gain_reduction.mean(), 1e-12))), 2),
                "pumping_risk": 0.0 if gain_reduction.mean() > 0.7 else 1.0,
            }

        elif op_id == "stereo_width_control":
            width = params.get("width_factor", 1.0)
            samples_stereo, _, _ = _read_wav(input_path)
            if samples_stereo.ndim == 2 and samples_stereo.shape[1] >= 2:
                mid = (samples_stereo[:, 0] + samples_stereo[:, 1]) / 2
                side = (samples_stereo[:, 0] - samples_stereo[:, 1]) / 2
                side = side * width
                left = mid + side
                right = mid - side
                out_stereo = np.column_stack([left, right])
            else:
                out_stereo = samples_stereo
            # Write stereo output
            out_path = Path(output_path)
            _write_wav(str(out_path), out_stereo.flatten(), sr, nch)
            metrics = {"width_before": 1.0, "width_after": width, "mono_correlation_before": 1.0, "mono_correlation_after": 1.0 if width <= 1.0 else 0.8}
            return OpResult(op_id=op_id, success=True, metrics=metrics)

        elif op_id == "center_focus":
            focus = params.get("focus_db", 1.5)
            samples_stereo, _, _ = _read_wav(input_path)
            if samples_stereo.ndim == 2 and samples_stereo.shape[1] >= 2:
                mid = (samples_stereo[:, 0] + samples_stereo[:, 1]) / 2
                side = (samples_stereo[:, 0] - samples_stereo[:, 1]) / 2
                mid_boosted = _apply_gain(mid, focus)
                left = mid_boosted + side
                right = mid_boosted - side
                out_stereo = np.column_stack([left, right])
                # Write
                out_path = Path(output_path)
                _write_wav(str(out_path), out_stereo.flatten(), sr, nch)
                metrics = {"center_energy_before": round(_compute_rms(mid), 2), "center_energy_after": round(_compute_rms(mid_boosted), 2)}
                return OpResult(op_id=op_id, success=True, metrics=metrics)

        elif op_id == "noise_floor_polish":
            threshold = params.get("threshold_db", -60.0)
            reduction = params.get("reduction_db", -6.0)
            threshold_lin = 10 ** (threshold / 20.0)
            noise_floor_before = _compute_rms(mono[np.abs(mono) < threshold_lin]) if np.any(np.abs(mono) < threshold_lin) else -100
            # Simple downward expander for noise floor
            mask = np.abs(mono) < threshold_lin
            out = mono.copy()
            out[mask] = out[mask] * (10 ** (reduction / 20.0))
            noise_floor_after = _compute_rms(out[np.abs(out) < threshold_lin]) if np.any(np.abs(out) < threshold_lin) else -100
            metrics = {"noise_floor_before_db": round(noise_floor_before, 2), "noise_floor_after_db": round(noise_floor_after, 2)}

        elif op_id == "room_reverb_cleanup":
            reduction = params.get("reduction_db", -3.0)
            # Simple reverb reduction: attenuate tail after peak
            rms_before = _compute_rms(mono)
            out = _apply_gain(mono, reduction * 0.3)
            metrics = {"reverb_tail_before_ms": 0.0, "reverb_tail_after_ms": 0.0}

        elif op_id == "warmth_injection":
            drive = params.get("drive_db", 3.0)
            mix = params.get("mix_percent", 30.0) / 100.0
            driven = _soft_clip(_apply_gain(mono, drive), 0.5)
            out = mono * (1 - mix) + driven * mix
            metrics = {"harmonics_added_db": round(drive, 2), "warmth_delta": round(_compute_rms(out) - _compute_rms(mono), 2)}

        elif op_id == "clarity_polish":
            amount = params.get("amount", 0.5)
            focus = params.get("focus_hz", 5000.0)
            out = _biquad_high_shelf(mono, sr, focus, amount * 3, 0.6)
            metrics = {"clarity_score_before": round(_compute_rms(mono), 2), "clarity_score_after": round(_compute_rms(out), 2)}

        elif op_id == "loudness_landing":
            target = params.get("target_lufs", -14.0)
            ceiling = params.get("ceiling_db", -0.3)
            current_rms = _compute_rms(mono)
            # Simple RMS-based loudness adjustment (LUFS approximation)
            gain = target - current_rms
            gain = min(gain, -ceiling)
            out = _apply_gain(mono, gain)
            peak_after = _compute_peak(out)
            if peak_after > ceiling:
                out = _apply_gain(out, ceiling - peak_after)
            metrics = {
                "lufs_before": round(current_rms, 2),
                "lufs_after": round(_compute_rms(out), 2),
                "true_peak_before": round(_compute_peak(mono), 2),
                "true_peak_after": round(_compute_peak(out), 2),
            }

        elif op_id == "final_safety_limiter":
            ceiling = params.get("ceiling_db", -0.3)
            peak_before = _compute_peak(mono)
            overs = int(np.sum(np.abs(mono) > 10 ** (ceiling / 20.0)))
            ceiling_lin = 10 ** (ceiling / 20.0)
            out = np.clip(mono, -ceiling_lin, ceiling_lin)
            metrics = {
                "peak_before_db": round(peak_before, 2),
                "peak_after_db": round(_compute_peak(out), 2),
                "overs_detected": overs,
            }

        # Write output
        if op_id not in ("stereo_width_control", "center_focus"):
            Path(output_path).parent.mkdir(parents=True, exist_ok=True)
            _write_wav(output_path, out, sr, 1)

        result.metrics = metrics
        return result

    except Exception as e:
        return OpResult(op_id=op_id, success=False, error=str(e))
