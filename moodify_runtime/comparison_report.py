"""Stepwise Comparison Report Generator.

Generates before/after and per-step delta reports from MRS surfaces,
craft evidence manifests, and fusion scores. Deterministic formatting.
Part of ECHAIN-MOODIFY-MRS-EXTREME-017 / MHP-914.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .mrs_surface import MRSSurface
from .craft_evidence import CraftManifest
from .fusion_scorer import FusionScore


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class ComparisonReport:
    report_id: str
    sample_id: str
    preset: str
    genre: str
    mrs_surface: MRSSurface | None = None
    craft_manifest: CraftManifest | None = None
    fusion_score: FusionScore | None = None
    generated_at: str = ""

    def to_dict(self) -> dict[str, Any]:
        d: dict[str, Any] = {
            "report_id": self.report_id,
            "sample_id": self.sample_id,
            "preset": self.preset,
            "genre": self.genre,
            "generated_at": self.generated_at,
        }
        if self.mrs_surface:
            d["mrs_surface"] = self.mrs_surface.to_dict()
        if self.craft_manifest:
            d["craft_manifest"] = self.craft_manifest.summary()
        if self.fusion_score:
            d["fusion_score"] = self.fusion_score.to_dict()
        return d


def generate_comparison_json(report: ComparisonReport) -> str:
    return json.dumps(report.to_dict(), ensure_ascii=False, indent=2)


def generate_comparison_markdown(report: ComparisonReport) -> str:
    lines = [
        "# Stepwise Comparison Report",
        "",
        f"**Report**: {report.report_id}",
        f"**Sample**: {report.sample_id} | **Preset**: {report.preset} | **Genre**: {report.genre}",
        f"**Generated**: {report.generated_at}",
        "",
    ]

    # MRS Surface section
    if report.mrs_surface:
        ms = report.mrs_surface
        lines.extend([
            "## MRS Quality Surface",
            "",
            f"**Composite**: {ms.composite:.1f} | **Confidence**: {ms.confidence:.0f}% | **Gate**: **{ms.gate}**",
            "",
            "| Dimension | Score | Weight | Status |",
            "|---|---|---|---|",
        ])
        for d in ms.dimensions:
            lines.append(f"| {d.label} | {d.value:.1f} | {d.weight:.0%} | {d.status.upper()} |")
        if ms.flags:
            lines.extend(["", "**Flags**: " + ", ".join(f"`{f}`" for f in ms.flags)])

    # Fusion Score section
    if report.fusion_score:
        fs = report.fusion_score
        lines.extend([
            "",
            "## Fusion Score",
            "",
            f"**Verdict**: **{fs.verdict}** | **Quality**: {fs.composite_quality:.1f}",
            "",
            "| Penalty | Score |",
            "|---|---|",
            f"| Artifact | {fs.artifact_penalty:.1f} |",
            f"| Overprocessing | {fs.overprocessing_penalty:.1f} |",
            f"| Intent Loss | {fs.intent_loss_penalty:.1f} |",
            f"| **Composite** | **{fs.composite_penalty:.1f}** |",
            "",
            fs.explanation,
        ])

    # Craft Evidence section
    if report.craft_manifest:
        cm = report.craft_manifest
        lines.extend([
            "",
            "## Craft Chain Evidence",
            "",
            f"**Chain**: {cm.chain_name} | **Steps recorded**: {len(cm.steps)}/{cm.total_steps}",
            "",
            "| # | Operation | Category | Risk | Delta | Error |",
            "|---|---|---|---|---|---|",
        ])
        for s in cm.steps:
            delta_str = ", ".join(f"{k}: {v}" for k, v in list(s.delta.items())[:3])
            err_str = "ERROR" if s.error else ""
            lines.append(
                f"| {s.step_index} | {s.op_name} | {s.category} | {s.risk} | "
                f"{delta_str if delta_str else '-'} | {err_str} |"
            )

    lines.extend(["", "---", f"*Report generated at {report.generated_at}*"])
    return "\n".join(lines)


def write_comparison_report(report: ComparisonReport, output_dir: Path) -> dict[str, str]:
    output_dir.mkdir(parents=True, exist_ok=True)
    json_path = output_dir / "comparison_report.json"
    md_path = output_dir / "comparison_report.md"

    json_path.write_text(generate_comparison_json(report), encoding="utf-8")
    md_path.write_text(generate_comparison_markdown(report), encoding="utf-8")

    return {"json": str(json_path), "markdown": str(md_path)}
