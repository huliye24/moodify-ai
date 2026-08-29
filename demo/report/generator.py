"""Report rendering — IntelligenceReport → report.json / report.md / terminal.

Rendering only. No analysis, no scoring — all numbers come from the
engine-filled report object.
"""

from __future__ import annotations

import json
from pathlib import Path

from engine.report_schema.schema import IntelligenceReport


def write_json(report: IntelligenceReport, out_dir: str | Path) -> Path:
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / "report.json"
    path.write_text(json.dumps(report.to_dict(), indent=2, ensure_ascii=False),
                    encoding="utf-8")
    return path


def write_markdown(report: IntelligenceReport, out_dir: str | Path) -> Path:
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / "report.md"
    path.write_text(render_markdown(report), encoding="utf-8")
    return path


def render_terminal(report: IntelligenceReport) -> str:
    """Compact terminal summary (the demo's headline output)."""
    t = report.track_info
    q = report.quality_score
    f = report.audio_features
    width = f.stereo.get("width_rating", "n/a")

    lines = [
        "=" * 58,
        "             Moodify Intelligence Report",
        "=" * 58,
        f"  Track          : {t.file_name}",
        f"  Duration       : {t.duration_s:.1f}s   "
        f"({t.sample_rate/1000:.1f} kHz / {t.channels}ch / {t.format})",
        "-" * 58,
        f"  Overall Score  : {q.overall} / 100",
        f"  Audio Quality  : {q.audio_quality} / 100",
        f"  Dynamic Range  : {q.dynamic_range} / 100",
        f"  Loudness       : {f.loudness.get('integrated_lufs', 'n/a')} LUFS "
        f"(LRA {f.loudness.get('loudness_range_lu', 'n/a')} LU)",
        f"  Stereo Image   : {str(width).capitalize()}",
        "-" * 58,
    ]
    if report.issues:
        lines.append("  Detected Issues:")
        for n, issue in enumerate(report.issues, 1):
            lines.append(f"   {n}. [{issue.severity}] {issue.title}")
    else:
        lines.append("  Detected Issues: none")

    lines += ["-" * 58, "  Recommendations:"]
    if report.recommendations:
        for n, rec in enumerate(report.recommendations, 1):
            lines.append(f"   {n}. [{rec.priority}] {rec.action}")
    else:
        lines.append("   - No action required.")

    ci = report.commercial_insight
    lines += [
        "-" * 58,
        "  Moodify Analysis:",
        f'   "{ci.summary}"',
        f"   Release readiness: {ci.release_readiness}",
        "=" * 58,
    ]
    return "\n".join(lines)


def render_markdown(report: IntelligenceReport) -> str:
    """Full Markdown report (report.md)."""
    t = report.track_info
    q = report.quality_score
    f = report.audio_features
    ci = report.commercial_insight

    md = [
        "# Moodify Intelligence Report",
        "",
        f"> {ci.summary}",
        "",
        "## Track",
        "",
        "| | |",
        "|---|---|",
        f"| File | `{t.file_name}` |",
        f"| Format | {t.format}, {t.sample_rate} Hz, {t.channels} ch |",
        f"| Duration | {t.duration_s:.1f} s |",
        "",
        "## Scores",
        "",
        "| Dimension | Score |",
        "|---|---|",
        f"| **Overall** | **{q.overall} / 100** |",
        f"| Audio Quality | {q.audio_quality} / 100 |",
        f"| Dynamic Range | {q.dynamic_range} / 100 |",
        f"| MRS method | {q.mrs.get('method', 'n/a')} |",
        "",
        "## Audio Features",
        "",
        "| Feature | Value |",
        "|---|---|",
        f"| Integrated loudness | {f.loudness.get('integrated_lufs', 'n/a')} LUFS |",
        f"| Loudness range (LRA) | {f.loudness.get('loudness_range_lu', 'n/a')} LU |",
        f"| Sample peak | {f.loudness.get('peak_db', 'n/a')} dBFS |",
        f"| Crest factor | {f.dynamics.get('crest_factor', 'n/a')} |",
        f"| Dynamic range (P95–P05) | {f.dynamics.get('dynamic_range_db', 'n/a')} dB |",
        f"| L/R correlation | {f.stereo.get('correlation_lr', 'n/a')} |",
        f"| Stereo width | {f.stereo.get('width_rating', 'n/a')} |",
        "",
        "### Spectral Balance (dB rel. total)",
        "",
        "| Sub | Bass | Low-Mid | Mid | Presence | Air |",
        "|---|---|---|---|---|---|",
        "| " + " | ".join(f"{f.spectrum.get(b, float('nan')):.1f}"
                            for b in ("sub", "bass", "low_mid", "mid", "presence", "air"))
        + " |",
        "",
        "## Detected Issues",
        "",
    ]
    if report.issues:
        for n, issue in enumerate(report.issues, 1):
            md += [f"### {n}. {issue.title} `[{issue.severity}]`",
                   "", issue.detail, "",
                   "```json", json.dumps(issue.evidence, indent=2), "```", ""]
    else:
        md += ["_None detected._", ""]

    md += ["## Recommendations", ""]
    if report.recommendations:
        for n, rec in enumerate(report.recommendations, 1):
            md += [f"{n}. **{rec.action}**  ",
                   f"   _Target:_ {rec.target} · _Priority:_ {rec.priority}  ",
                   f"   _Why:_ {rec.rationale}", ""]
    else:
        md += ["_No action required._", ""]

    md += [
        "## Commercial Insight",
        "",
        f"- **Release readiness:** {ci.release_readiness}",
        f"- **Summary:** {ci.summary}",
    ]
    if ci.strengths:
        md += ["", "**Strengths**", ""] + [f"- {s}" for s in ci.strengths]
    if ci.risks:
        md += ["", "**Risks**", ""] + [f"- {r}" for r in ci.risks]
    md += [
        "",
        "---",
        f"_Generated by Moodify Intelligence Engine "
        f"{report.meta.get('engine_version', '')} · schema "
        f"{report.meta.get('schema_id', '')} · "
        f"{report.meta.get('generated_at', '')}_",
        "",
    ]
    return "\n".join(md)
