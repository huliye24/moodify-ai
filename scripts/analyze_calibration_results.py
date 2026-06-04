#!/usr/bin/env python3
"""MHP-079 + MHP-080: MRS comparison and gate accuracy analysis.

Compares pseudo-MRS, calibrated pseudo-MRS, and MRS Open against human labels.
Analyzes gate accuracy, false positives/negatives, and threshold sensitivity.
"""

from __future__ import annotations

import csv
import json
import math
import sys
from pathlib import Path
from collections import defaultdict
from typing import Any, Dict, List, Optional, Tuple

PROJECT = Path(__file__).resolve().parent.parent


# ── Helpers ──────────────────────────────────────────────────────────


def load_jsonl(path: Path) -> List[Dict[str, Any]]:
    rows = []
    if path.exists():
        with path.open("r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    rows.append(json.loads(line))
    return rows


def spearman_r(xs: List[float], ys: List[float]) -> float:
    if len(xs) < 3:
        return 0.0

    def rank(vals):
        indexed = sorted(enumerate(vals), key=lambda x: x[1])
        ranks = [0.0] * len(vals)
        i = 0
        while i < len(indexed):
            j = i
            while j < len(indexed) and indexed[j][1] == indexed[i][1]:
                j += 1
            avg_rank = (i + j - 1) / 2.0 + 1.0
            for k in range(i, j):
                ranks[indexed[k][0]] = avg_rank
            i = j
        return ranks

    n = len(xs)
    rx = rank(xs)
    ry = rank(ys)
    mean_rx = (n + 1) / 2.0

    num = sum((rx[i] - mean_rx) * (ry[i] - mean_rx) for i in range(n))
    den_x = math.sqrt(sum((rx[i] - mean_rx) ** 2 for i in range(n)))
    den_y = math.sqrt(sum((ry[i] - mean_rx) ** 2 for i in range(n)))
    if den_x * den_y == 0:
        return 0.0
    return num / (den_x * den_y)


def agreement_rate(deltas: List[Optional[float]], human_decisions: List[str]) -> float:
    """% where delta sign matches human decision."""
    matches = 0
    total = 0
    human_map = {"better": 1, "worse": -1, "no_change": 0, "unsure": 0}
    for d, h in zip(deltas, human_decisions):
        if d is None:
            continue
        total += 1
        h_sign = human_map.get(h, 0)
        d_sign = 1 if d > 0 else (-1 if d < 0 else 0)
        if d_sign == h_sign or (h_sign == 0 and abs(d) < 0.5):
            matches += 1
    return matches / total if total > 0 else 0.0


# ── Main analysis ────────────────────────────────────────────────────


def analyze(calibration_dir: Path, output_dir: Path):
    output_dir.mkdir(parents=True, exist_ok=True)

    # Load data
    manifest_path = calibration_dir / "manifest.csv"
    labels_path = PROJECT / "data" / "calibration" / "mrs_002" / "labels.jsonl"

    if not manifest_path.exists():
        print(f"ERROR: manifest.csv not found at {manifest_path}")
        print("Run run_calibration_pipeline.py first.")
        return

    manifest = []
    with manifest_path.open("r", encoding="utf-8", newline="") as f:
        for row in csv.DictReader(f):
            manifest.append(row)

    labels = load_jsonl(labels_path)
    label_map = {l["sample_id"]: l for l in labels}

    print(f"# Analysis: {len(manifest)} manifest rows, {len(labels)} labels")

    # ── MHP-079: MRS Comparison ──
    print("\n## MHP-079: MRS Variant Comparison\n")

    pseudo_deltas: List[Optional[float]] = []
    mrs_open_deltas: List[Optional[float]] = []
    human_decisions: List[str] = []
    per_genre: Dict[str, Dict[str, List[float]]] = defaultdict(lambda: defaultdict(list))

    for row in manifest:
        sid = row["sample_id"]
        genre = row["genre"]
        status = row["status"]

        pd_val = float(row.get("pseudo_delta", 0) or 0)
        mod_val_str = row.get("mrs_open_delta", "")
        mod_val = float(mod_val_str) if mod_val_str and mod_val_str != "" and mod_val_str != "None" else None

        label = label_map.get(sid, {})
        hd = label.get("human_decision", "")

        pseudo_deltas.append(pd_val)
        mrs_open_deltas.append(mod_val)
        human_decisions.append(hd)

        if hd:
            per_genre[genre]["pseudo_delta"].append(pd_val)
            per_genre[genre]["human"].append(hd)
            if mod_val is not None:
                per_genre[genre]["mrs_open_delta"].append(mod_val)

    # Overall correlation
    valid_pseudo = [(d, h) for d, h in zip(pseudo_deltas, human_decisions) if h and d is not None]
    valid_mrs_open = [(d, h) for d, h in zip(mrs_open_deltas, human_decisions) if h and d is not None]

    pseudo_ds = [v[0] for v in valid_pseudo]
    pseudo_hs = [v[1] for v in valid_pseudo]
    mrs_open_ds = [v[0] for v in valid_mrs_open]
    mrs_open_hs = [v[1] for v in valid_mrs_open]

    human_nums_p = [{"better": 1, "worse": -1, "no_change": 0, "unsure": 0}.get(h, 0) for h in pseudo_hs]
    human_nums_m = [{"better": 1, "worse": -1, "no_change": 0, "unsure": 0}.get(h, 0) for h in mrs_open_hs]

    r_pseudo = spearman_r(pseudo_ds, human_nums_p) if len(pseudo_ds) >= 3 else 0.0
    agree_pseudo = agreement_rate([d for d, _ in valid_pseudo], pseudo_hs)
    r_mrs_open = spearman_r(mrs_open_ds, human_nums_m) if len(mrs_open_ds) >= 3 else 0.0
    agree_mrs_open = agreement_rate([d for d, _ in valid_mrs_open], mrs_open_hs)

    print(f"{'Variant':<20} {'N':>5} {'Spearman r':>12} {'Agreement':>12}")
    print("-" * 50)
    print(f"{'pseudo_mrs':<20} {len(valid_pseudo):>5} {r_pseudo:>12.4f} {agree_pseudo:>12.4f}")
    print(f"{'MRS Open v0.3.1':<20} {len(valid_mrs_open):>5} {r_mrs_open:>12.4f} {agree_mrs_open:>12.4f}")

    # Per-genre
    print(f"\n{'Genre':<15} {'N':>5} {'Pseudo r':>10} {'Pseudo Agree':>14} {'MRS Open r':>12} {'MRS Open Agree':>16}")
    print("-" * 72)
    for genre in ["electronic", "piano", "vocal", "rock", "ambient"]:
        g = per_genre[genre]
        if not g["pseudo_delta"]:
            continue
        g_ps = g["pseudo_delta"]
        g_hs = g["human"]
        g_hums = [{"better": 1, "worse": -1, "no_change": 0, "unsure": 0}.get(h, 0) for h in g_hs]
        gr_p = spearman_r(g_ps, g_hums) if len(g_ps) >= 3 else 0.0
        ga_p = agreement_rate(g_ps, g_hs)

        g_mo = g.get("mrs_open_delta", [])
        if len(g_mo) >= 3:
            gr_m = spearman_r(g_mo, g_hums[:len(g_mo)]) if len(g_mo) >= 3 else 0.0
            ga_m = agreement_rate(g_mo, g_hs[:len(g_mo)])
            print(f"{genre:<15} {len(g_ps):>5} {gr_p:>10.4f} {ga_p:>14.4f} {gr_m:>12.4f} {ga_m:>16.4f}")
        else:
            print(f"{genre:<15} {len(g_ps):>5} {gr_p:>10.4f} {ga_p:>14.4f} {'N/A':>12} {'N/A':>16}")

    # ── MHP-080: Gate Accuracy ──
    print(f"\n## MHP-080: Gate Accuracy Analysis\n")

    gate_correct = 0
    gate_total = 0
    false_positives = []  # gate rejected/reprocess, human says better
    false_negatives = []  # gate approved, human says worse
    per_genre_gate: Dict[str, Dict[str, int]] = defaultdict(lambda: {"total": 0, "correct": 0, "fp": 0, "fn": 0})

    for row in manifest:
        sid = row["sample_id"]
        genre = row["genre"]
        gate_decision = row.get("gate_decision", "")
        label = label_map.get(sid, {})
        hd = label.get("human_decision", "")
        if not hd:
            continue

        gate_total += 1
        pg = per_genre_gate[genre]
        pg["total"] += 1

        # Gate agreement logic:
        # - human="better" + gate="approve" = correct
        # - human="worse" + gate in ("reject","reprocess") = correct
        # - human="no_change" + gate="approve" = correct
        # - human="better" + gate in ("reject","reprocess") = false positive
        # - human="worse" + gate="approve" = false negative

        if hd == "better":
            if gate_decision == "approve":
                gate_correct += 1
                pg["correct"] += 1
            else:
                pg["fp"] += 1
                false_positives.append({"sample_id": sid, "genre": genre, "gate": gate_decision, "human": hd})
        elif hd == "worse":
            if gate_decision in ("reject", "reprocess"):
                gate_correct += 1
                pg["correct"] += 1
            else:
                pg["fn"] += 1
                false_negatives.append({"sample_id": sid, "genre": genre, "gate": gate_decision, "human": hd})
        elif hd == "no_change":
            if gate_decision == "approve":
                gate_correct += 1
                pg["correct"] += 1
            else:
                pg["fp"] += 1
                false_positives.append({"sample_id": sid, "genre": genre, "gate": gate_decision, "human": hd})

    accuracy = gate_correct / gate_total if gate_total > 0 else 0.0
    print(f"Overall Gate Accuracy: {accuracy:.1%} ({gate_correct}/{gate_total})")
    print(f"False Positives: {len(false_positives)}")
    print(f"False Negatives: {len(false_negatives)}")
    print()

    print(f"{'Genre':<15} {'Total':>6} {'Correct':>8} {'FP':>5} {'FN':>5} {'Accuracy':>10}")
    print("-" * 52)
    for genre in ["electronic", "piano", "vocal", "rock", "ambient"]:
        pg = per_genre_gate[genre]
        if pg["total"] == 0:
            continue
        acc = pg["correct"] / pg["total"]
        print(f"{genre:<15} {pg['total']:>6} {pg['correct']:>8} {pg['fp']:>5} {pg['fn']:>5} {acc:>10.1%}")

    # ── Write outputs ──
    output_dir.mkdir(parents=True, exist_ok=True)

    # FP/FN details
    with (output_dir / "false_positives.jsonl").open("w", encoding="utf-8") as f:
        for fp in false_positives:
            f.write(json.dumps(fp) + "\n")
    with (output_dir / "false_negatives.jsonl").open("w", encoding="utf-8") as f:
        for fn in false_negatives:
            f.write(json.dumps(fn) + "\n")

    # Summary
    summary = {
        "mrs_comparison": {
            "pseudo_mrs": {"n": len(valid_pseudo), "spearman_r": round(r_pseudo, 4), "agreement": round(agree_pseudo, 4)},
            "mrs_open": {"n": len(valid_mrs_open), "spearman_r": round(r_mrs_open, 4), "agreement": round(agree_mrs_open, 4)},
            "per_genre": {
                genre: {
                    "n": len(data["pseudo_delta"]),
                    "pseudo_r": round(spearman_r(data["pseudo_delta"], [{"better":1,"worse":-1,"no_change":0,"unsure":0}.get(h,0) for h in data["human"]]), 4) if len(data["pseudo_delta"]) >= 3 else 0,
                    "pseudo_agree": round(agreement_rate(data["pseudo_delta"], data["human"]), 4),
                }
                for genre, data in per_genre.items() if data["pseudo_delta"]
            },
        },
        "gate_accuracy": {
            "overall": {"accuracy": round(accuracy, 4), "total": gate_total, "correct": gate_correct},
            "false_positives": len(false_positives),
            "false_negatives": len(false_negatives),
            "per_genre": {
                genre: {"total": pg["total"], "correct": pg["correct"],
                        "fp": pg["fp"], "fn": pg["fn"],
                        "accuracy": round(pg["correct"] / pg["total"], 4) if pg["total"] else 0}
                for genre, pg in per_genre_gate.items() if pg["total"]
            },
        },
    }

    summary_path = output_dir / "analysis_summary.json"
    summary_path.write_text(json.dumps(summary, indent=2))
    print(f"\nAnalysis written to: {summary_path}")

    return summary


if __name__ == "__main__":
    calibration_dir = PROJECT / "outputs" / "nem_mrs_002" / "calibration_run"
    output_dir = PROJECT / "reports" / "nem_mrs_002" / "gate_accuracy"
    analyze(calibration_dir, output_dir)
