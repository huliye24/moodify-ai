#!/usr/bin/env python3
"""MHP-073: Grid-search calibration for pseudo-MRS weights.

Optimizes the four sub-score weights (peak, rms, crest, dc_offset) by
grid-searching over the weight space and selecting the combination that
maximizes agreement with human preference labels.

Usage:
    python3 scripts/calibrate_pseudo_mrs.py [--data data/calibration/labels.jsonl]
"""

from __future__ import annotations

import json
import math
import sys
from itertools import product
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from moodify_runtime.metrics import analyze_wav_stdlib


def _safe_float(x: Any) -> Optional[float]:
    try:
        v = float(x)
        return v if math.isfinite(v) else None
    except Exception:
        return None


def pseudo_mrs_with_weights(
    metrics: Dict[str, Any],
    w_peak: float,
    w_rms: float,
    w_crest: float,
    w_dc: float,
) -> Optional[float]:
    """Compute pseudo-MRS with custom weights (must sum to ~1.0)."""
    if not metrics.get("supported"):
        return None

    rms = _safe_float(metrics.get("rms"))
    peak = _safe_float(metrics.get("peak"))
    crest = _safe_float(metrics.get("crest_factor"))
    dc = abs(_safe_float(metrics.get("dc_offset")) or 0.0)

    if rms is None or peak is None or crest is None:
        return None

    peak_score = max(0.0, min(1.0, 1.0 - max(0.0, peak - 0.98) * 10.0))
    rms_score = max(0.0, min(1.0, 1.0 - abs(rms - 0.12) / 0.20))
    crest_score = max(0.0, min(1.0, 1.0 - abs(crest - 8.0) / 12.0))
    dc_score = max(0.0, min(1.0, 1.0 - dc * 100.0))

    total = w_peak + w_rms + w_crest + w_dc
    if total <= 0:
        return None
    w_peak /= total
    w_rms /= total
    w_crest /= total
    w_dc /= total

    return 100.0 * (w_peak * peak_score + w_rms * rms_score
                    + w_crest * crest_score + w_dc * dc_score)


def spearman_r(xs: List[float], ys: List[float]) -> float:
    """Spearman rank correlation without scipy/numpy dependency."""
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
    mean_ry = (n + 1) / 2.0

    num = sum((rx[i] - mean_rx) * (ry[i] - mean_ry) for i in range(n))
    den_x = math.sqrt(sum((rx[i] - mean_rx) ** 2 for i in range(n)))
    den_y = math.sqrt(sum((ry[i] - mean_ry) ** 2 for i in range(n)))
    if den_x * den_y == 0:
        return 0.0
    return num / (den_x * den_y)


def agreement_rate(
    before_scores: List[float],
    after_scores: List[float],
    human_decisions: List[str],
) -> float:
    """% of pairs where MRS delta sign matches human 'better'/'worse'."""
    if not before_scores:
        return 0.0
    matches = 0
    total = 0
    for b, a, h in zip(before_scores, after_scores, human_decisions):
        if b is None or a is None:
            continue
        delta = a - b
        total += 1
        if (delta > 0 and h == "better") or (delta < 0 and h == "worse"):
            matches += 1
        elif delta == 0 and h == "no_change":
            matches += 1
    return matches / total if total > 0 else 0.0


