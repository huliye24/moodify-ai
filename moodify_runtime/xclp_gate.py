"""X-CLP gate helper for Moodify modules.

Wraps the X-CLP scoring protocol to score Moodify source modules and
produce gate reports. Part of ECHAIN-MOODIFY-DEEPSEEK-API-015 / MHP-900.
"""

from __future__ import annotations

import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

# X-CLP lives alongside moodify-mainline on the cloud server.
_XCLP_ROOT = Path("/home/ubuntu/X-CLP")
if str(_XCLP_ROOT) not in sys.path:
    sys.path.insert(0, str(_XCLP_ROOT))

from xclp.scoring import (  # type: ignore[import-not-found]
    DIMENSIONS,
    ScoreResult,
    classify_score,
    clamp_score,
    compute_l_code,
    score_from_config,
)

__all__ = [
    "DIMENSIONS",
    "ScoreResult",
    "classify_score",
    "clamp_score",
    "compute_l_code",
    "score_from_config",
    "GateReport",
    "score_module",
    "gate_module",
    "format_gate_report_markdown",
]


@dataclass
class GateReport:
    module_name: str
    score: ScoreResult
    xclp_target: int
    passed: bool
    gap: float
    notes: list[str] = field(default_factory=list)


def score_module(
    module_name: str,
    r_speed: float,
    s_structure: float,
    m_maintainability: float,
    e_evolvability: float,
) -> ScoreResult:
    return score_from_config({
        "project_name": module_name,
        "scores": {
            "R_speed": r_speed,
            "S_structure": s_structure,
            "M_maintainability": m_maintainability,
            "E_evolvability": e_evolvability,
        },
    })


def gate_module(
    module_name: str,
    r_speed: float,
    s_structure: float,
    m_maintainability: float,
    e_evolvability: float,
    xclp_target: int = 60,
) -> GateReport:
    score = score_module(module_name, r_speed, s_structure, m_maintainability, e_evolvability)
    passed = score.L_code >= xclp_target
    gap = max(0.0, xclp_target - score.L_code)

    notes: list[str] = []
    if not passed:
        dims = {
            "R_speed": r_speed,
            "S_structure": s_structure,
            "M_maintainability": m_maintainability,
            "E_evolvability": e_evolvability,
        }
        weakest = min(dims, key=lambda k: dims[k])
        notes.append(f"weakest dimension: {weakest} ({dims[weakest]:.0f}) — target {xclp_target}")
        if r_speed < 40:
            notes.append("R_speed too low: delivery path is fragile")
        if s_structure < 40:
            notes.append("S_structure too low: module boundaries are unclear")
        if m_maintainability < 40:
            notes.append("M_maintainability too low: debug/modify costs are high")
        if e_evolvability < 40:
            notes.append("E_evolvability too low: cannot evolve without rewrite")

    return GateReport(
        module_name=module_name,
        score=score,
        xclp_target=xclp_target,
        passed=passed,
        gap=gap,
        notes=notes,
    )


def format_gate_report_markdown(reports: list[GateReport], title: str = "X-CLP Gate Report") -> str:
    lines = [
        f"# {title}",
        "",
        f"| Module | R | S | M | E | L_code | Level | Gate | Target | Pass |",
        f"|---|---|---|---|---|---|---|---|---|---|",
    ]
    for r in reports:
        s = r.score
        lines.append(
            f"| {r.module_name} | {s.R_speed:.0f} | {s.S_structure:.0f} | "
            f"{s.M_maintainability:.0f} | {s.E_evolvability:.0f} | "
            f"{s.L_code:.1f} | {s.level} | {s.gate} | {r.xclp_target} | "
            f"{'PASS' if r.passed else 'FAIL'} |"
        )

    passed = sum(1 for r in reports if r.passed)
    lines.extend([
        "",
        f"**Summary**: {passed}/{len(reports)} modules passed their X-CLP gate.",
        "",
    ])

    failed = [r for r in reports if not r.passed]
    if failed:
        lines.append("## Failures")
        lines.append("")
        for r in failed:
            lines.append(f"### {r.module_name} (gap: {r.gap:.1f})")
            for note in r.notes:
                lines.append(f"- {note}")
            lines.append("")

    return "\n".join(lines)
