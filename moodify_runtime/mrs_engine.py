"""MHP-084: MRS Scoring Engine — unified entry point.

Combines pseudo-MRS, MRS Open v0.3.1, and graduated over-dark detection
into a single score_audio() call. Genre-specific thresholds are applied
automatically from configs/mrs_thresholds.yaml.

Usage:
    from moodify_runtime.mrs_engine import score_audio
    result = score_audio("original.wav", "processed.wav", genre="piano")
    print(result.mrs_score, result.gate_decision)
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

from .metrics import (
    analyze_wav_stdlib,
    pseudo_mrs,
    compute_mrs_open_v031,
)
from .over_dark import detect_over_dark, OverDarkResult
from .operator_console import decide_candidate_gate


@dataclass
class MRSScoreResult:
    """Unified MRS scoring result for a before/after audio pair."""
    sample_id: str = ""
    genre: str = ""
    preset: str = ""

    # Pseudo-MRS
    pseudo_mrs_before: Optional[float] = None
    pseudo_mrs_after: Optional[float] = None
    pseudo_mrs_delta: Optional[float] = None

    # MRS Open v0.3.1
    mrs_open_before: Optional[float] = None
    mrs_open_after: Optional[float] = None
    mrs_open_delta: Optional[float] = None
    mrs_open_available: bool = False
    mrs_open_error: Optional[str] = None

    # Over-dark
    over_dark_level: str = "none"
    over_dark_score: float = 0.0
    over_dark_affected_bands: List[str] = field(default_factory=list)
    over_dark_recommendation: str = "pass"

    # Gate
    gate_decision: str = ""
    gate_reasons: List[str] = field(default_factory=list)
    gate_required_mrs_delta: float = 0.0

    # Metadata
    before_metrics: Dict[str, Any] = field(default_factory=dict)
    after_metrics: Dict[str, Any] = field(default_factory=dict)
    error: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @property
    def mrs_delta_for_gate(self) -> Optional[float]:
        """Best available MRS delta for gate decisions."""
        if self.mrs_open_delta is not None:
            return self.mrs_open_delta
        return self.pseudo_mrs_delta


def score_audio(
    before_path: str,
    after_path: str,
    genre: str = "",
    preset: str = "",
    sample_id: str = "",
) -> MRSScoreResult:
    """Score processed audio against its original.

    This is the single entry point for all MRS scoring. It:
    1. Analyzes before/after WAV files
    2. Computes pseudo-MRS (calibrated weights)
    3. Computes MRS Open v0.3.1 (when available)
    4. Runs graduated over-dark detection
    5. Applies genre-specific gate thresholds
    6. Returns a unified MRSScoreResult

    Args:
        before_path: Path to the original (pre-processing) audio file.
        after_path: Path to the processed audio file.
        genre: Genre hint for per-genre thresholds (e.g. "piano").
        preset: DSP preset name for metadata.
        sample_id: Optional sample identifier.

    Returns:
        MRSScoreResult with all scores and gate decision.
    """
    result = MRSScoreResult(
        sample_id=sample_id,
        genre=genre,
        preset=preset,
    )

    # ── 1. Analyze WAV files ──
    try:
        before_metrics = analyze_wav_stdlib(Path(before_path))
        result.before_metrics = before_metrics
    except Exception as e:
        result.error = f"before_analysis_failed: {e}"
        return result

    after_path_obj = Path(after_path)
    if after_path_obj.exists():
        try:
            after_metrics = analyze_wav_stdlib(after_path_obj)
            result.after_metrics = after_metrics
        except Exception as e:
            result.error = f"after_analysis_failed: {e}"
            return result
    else:
        result.error = f"after_file_not_found: {after_path}"
        return result

    # ── 2. Pseudo-MRS ──
    result.pseudo_mrs_before = pseudo_mrs(before_metrics)
    result.pseudo_mrs_after = pseudo_mrs(after_metrics)
    if result.pseudo_mrs_before is not None and result.pseudo_mrs_after is not None:
        result.pseudo_mrs_delta = result.pseudo_mrs_after - result.pseudo_mrs_before

    # ── 3. MRS Open v0.3.1 ──
    mrs_before = compute_mrs_open_v031(before_path)
    result.mrs_open_available = mrs_before.get("error") is None
    result.mrs_open_error = mrs_before.get("error")
    result.mrs_open_before = mrs_before.get("mrs_open")

    mrs_after = compute_mrs_open_v031(after_path)
    result.mrs_open_after = mrs_after.get("mrs_open")
    if result.mrs_open_before is not None and result.mrs_open_after is not None:
        result.mrs_open_delta = result.mrs_open_after - result.mrs_open_before

    # ── 4. Over-dark detection ──
    od = detect_over_dark(before_path, after_path, genre=genre)
    result.over_dark_level = od.level
    result.over_dark_score = od.score
    result.over_dark_affected_bands = od.affected_bands
    result.over_dark_recommendation = od.recommendation

    # ── 5. Gate decision ──
    mrs_delta = result.mrs_delta_for_gate
    runtime_success = result.error is None
    gate = decide_candidate_gate(
        candidate_id=f"{sample_id}_{preset}",
        job_id=f"engine_{sample_id}",
        runtime_success=runtime_success,
        mrs_score_delta=mrs_delta,
        over_dark_level=od.level,
        genre=genre,
    )
    result.gate_decision = gate["decision"]
    result.gate_reasons = gate["reasons"]
    result.gate_required_mrs_delta = gate["required_mrs_delta"]

    return result