def grid_search(
    pairs: List[Dict[str, Any]],
    weight_space: Dict[str, List[float]],
) -> List[Dict[str, Any]]:
    """Grid search over weight combinations.

    Each pair must have: before_metrics, after_metrics, human_decision.
    """
    results = []
    peak_w = weight_space["peak"]
    rms_w = weight_space["rms"]
    crest_w = weight_space["crest"]
    dc_w = weight_space["dc"]

    for wp, wr, wc, wd in product(peak_w, rms_w, crest_w, dc_w):
        total = wp + wr + wc + wd
        if abs(total - 1.0) > 0.001:
            continue

        before_scores = []
        after_scores = []
        human_decisions = []

        for pair in pairs:
            bm = pair.get("before_metrics") or {}
            am = pair.get("after_metrics") or {}
            b = pseudo_mrs_with_weights(bm, wp, wr, wc, wd)
            a = pseudo_mrs_with_weights(am, wp, wr, wc, wd)
            before_scores.append(b)
            after_scores.append(a)
            human_decisions.append(pair.get("human_decision", ""))

        # Score this weight combination
        deltas = [(a - b) if (a is not None and b is not None) else None
                  for a, b in zip(after_scores, before_scores)]
        valid_deltas = [d for d in deltas if d is not None]
        valid_humans = [human_decisions[i] for i, d in enumerate(deltas) if d is not None]

        # Map human decisions to numeric: better=+1, worse=-1, no_change=0
        human_map = {"better": 1.0, "worse": -1.0, "no_change": 0.0, "unsure": 0.0}
        human_nums = [human_map.get(h, 0.0) for h in valid_humans]

        r = spearman_r(valid_deltas, human_nums) if len(valid_deltas) >= 3 else 0.0
        agree = agreement_rate(before_scores, after_scores, human_decisions)

        results.append({
            "weights": {"peak": wp, "rms": wr, "crest": wc, "dc": wd},
            "spearman_r": round(r, 4),
            "agreement_rate": round(agree, 4),
            "score": round(r * 0.6 + agree * 0.4, 4),  # composite
            "n_pairs": len(valid_deltas),
        })

    results.sort(key=lambda x: x["score"], reverse=True)
    return results


def load_pairs_from_audio_dir(
    before_dir: Path,
    after_dir: Path,
    labels_path: Optional[Path] = None,
) -> List[Dict[str, Any]]:
    """Build pairs from before/after WAV directories with optional labels."""
    pairs = []
    labels = {}
    if labels_path and labels_path.exists():
        for line in labels_path.read_text(encoding="utf-8").strip().splitlines():
            if line.strip():
                labels.update(json.loads(line) if isinstance(json.loads(line), dict) else {})

    before_files = sorted(before_dir.glob("*.wav"))
    for bf in before_files:
        af = after_dir / bf.name
        pair = {
            "sample_id": bf.stem,
            "before_metrics": analyze_wav_stdlib(bf),
            "after_metrics": analyze_wav_stdlib(af) if af.exists() else {},
            "human_decision": labels.get(bf.stem, {}).get("human_decision", ""),
        }
        pairs.append(pair)
    return pairs


