"""MHP-161/162/165: Preset Metadata Model, Safety Gate Engine, and Craft Record integration.

Build NEM for ECHAIN-MOODIFY-PRESET-CRAFT-002.
"""

from __future__ import annotations

import uuid
from dataclasses import asdict, dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

from .utils import utc_now_iso


# ═══════════════════════════════════════════════════════════════════════
# MHP-162: Preset Metadata Model
# ═══════════════════════════════════════════════════════════════════════


class PresetCategory(Enum):
    WARM_REALITY = "warm_reality"
    DYNAMIC_RECOVERY = "dynamic_recovery"
    SOFT_SPACE = "soft_space"
    ANTI_FATIGUE = "anti_fatigue"
    BYPASS = "bypass"


PRESET_CATEGORY_MAP: Dict[str, str] = {
    "warm_vocal": "warm_reality",
    "clean_master": "dynamic_recovery",
    "wide_space": "soft_space",
    "safe_air": "anti_fatigue",
    "clean_master_safe": "anti_fatigue",
    "air_preserve_master": "soft_space",
    "bypass_control": "bypass",
}

PRESET_ADOPTION_STATUSES = ("experimental", "candidate", "stable", "adopted", "deprecated")


@dataclass
class PresetMetadata:
    """Self-describing preset metadata for craft library."""
    preset_id: str
    name: str
    category: str
    description: str = ""
    version: str = "0.1.0"
    adoption_status: str = "experimental"
    parameters: Dict[str, Any] = field(default_factory=dict)
    safety_gate_results: Dict[str, Any] = field(default_factory=dict)
    known_good_genres: List[str] = field(default_factory=list)
    known_bad_genres: List[str] = field(default_factory=list)
    failure_cases: List[str] = field(default_factory=list)
    created_at: str = field(default_factory=utc_now_iso)
    updated_at: str = field(default_factory=utc_now_iso)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def load_preset_metadata(name: str) -> PresetMetadata:
    """Load preset metadata. Falls back to defaults for unknown presets."""
    category = PRESET_CATEGORY_MAP.get(name, "dynamic_recovery")
    return PresetMetadata(
        preset_id=f"PRST_{name}",
        name=name,
        category=category,
        description=f"Preset: {name} (category: {category})",
    )


# ═══════════════════════════════════════════════════════════════════════
# MHP-165: Preset Safety Gate Engine
# ═══════════════════════════════════════════════════════════════════════


@dataclass
class SafetyGateResult:
    passed: bool
    failures: List[Dict[str, Any]] = field(default_factory=list)
    warnings: List[Dict[str, Any]] = field(default_factory=list)
    gate_id: str = ""
    checked_at: str = field(default_factory=utc_now_iso)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def validate_preset_safety(
    preset_name: str,
    over_dark_level: str = "none",
    over_bright_level: str = "none",
    transient_damage_level: str = "none",
    vocal_thinning_level: str = "none",
    stereo_collapse_level: str = "none",
) -> SafetyGateResult:
    """Run all safety gate checks for a preset.

    A preset must pass ALL gates to be adopted.
    - CRITICAL gates (over_dark severe, over_bright severe) → hard fail
    - HIGH gates (transient severe, vocal thinning severe) → fail
    - MEDIUM gates (stereo collapse severe) → warning
    """
    failures: List[Dict[str, Any]] = []
    warnings: List[Dict[str, Any]] = []

    # ── CRITICAL ──
    if over_dark_level == "severe":
        failures.append({"gate": "over_dark", "level": "severe", "message": "Severe bass accumulation detected"})
    elif over_dark_level == "mild":
        warnings.append({"gate": "over_dark", "level": "mild", "message": "Mild bass accumulation — review before adopting"})

    if over_bright_level == "severe":
        failures.append({"gate": "over_bright", "level": "severe", "message": "Severe high-frequency boost detected"})
    elif over_bright_level == "mild":
        warnings.append({"gate": "over_bright", "level": "mild", "message": "Mild high-frequency boost — review before adopting"})

    # ── HIGH ──
    if transient_damage_level == "severe":
        failures.append({"gate": "transient_damage", "level": "severe", "message": "Transient damage detected"})

    if vocal_thinning_level == "severe":
        failures.append({"gate": "vocal_thinning", "level": "severe", "message": "Vocal thinning detected"})

    # ── MEDIUM ──
    if stereo_collapse_level == "severe":
        warnings.append({"gate": "stereo_collapse", "level": "severe", "message": "Stereo width collapsed — review if source is stereo"})

    return SafetyGateResult(
        passed=len(failures) == 0,
        failures=failures,
        warnings=warnings,
        gate_id=f"SG_{uuid.uuid4().hex[:8].upper()}",
    )


# ═══════════════════════════════════════════════════════════════════════
# MHP-163: Preset Experiment Runner
# ═══════════════════════════════════════════════════════════════════════


