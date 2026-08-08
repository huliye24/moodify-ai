"""Learning surface pack for the multi-night learning store.

Generates operator-readable learning views, pack manifests, and stable
latest pointers. Part of ECHAIN-MOODIFY-MULTI-NIGHT-STORE-016 / MHP-908.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .learning_store import store_summary
from .trend_analyzer import analyze_trends, format_trend_markdown
from .significance_evaluator import evaluate_store, format_significance_markdown


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def generate_learning_report(
    store_path: Path,
    output_dir: Path,
    window_size: int = 3,
) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)

    store_summ = store_summary(store_path)
    trend_report = analyze_trends(store_path, window_size=window_size)
    sig_report = evaluate_store(store_path) if store_summ["total_nights"] >= 2 else None

    now_iso = _utc_now_iso()
    run_id = datetime.now().strftime("%Y%m%d_%H%M%S")

    # Write outputs
    trend_md = format_trend_markdown(trend_report)
    (output_dir / "trend_report.md").write_text(trend_md, encoding="utf-8")

    if sig_report:
        sig_md = format_significance_markdown(sig_report)
        (output_dir / "significance_report.md").write_text(sig_md, encoding="utf-8")

    # Pack manifest
    manifest = {
        "pack_id": f"learning_surface_{run_id}",
        "generated_at": now_iso,
        "store_summary": store_summ,
        "trend_summary": trend_report.summary,
        "files": ["trend_report.md"],
    }
    if sig_report:
        manifest["significance_summary"] = {
            "group_a_n": sig_report.group_a.n,
            "group_b_n": sig_report.group_b.n,
            "signal_count": sum(1 for r in sig_report.results if r.signal == "signal"),
            "noise_count": sum(1 for r in sig_report.results if r.signal == "noise"),
        }
        manifest["files"].append("significance_report.md")

    (output_dir / "pack_manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")

    # Learning summary (operator-readable one-pager)
    lines = [
        "# Moodify Multi-Night Learning Surface",
        "",
        f"**Generated**: {now_iso}",
        f"**Nights in store**: {store_summ['total_nights']}",
        f"**Date range**: {store_summ.get('earliest', 'n/a')} to {store_summ.get('latest', 'n/a')}",
        "",
        "## Trend Summary",
        "",
        f"- EDS direction: **{trend_report.summary.get('eds_overall_direction', 'n/a')}**",
        f"- Elapsed direction: **{trend_report.summary.get('elapsed_overall_direction', 'n/a')}**",
        f"- Improving nights: {trend_report.summary.get('eds_improving_nights', 0)}",
        f"- Declining nights: {trend_report.summary.get('eds_declining_nights', 0)}",
    ]
    if sig_report:
        lines.extend([
            "",
            "## Signal Detection",
            "",
            f"| Metric | Signal | Effect |",
            f"|---|---|---|",
        ])
        for r in sig_report.results:
            lines.append(f"| {r.metric} | **{r.signal.upper()}** | {r.effect_label} (d={r.effect_size:.3f}) |")
    lines.extend([
        "",
        "## Files",
        "",
        f"- Store: `{store_summ['store_path']}`",
        f"- Trend report: `{output_dir / 'trend_report.md'}`",
    ])
    if sig_report:
        lines.append(f"- Significance report: `{output_dir / 'significance_report.md'}`")
    lines.append(f"- Manifest: `{output_dir / 'pack_manifest.json'}`")

    (output_dir / "learning_summary.md").write_text("\n".join(lines), encoding="utf-8")

    # Latest pointer
    latest = {
        "latest_pack_id": manifest["pack_id"],
        "latest_pack_dir": str(output_dir),
        "generated_at": now_iso,
        "store_path": str(store_path),
    }
    latest_path = output_dir.parent / "LATEST.json"
    latest_path.write_text(json.dumps(latest, ensure_ascii=False, indent=2), encoding="utf-8")

    manifest["files"].append("learning_summary.md")
    manifest["latest_pointer"] = str(latest_path)

    return manifest
