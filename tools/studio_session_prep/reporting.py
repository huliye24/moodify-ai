"""Report generation — Markdown + HTML technical reports for studio sessions."""
from __future__ import annotations

import html as html_mod
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _safe_val(d: dict, key: str, default: Any = "—") -> Any:
    v = d.get(key)
    return v if v is not None else default


def _fmt_val(v: Any, prec: int = 2) -> str:
    if v is None:
        return "null"
    if isinstance(v, float):
        return f"{v:.{prec}f}"
    return str(v)


def build_comparison_table(
    reference_metrics: dict[str, Any],
    candidate_metrics: dict[str, Any],
) -> dict[str, Any]:
    """Compare two sets of metrics and produce a structured diff.

    Returns: dict with metric deltas, warnings, and human_review=PENDING.
    """
    comparison: dict[str, Any] = {
        "generated_at": _utc_now(),
        "reference_source": reference_metrics.get("source_path", ""),
        "candidate_source": candidate_metrics.get("source_path", ""),
        "deltas": {},
        "warnings": [],
        "limitations": [],
        "human_review": "PENDING",
    }

    # Level deltas
    ref_level = reference_metrics.get("level", {})
    cand_level = candidate_metrics.get("level", {})
    for key in ["peak_dbfs", "rms_db", "crest_factor"]:
        rv = ref_level.get(key)
        cv = cand_level.get(key)
        if rv is not None and cv is not None:
            comparison["deltas"][f"{key}_delta"] = round(cv - rv, 2)

    # Spectral deltas
    ref_spec = reference_metrics.get("spectral", {})
    cand_spec = candidate_metrics.get("spectral", {})
    for key in ["spectral_centroid_hz", "spectral_entropy", "spectral_flux"]:
        rv = ref_spec.get(key)
        cv = cand_spec.get(key)
        if rv is not None and cv is not None:
            comparison["deltas"][f"{key}_delta"] = round(cv - rv, 4)

    # Stereo deltas
    ref_stereo = reference_metrics.get("stereo", {})
    cand_stereo = candidate_metrics.get("stereo", {})
    lr_ref = ref_stereo.get("left_right_correlation")
    lr_cand = cand_stereo.get("left_right_correlation")
    if lr_ref is not None and lr_cand is not None:
        comparison["deltas"]["left_right_correlation_delta"] = round(lr_cand - lr_ref, 3)

    # Band fraction deltas
    ref_bands = reference_metrics.get("band_fractions", {})
    cand_bands = candidate_metrics.get("band_fractions", {})
    for key, rv in ref_bands.items():
        cv = cand_bands.get(key)
        if rv is not None and cv is not None:
            comparison["deltas"][f"{key}_delta"] = round(cv - rv, 4)

    # Warnings generation
    rms_delta = comparison["deltas"].get("rms_db_delta")
    if rms_delta is not None:
        if abs(rms_delta) > 3.0:
            comparison["warnings"].append(
                f"Large loudness change ({rms_delta:+.1f} dB RMS). "
                "Level-match before subjective comparison."
            )
        elif abs(rms_delta) > 0.5:
            comparison["warnings"].append(
                f"Moderate loudness change ({rms_delta:+.1f} dB RMS). "
                "Loudness bias possible in A/B listening."
            )

    # Limitations
    comparison["limitations"].extend([
        "LRA, true peak, phase, and masking are unavailable — null values do not indicate safety.",
        "Spectral differences must not be interpreted as 'better sounding' without controlled listening.",
        "Comparison is purely technical; artistic judgment requires human review.",
    ])

    return comparison


