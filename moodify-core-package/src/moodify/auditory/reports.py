"""Comparison reports and the four-image contact sheet (DSK-MFY-AUDITORY-SCAN-001)."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path



def build_contact_sheet(
    before_linear: Path,
    after_linear: Path,
    before_log: Path,
    after_log: Path,
    out_path: Path,
    *,
    case_id: str,
    source_sha_short: str,
    candidate_sha_short: str,
    profile_id: str,
) -> None:
    """Four-image contact sheet: before/after x linear/log."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.image import imread

    fig, axes = plt.subplots(2, 2, figsize=(16, 9))
    panels = [
        (axes[0, 0], before_linear, "BEFORE — LINEAR FREQUENCY"),
        (axes[0, 1], after_linear, "AFTER — LINEAR FREQUENCY"),
        (axes[1, 0], before_log, "BEFORE — LOG FREQUENCY"),
        (axes[1, 1], after_log, "AFTER — LOG FREQUENCY"),
    ]
    for ax, path, title in panels:
        img = imread(str(path))
        ax.imshow(img)
        ax.set_title(title, fontsize=11)
        ax.axis("off")
    fig.suptitle(
        f"case={case_id}  source={source_sha_short}  candidate={candidate_sha_short}\n"
        f"profile={profile_id}  generated={datetime.now(timezone.utc).isoformat()}",
        fontsize=9,
    )
    fig.tight_layout(rect=(0, 0, 1, 0.93))
    fig.savefig(out_path, dpi=100)
    plt.close(fig)


def build_comparison_report(
    out_path: Path,
    *,
    case_id: str,
    candidate_id: str,
    profile_id: str,
    profile_hash: str,
    metric_delta: dict,
    judgment: dict,
    normalization: dict,
    raw_band_deltas: dict,
    normalized_band_deltas: dict,
    plan_id: str | None,
    judgment_rules: dict,
    source_sha256: str,
    candidate_sha256: str,
) -> None:
    report = {
        "case_id": case_id,
        "candidate_id": candidate_id,
        "scan_profile_id": profile_id,
        "scan_profile_hash": profile_hash,
        "processing_plan_id": plan_id,
        "normalization": normalization,
        "raw_band_deltas": raw_band_deltas,
        "normalized_band_deltas": normalized_band_deltas,
        "metrics_delta": metric_delta,
        "judgment": judgment,
        "judgment_rules": judgment_rules,
        "source_sha256": source_sha256,
        "candidate_sha256": candidate_sha256,
        "human_listening_required": True,
        "artistic_approval_granted": False,
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }
    out_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