def run_preset_experiment(
    sample_path: str,
    preset_names: List[str],
    genre: str = "",
    output_dir: str = "",
) -> List[Dict[str, Any]]:
    """Process one audio sample through multiple presets for comparison.

    Returns a list of results, one per preset.
    """
    import subprocess
    import sys
    import tempfile
    from pathlib import Path

    results = []
    sample_id = Path(sample_path).stem

    for preset in preset_names:
        out_dir = (Path(output_dir) if output_dir else Path(tempfile.gettempdir()) / "craft_exp") / sample_id / preset
        out_dir.mkdir(parents=True, exist_ok=True)

        try:
            proc = subprocess.run(
                [sys.executable, "-m", "moodify.cli", "process", sample_path,
                 "--output-dir", str(out_dir), "--preset", preset],
                capture_output=True, text=True, timeout=120,
            )
            ok = proc.returncode == 0
        except subprocess.TimeoutExpired:
            ok = False
            proc = None

        # Compute metrics
        from .metrics import analyze_wav_stdlib, pseudo_mrs
        from .craft_probes import (
            detect_over_bright,
            detect_transient_damage,
            detect_vocal_thinning,
            detect_stereo_collapse,
        )
        from .over_dark import detect_over_dark

        before_metrics = analyze_wav_stdlib(Path(sample_path))
        after_wavs = sorted(out_dir.glob("*.wav")) if out_dir.exists() else []

        result = {
            "sample_id": sample_id,
            "preset": preset,
            "genre": genre,
            "status": "done" if ok else "failed",
            "pseudo_mrs_before": pseudo_mrs(before_metrics),
            "pseudo_mrs_after": 0.0,
            "pseudo_mrs_delta": 0.0,
        }

        if after_wavs:
            after_metrics = analyze_wav_stdlib(after_wavs[0])
            result["pseudo_mrs_after"] = pseudo_mrs(after_metrics)
            if result["pseudo_mrs_before"] and result["pseudo_mrs_after"]:
                result["pseudo_mrs_delta"] = result["pseudo_mrs_after"] - result["pseudo_mrs_before"]

            after_path = str(after_wavs[0])

            od = detect_over_dark(sample_path, after_path, genre=genre)
            result["over_dark"] = od.level

            ob = detect_over_bright(sample_path, after_path)
            result["over_bright"] = ob["level"]

            td = detect_transient_damage(sample_path, after_path)
            result["transient_damage"] = td["level"]

            vt = detect_vocal_thinning(sample_path, after_path)
            result["vocal_thinning"] = vt["level"]

            sc = detect_stereo_collapse(sample_path, after_path)
            result["stereo_collapse"] = sc["level"]

            gate = validate_preset_safety(
                preset,
                over_dark_level=od.level,
                over_bright_level=ob["level"],
                transient_damage_level=td["level"],
                vocal_thinning_level=vt["level"],
                stereo_collapse_level=sc["level"],
            )
            result["safety_gate"] = gate.to_dict()

        results.append(result)

    return results


# ═══════════════════════════════════════════════════════════════════════
# MHP-164: A/B Comparison Report Builder
# ═══════════════════════════════════════════════════════════════════════


def build_ab_comparison_report(
    experiment_results: List[Dict[str, Any]],
    output_path: str = "",
) -> Dict[str, Any]:
    """Build a markdown A/B comparison report from preset experiment results.

    Ranks presets by pseudo_mrs_delta within each sample.
    """
    from pathlib import Path

    # Group by sample
    by_sample: Dict[str, List[Dict]] = {}
    for r in experiment_results:
        by_sample.setdefault(r["sample_id"], []).append(r)

    lines = [
        "# Preset A/B Comparison Report",
        f"Generated: {utc_now_iso()}",
        f"Samples: {len(by_sample)}",
        "",
    ]

    summary_presets: Dict[str, List[float]] = {}
    for sample_id, results in sorted(by_sample.items()):
        ranked = sorted(results, key=lambda r: r.get("pseudo_mrs_delta", -999), reverse=True)
        lines.append(f"## {sample_id}")
        lines.append("")
        lines.append("| Rank | Preset | Δ MRS | Over-dark | Over-bright | Transient | Vocal | Safety |")
        lines.append("|------|--------|-------|-----------|-------------|-----------|-------|--------|")

        for i, r in enumerate(ranked):
            sg = r.get("safety_gate", {})
            passed = "✅" if sg.get("passed", False) else "❌"
            lines.append(
                f"| {i+1} | {r['preset']} | {r.get('pseudo_mrs_delta', 0):+.1f} | "
                f"{r.get('over_dark','-')} | {r.get('over_bright','-')} | "
                f"{r.get('transient_damage','-')} | {r.get('vocal_thinning','-')} | {passed} |"
            )
            summary_presets.setdefault(r["preset"], []).append(r.get("pseudo_mrs_delta", 0))
        lines.append("")

    # Overall preset ranking
    lines.append("## Preset Ranking (mean Δ MRS)")
    lines.append("")
    lines.append("| Preset | Mean Δ | Samples | Best In |")
    lines.append("|--------|--------|---------|---------|")
    preset_ranks = []
    for preset, deltas in summary_presets.items():
        best_in = sum(1 for results in by_sample.values()
                      if results and max(results, key=lambda r: r.get("pseudo_mrs_delta", -999))["preset"] == preset)
        preset_ranks.append((preset, sum(deltas) / len(deltas), len(deltas), best_in))
    for preset, mean_delta, n, best in sorted(preset_ranks, key=lambda x: x[1], reverse=True):
        lines.append(f"| {preset} | {mean_delta:+.1f} | {n} | {best} |")

    report = "\n".join(lines)
    if output_path:
        Path(output_path).write_text(report, encoding="utf-8")

    return {"report": report, "preset_ranks": preset_ranks}