def main():
    import argparse
    ap = argparse.ArgumentParser(description="Calibrate pseudo-MRS weights via grid search")
    ap.add_argument("--data", default="", help="Path to labels.jsonl")
    ap.add_argument("--before-dir", default="", help="Before WAV directory")
    ap.add_argument("--after-dir", default="", help="After WAV directory")
    ap.add_argument("--top-k", type=int, default=5, help="Show top K results")
    ap.add_argument("--json", action="store_true", help="Output JSON")
    args = ap.parse_args()

    # ── Weight space ──
    weight_space = {
        "peak":  [0.10, 0.15, 0.20, 0.25, 0.30, 0.35, 0.40],
        "rms":   [0.10, 0.15, 0.20, 0.25, 0.30, 0.35, 0.40],
        "crest": [0.15, 0.20, 0.25, 0.30, 0.35, 0.40, 0.50],
        "dc":    [0.05, 0.10, 0.15, 0.20],
    }

    # ── Load data ──
    pairs: List[Dict[str, Any]] = []
    if args.before_dir and args.after_dir:
        pairs = load_pairs_from_audio_dir(
            Path(args.before_dir), Path(args.after_dir),
            Path(args.data) if args.data else None,
        )

    # If no real data, use synthetic sanity-check pairs
    if not pairs:
        print("# No labeled pairs provided — running synthetic sanity check")
        pairs = _synthetic_pairs()

    print(f"# Pairs: {len(pairs)}")
    print(f"# Weight combinations to test: ~{len(weight_space['peak']) * len(weight_space['rms']) * len(weight_space['crest']) * len(weight_space['dc'])}")
    print()

    # ── Run grid search ──
    results = grid_search(pairs, weight_space)

    # ── Default weights for comparison ──
    default_before = []
    default_after = []
    default_humans = []
    for pair in pairs:
        bm = pair.get("before_metrics") or {}
        am = pair.get("after_metrics") or {}
        # Use the actual pseudo_mrs function from metrics.py
        from moodify_runtime.metrics import pseudo_mrs
        default_before.append(pseudo_mrs(bm))
        default_after.append(pseudo_mrs(am))
        default_humans.append(pair.get("human_decision", ""))

    default_deltas = [(a - b) if (a is not None and b is not None) else None
                      for a, b in zip(default_after, default_before)]
    valid_default = [d for d in default_deltas if d is not None]
    valid_h = [default_humans[i] for i, d in enumerate(default_deltas) if d is not None]
    human_map = {"better": 1.0, "worse": -1.0, "no_change": 0.0, "unsure": 0.0}
    human_nums = [human_map.get(h, 0.0) for h in valid_h]
    default_r = spearman_r(valid_default, human_nums) if len(valid_default) >= 3 else 0.0
    default_agree = agreement_rate(default_before, default_after, default_humans)

    print(f"## Default weights (0.25, 0.25, 0.35, 0.15)")
    print(f"  Spearman r: {default_r:.4f}")
    print(f"  Agreement:  {default_agree:.4f}")
    print()

    print(f"## Top {args.top_k} Calibrated Weights")
    print(f"{'Rank':<5} {'Peak':<8} {'RMS':<8} {'Crest':<8} {'DC':<8} {'r':<10} {'Agree':<10} {'Score':<10}")
    print("-" * 70)
    for i, r in enumerate(results[:args.top_k]):
        w = r["weights"]
        print(f"{i+1:<5} {w['peak']:<8.2f} {w['rms']:<8.2f} {w['crest']:<8.2f} {w['dc']:<8.2f} "
              f"{r['spearman_r']:<10.4f} {r['agreement_rate']:<10.4f} {r['score']:<10.4f}")

    best = results[0]
    print()
    print(f"## Best weights: peak={best['weights']['peak']:.2f}, rms={best['weights']['rms']:.2f}, "
          f"crest={best['weights']['crest']:.2f}, dc={best['weights']['dc']:.2f}")
    print(f"  Composite score: {best['score']:.4f} (r={best['spearman_r']:.4f}, agree={best['agreement_rate']:.4f})")
    print(f"  Default → Calibrated delta: r {default_r:.4f}→{best['spearman_r']:.4f}, agree {default_agree:.4f}→{best['agreement_rate']:.4f}")

    if args.json:
        print(json.dumps({"default": {"r": default_r, "agreement": default_agree},
                          "best": best, "top_k": results[:args.top_k]}, indent=2))


def _synthetic_pairs() -> List[Dict[str, Any]]:
    """Generate synthetic metric pairs for sanity-checking the grid search."""
    pairs = []
    # Simulate 10 pairs with known patterns
    for i in range(10):
        # "Better" samples: improved rms and crest
        if i < 6:
            bm = {"supported": True, "rms": 0.08 + i * 0.005, "peak": 0.85,
                  "crest_factor": 5.0 + i * 0.3, "dc_offset": 0.001, "sample_rate": 44100,
                  "channels": 2, "sample_width_bytes": 2, "frame_count": 100000}
            am = {"supported": True, "rms": 0.12, "peak": 0.90,
                  "crest_factor": 7.5, "dc_offset": 0.0005, "sample_rate": 44100,
                  "channels": 2, "sample_width_bytes": 2, "frame_count": 100000}
            pairs.append({"sample_id": f"better_{i}", "before_metrics": bm, "after_metrics": am,
                          "human_decision": "better"})
        else:
            bm = {"supported": True, "rms": 0.12, "peak": 0.88,
                  "crest_factor": 7.0, "dc_offset": 0.001, "sample_rate": 44100,
                  "channels": 2, "sample_width_bytes": 2, "frame_count": 100000}
            am = {"supported": True, "rms": 0.07, "peak": 0.95,
                  "crest_factor": 3.5, "dc_offset": 0.003, "sample_rate": 44100,
                  "channels": 2, "sample_width_bytes": 2, "frame_count": 100000}
            pairs.append({"sample_id": f"worse_{i}", "before_metrics": bm, "after_metrics": am,
                          "human_decision": "worse"})
    return pairs


if __name__ == "__main__":
    main()
