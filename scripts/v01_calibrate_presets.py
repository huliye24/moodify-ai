"""MHP-005-A: before/after calibration tool for v0.1.0 presets.

Run all 3 presets on every WAV in --input-dir, compare metrics,
and produce summary.json + summary.md.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

SUPPORTED_EXTENSIONS = {".wav", ".mp3", ".flac", ".aiff", ".aif"}
PRESETS = ["warm_vocal", "clean_master", "wide_space"]


def collect_audio_files(input_dir: str) -> list[Path]:
    """Return sorted list of supported audio files in input_dir."""
    root = Path(input_dir)
    if not root.is_dir():
        print(f"ERROR: input-dir not found: {input_dir}")
        sys.exit(1)

    files = sorted(
        f for f in root.iterdir()
        if f.suffix.lower() in SUPPORTED_EXTENSIONS
    )
    if not files:
        print(f"ERROR: no supported audio files in {input_dir}")
        sys.exit(1)

    return files


def run_calibration(input_files: list[Path], output_dir: str) -> dict:
    """Run all presets on all files, return summary dict."""
    from moodify.v01_pipeline import process_audio

    out_root = Path(output_dir)
    entries = []

    for fp in input_files:
        for preset in PRESETS:
            preset_out = out_root / fp.stem / preset
            preset_out.mkdir(parents=True, exist_ok=True)

            result = process_audio(
                input_path=str(fp),
                preset=preset,
                output_dir=str(preset_out),
            )

            entry = {
                "file": fp.name,
                "preset": preset,
                "success": result.success,
            }

            if result.success and result.metrics_before:
                mb = result.metrics_before.to_dict()
                entry["before"] = {
                    "peak_db": mb["dynamics"]["peak_db"],
                    "crest_factor": mb["dynamics"]["crest_factor"],
                    "dynamic_range_db": mb["dynamics"]["dynamic_range_db"],
                    "correlation_lr": mb["stereo"]["correlation_lr"],
                    "spectrum": mb["spectrum"],
                }

            if result.success and result.diagnosis:
                diag = result.diagnosis.to_dict()
                entry["diagnosis"] = {
                    "overall_health": diag["overall_health"],
                    "issues": diag["issues"],
                    "strengths": diag["strengths"],
                    "suggested_presets": diag["suggested_presets"],
                }

            if result.success and result.output_path:
                entry["output_path"] = result.output_path
                # Measure "after" by re-analyzing the processed output
                from moodify.v01_analyzer import analyze  # noqa: F811
                after_metrics = analyze(result.output_path, str(preset_out))
                ma = after_metrics.to_dict()
                entry["after"] = {
                    "peak_db": ma["dynamics"]["peak_db"],
                    "crest_factor": ma["dynamics"]["crest_factor"],
                    "dynamic_range_db": ma["dynamics"]["dynamic_range_db"],
                    "correlation_lr": ma["stereo"]["correlation_lr"],
                    "spectrum": ma["spectrum"],
                }

            if not result.success:
                entry["error"] = result.error

            entries.append(entry)

            status = "OK" if result.success else "FAIL"
            cf_before = entry.get("before", {}).get("crest_factor", "?")
            cf_after = entry.get("after", {}).get("crest_factor", "?")
            cf_b = f"{cf_before:.2f}" if isinstance(cf_before, (int, float)) else str(cf_before)
            cf_a = f"{cf_after:.2f}" if isinstance(cf_after, (int, float)) else str(cf_after)
            print(f"  [{status}] {fp.name:45s}  {preset:14s}  "
                  f"crest {cf_b}→{cf_a}")

    summary = {
        "calibration_version": "MHP-005-A",
        "presets": PRESETS,
        "num_files": len(input_files),
        "num_entries": len(entries),
        "entries": entries,
    }

    return summary


def save_summary_json(summary: dict, output_dir: str) -> Path:
    """Write summary.json and return path."""
    out_root = Path(output_dir)
    out_root.mkdir(parents=True, exist_ok=True)

    out_path = out_root / "summary.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)

    return out_path


def save_summary_md(summary: dict, output_dir: str) -> Path:
    """Write summary.md and return path."""
    out_root = Path(output_dir)
    out_root.mkdir(parents=True, exist_ok=True)

    lines = [
        "# Moodify v0.1.0 Preset Calibration Report",
        "",
        f"**Files processed**: {summary['num_files']}",
        f"**Presets tested**: {', '.join(summary['presets'])}",
        f"**Total runs**: {summary['num_entries']}",
        "",
        "---",
        "",
        "## Per-File Results",
        "",
    ]

    for entry in summary["entries"]:
        icon = "✓" if entry["success"] else "✗"
        lines.append(f"### {icon} {entry['file']} — {entry['preset']}")
        lines.append("")

        if not entry["success"]:
            lines.append(f"**FAILED**: {entry.get('error', 'unknown error')}")
            lines.append("")
            continue

        before = entry.get("before", {})
        after = entry.get("after", {})
        if before:
            lines.append("| Metric | Before | After |")
            lines.append("|--------|--------|-------|")
            after_peak = f"{after['peak_db']:+.1f} dB" if after else "—"
            after_cf = f"{after['crest_factor']:.2f}" if after else "—"
            after_dr = f"{after['dynamic_range_db']:.1f} dB" if after else "—"
            after_corr = f"{after['correlation_lr']:.3f}" if after else "—"
            lines.append(f"| Peak | {before['peak_db']:+.1f} dB | {after_peak} |")
            lines.append(f"| Crest Factor | {before['crest_factor']:.2f} | {after_cf} |")
            lines.append(f"| Dynamic Range | {before['dynamic_range_db']:.1f} dB | {after_dr} |")
            lines.append(f"| Correlation L/R | {before['correlation_lr']:.3f} | {after_corr} |")
            lines.append("")

            sp = before["spectrum"]
            sp_a = after["spectrum"] if after else {}
            lines.append("| Band | Before (dB) | After (dB) |")
            lines.append("|------|-------------|------------|")
            for band in ["sub_bass", "bass", "low_mid", "mid", "presence", "air"]:
                after_val = f"{sp_a[band]:+.1f}" if sp_a else "—"
                lines.append(f"| {band} | {sp[band]:+.1f} | {after_val} |")
            lines.append("")

        diag = entry.get("diagnosis", {})
        if diag:
            lines.append(f"**Health**: {diag.get('overall_health', '?')}")
            if diag.get("issues"):
                lines.append("")
                lines.append("Issues:")
                for issue in diag["issues"]:
                    lines.append(f"- {issue}")
            if diag.get("suggested_presets"):
                suggested = ", ".join(diag["suggested_presets"])
                lines.append(f"")
                lines.append(f"Suggested presets: {suggested}")
            lines.append("")

        if entry.get("output_path"):
            lines.append(f"Output: `{entry['output_path']}`")
            lines.append("")

        lines.append("---")
        lines.append("")

    # Cross-preset comparison table
    lines.append("## Crest Factor Before → After")
    lines.append("")
    lines.append("| File | warm_vocal | clean_master | wide_space |")
    lines.append("|------|-----------|-------------|-----------|")

    for fp_name in sorted(set(e["file"] for e in summary["entries"])):
        row = [fp_name]
        for preset in PRESETS:
            match = [
                e for e in summary["entries"]
                if e["file"] == fp_name and e["preset"] == preset and e["success"]
            ]
            if match:
                b = match[0].get("before", {})
                a = match[0].get("after", {})
                b_cf = b.get("crest_factor", 0)
                a_cf = a.get("crest_factor", 0)
                row.append(f"{b_cf:.2f}→{a_cf:.2f}")
            else:
                row.append("—")
        lines.append("| " + " | ".join(row) + " |")

    out_path = out_root / "summary.md"
    with open(out_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")

    return out_path


def main():
    parser = argparse.ArgumentParser(
        description="MHP-005-A: v0.1.0 preset before/after calibration"
    )
    parser.add_argument(
        "--input-dir", required=True,
        help="Directory containing audio files (WAV/MP3/FLAC)"
    )
    parser.add_argument(
        "--output-dir", default="calibration_reports/v0.1.0-alpha.1",
        help="Output directory for reports and processed files"
    )
    args = parser.parse_args()

    files = collect_audio_files(args.input_dir)
    print(f"\nMHP-005-A Calibration")
    print(f"  Input:  {args.input_dir} ({len(files)} files)")
    print(f"  Output: {args.output_dir}")
    print(f"  Presets: {', '.join(PRESETS)}\n")

    summary = run_calibration(files, args.output_dir)

    ok = sum(1 for e in summary["entries"] if e["success"])
    fail = summary["num_entries"] - ok

    json_path = save_summary_json(summary, args.output_dir)
    md_path = save_summary_md(summary, args.output_dir)

    print(f"\n  Done: {ok} ok, {fail} failed")
    print(f"  JSON: {json_path}")
    print(f"  MD:   {md_path}")

    return 0 if fail == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