def build_markdown_report(
    manifest: dict[str, Any] | None = None,
    wse_profile: dict[str, Any] | None = None,
    candidate_results: list[dict[str, Any]] | None = None,
    comparisons: list[dict[str, Any]] | None = None,
) -> str:
    """Build a complete Markdown technical report."""
    lines = [
        "# Moodify Studio Session — Technical Report",
        "",
        f"**Generated:** {_utc_now()}",
        f"**Tool Version:** 0.1.0",
        "",
    ]

    # Session info
    if manifest:
        brief = manifest.get("session_brief", {})
        lines += [
            "## 1. Session Information",
            "",
            f"- **Project:** {brief.get('project_title', '—')}",
            f"- **Client:** {brief.get('client_name', '—')}",
            f"- **Date:** {brief.get('session_date', '—')}",
            f"- **Engineer:** {brief.get('engineer_name', '—')}",
            f"- **Location:** {brief.get('studio_location', '—')}",
            f"- **Genre:** {brief.get('genre', '—')}",
            "",
        ]
        rs = manifest.get("recording_spec", {})
        if rs:
            lines += [
                "### Recording Specification",
                "",
                f"- **Sample Rate:** {rs.get('sample_rate', '—')} Hz",
                f"- **Bit Depth:** {rs.get('bit_depth', '—')}-bit",
                f"- **Format:** {rs.get('file_format', '—')}",
                f"- **Target Peak:** {rs.get('target_peak_dbfs', '—')} dBFS",
                f"- **Channels:** {rs.get('channel_count', '—')}",
                "",
            ]

    # WSE Profile
    if wse_profile:
        lines += [
            "## 2. WSE Analysis",
            "",
            f"- **File:** `{wse_profile.get('source_path', '—')}`",
            f"- **SHA-256:** `{wse_profile.get('source_sha256', '—')}`",
            f"- **Duration:** {wse_profile.get('duration_s', '—')}s",
            f"- **Sample Rate:** {wse_profile.get('sample_rate', '—')} Hz",
            f"- **Channels:** {wse_profile.get('channels', '—')}",
            "",
            "### Level Metrics",
            "",
        ]
        level = wse_profile.get("level", {})
        lines += [
            f"| Metric | Value |",
            f"|--------|-------|",
            f"| Peak | {_fmt_val(level.get('peak_dbfs'))} dBFS |",
            f"| RMS | {_fmt_val(level.get('rms_db'))} dB |",
            f"| Crest Factor | {_fmt_val(level.get('crest_factor'))} |",
            "",
        ]

        loudness = wse_profile.get("loudness", {})
        lines += [
            "### Loudness",
            "",
            f"| Metric | Value |",
            f"|--------|-------|",
            f"| Integrated LUFS | {_fmt_val(loudness.get('loudness_lufs'), 1)} |",
            f"| LRA | null (pyloudnorm limitation) |",
            f"| True Peak | null (no BS.1770 meter) |",
            "",
        ]

        spectral = wse_profile.get("spectral", {})
        lines += [
            "### Spectral",
            "",
            f"| Metric | Value |",
            f"|--------|-------|",
            f"| Centroid | {_fmt_val(spectral.get('spectral_centroid_hz'), 0)} Hz |",
            f"| Entropy | {_fmt_val(spectral.get('spectral_entropy'), 3)} |",
            f"| Flux | {_fmt_val(spectral.get('spectral_flux'), 6)} |",
            "",
        ]

        bf = wse_profile.get("band_fractions", {})
        if bf:
            lines += [
                "### Band Energy Fractions",
                "",
                "| Band | Fraction |",
                "|------|----------|",
            ]
            for band_key, fraction in bf.items():
                band_label = band_key.replace("band_", "").replace("_", "–")
                lines.append(f"| {band_label} Hz | {_fmt_val(fraction, 4)} |")
            lines.append("")

        unavailable = wse_profile.get("unavailable", {})
        if unavailable:
            lines += [
                "### Unavailable Metrics",
                "",
            ]
            for metric, reason in unavailable.items():
                lines.append(f"- **{metric}:** {reason}")
            lines.append("")

    # Candidate results
    if candidate_results:
        lines += [
            "## 3. Candidate Processing Results",
            "",
        ]
        for cr in candidate_results:
            cid = cr.get("candidate_id", "?")
            lines += [
                f"### Candidate: {cid}",
                "",
                f"- **Preset:** {cr.get('preset', '—')}",
                f"- **Executed:** {cr.get('executed', False)}",
                f"- **Dry Run:** {cr.get('dry_run', True)}",
                f"- **Exit Code:** {_fmt_val(cr.get('exit_code'), 0)}",
                f"- **Duration:** {cr.get('duration_s', 0):.1f}s",
            ]
            if cr.get("error"):
                lines.append(f"- **Error:** {cr['error']}")
            if cr.get("output_audio"):
                lines.append(f"- **Output:** `{cr['output_audio']}`")
            if cr.get("output_sha256"):
                lines.append(f"- **Output SHA-256:** `{cr['output_sha256']}`")
            lines.append("")

    # Comparisons
    if comparisons:
        lines += [
            "## 4. Candidate Comparisons",
            "",
        ]
        for i, comp in enumerate(comparisons):
            lines += [
                f"### Comparison {i + 1}",
                f"- **Human Review:** {comp.get('human_review', 'PENDING')}",
                "",
                "#### Deltas",
                "",
                "| Metric | Delta |",
                "|--------|-------|",
            ]
            for key, val in comp.get("deltas", {}).items():
                lines.append(f"| {key} | {_fmt_val(val)} |")
            lines.append("")

            warnings = comp.get("warnings", [])
            if warnings:
                lines += ["**Warnings:**", ""]
                for w in warnings:
                    lines.append(f"- {w}")
                lines.append("")

    # Limitations and disclaimer
    lines += [
        "## 5. Limitations",
        "",
        "- LRA and true peak measurements are unavailable (pyloudnorm limitation).",
        "- Phase analysis, masking analysis are not implemented.",
        "- Spectral differences are technical measurements only — not subjective quality ratings.",
        "- All candidate plans require human review before execution.",
        "- Candidate comparisons are technical; artistic judgment is separate.",
        "- This tool does not make automatic Final selections or rule promotions.",
        "",
        "## 6. Disclaimer",
        "",
        "This report is a technical summary generated by Moodify Studio Session Prep tools. ",
        "It does not constitute a claim of release-readiness, superiority over human engineering, ",
        "or automated quality judgment. Final delivery decisions must be made by a qualified engineer.",
        "",
        f"---\n*Report generated {_utc_now()} by Moodify Studio Prep v0.1.0*",
        "",
    ]

    return "\n".join(lines) + "\n"


def build_html_report(md_content: str, title: str = "Moodify Studio Report") -> str:
    """Convert a Markdown-like report to self-contained HTML."""
    # Simple conversion: wrap in pre for now; proper MD→HTML requires a library
    escaped = html_mod.escape(md_content)
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>{html_mod.escape(title)}</title>
<style>
  body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', system-ui, sans-serif;
         max-width: 960px; margin: 0 auto; padding: 24px; background: #0d1117; color: #c9d1d9; line-height: 1.6; }}
  h1 {{ color: #58a6ff; border-bottom: 1px solid #30363d; padding-bottom: 12px; }}
  h2 {{ color: #f0883e; margin-top: 32px; }}
  h3 {{ color: #d2a8ff; }}
  table {{ border-collapse: collapse; width: 100%; margin: 12px 0; }}
  th, td {{ padding: 6px 12px; text-align: left; border-bottom: 1px solid #21262d; }}
  th {{ background: #161b22; color: #c9d1d9; font-weight: 600; }}
  tr:hover {{ background: #161b22; }}
  code {{ background: #21262d; padding: 2px 6px; border-radius: 3px; }}
  pre {{ background: #161b22; padding: 16px; border-radius: 6px; overflow-x: auto; white-space: pre-wrap; }}
  .warning {{ color: #f85149; }}
  .null {{ color: #8b949e; font-style: italic; }}
</style>
</head>
<body>
<pre>{escaped}</pre>
</body>
</html>"""
