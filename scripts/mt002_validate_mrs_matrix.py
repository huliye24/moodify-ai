#!/usr/bin/env python3
"""Run MT-002's MRS validation matrix against score records."""
from __future__ import annotations

import argparse
import csv
import json
import math
import statistics
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from moodify_runtime.utils import utc_now_iso  # noqa: E402

MRS_VERSION = "mrs_open_v031"
TEST_NAMES = [
    "monotonicity",
    "scale_validation",
    "no_ceiling",
    "v02_v031_correlation",
    "bad_sample_suppression",
    "improvement_reward",
    "loudness_cheat_resistance",
    "stability",
    "hq_damage_sensitivity",
]


def _load_jsonl(path: Path) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                records.append(json.loads(line))
    return records


def _load_manifest(path: Path | None) -> dict[str, dict[str, str]]:
    if path is None:
        return {}
    with path.open("r", encoding="utf-8", newline="") as f:
        return {row.get("task_id", ""): row for row in csv.DictReader(f)}


def _number(value: Any) -> float | None:
    try:
        if value in (None, ""):
            return None
        numeric = float(value)
        return numeric if math.isfinite(numeric) else None
    except Exception:
        return None


def _ranks(values: list[float]) -> list[float]:
    order = sorted(range(len(values)), key=lambda i: values[i])
    ranks = [0.0] * len(values)
    i = 0
    while i < len(order):
        j = i
        while j + 1 < len(order) and values[order[j + 1]] == values[order[i]]:
            j += 1
        rank = (i + j + 2) / 2.0
        for k in range(i, j + 1):
            ranks[order[k]] = rank
        i = j + 1
    return ranks


def _pearson(xs: list[float], ys: list[float]) -> float | None:
    if len(xs) < 2 or len(xs) != len(ys):
        return None
    mx = statistics.fmean(xs)
    my = statistics.fmean(ys)
    num = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    den = math.sqrt(sum((x - mx) ** 2 for x in xs) * sum((y - my) ** 2 for y in ys))
    return num / den if den else None


def _spearman(pairs: list[tuple[float, float]]) -> float | None:
    if len(pairs) < 3:
        return None
    xs = [p[0] for p in pairs]
    ys = [p[1] for p in pairs]
    return _pearson(_ranks(xs), _ranks(ys))


def _result(name: str, status: str, notes: str, **metrics: Any) -> dict[str, Any]:
    return {"name": name, "status": status, "notes": notes, "metrics": metrics}


def _completed(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [r for r in records if r.get("status") == "completed"]


def validate_monotonicity(records: list[dict[str, Any]], _: dict[str, dict[str, str]]) -> dict[str, Any]:
    completed = _completed(records)
    invalid = [r for r in completed if _number(r.get("d_real_after")) is None or _number(r.get("mrs_score")) is None]
    inversions = 0
    checked = 0
    for i, left in enumerate(completed):
        left_d = _number(left.get("d_real_after"))
        left_score = _number(left.get("mrs_score"))
        if left_d is None or left_score is None:
            continue
        for right in completed[i + 1:]:
            right_d = _number(right.get("d_real_after"))
            right_score = _number(right.get("mrs_score"))
            if right_d is None or right_score is None or left_d == right_d:
                continue
            checked += 1
            if (left_d < right_d and left_score <= right_score) or (left_d > right_d and left_score >= right_score):
                inversions += 1
    if invalid:
        return _result("monotonicity", "FAIL", "completed records are missing d_real_after or mrs_score", invalid=len(invalid))
    inversion_rate = inversions / checked if checked else 0.0
    tolerance = 0.005
    status = "PASS" if checked and inversion_rate <= tolerance else "HOLD"
    notes = "MRS ordering follows D_real ordering within rounding tolerance" if status == "PASS" else "MRS ordering has too many inversions"
    return _result("monotonicity", status, notes, pairs_checked=checked, inversions=inversions, inversion_rate=inversion_rate, tolerance=tolerance)


def validate_scale_validation(records: list[dict[str, Any]], _: dict[str, dict[str, str]]) -> dict[str, Any]:
    scores = [_number(r.get("mrs_score")) for r in _completed(records)]
    scores = [s for s in scores if s is not None]
    if len(scores) < 10:
        return _result("scale_validation", "HOLD", "too few completed scores", completed=len(scores))
    median = statistics.median(scores)
    status = "PASS" if 850.0 <= median <= 1150.0 else "HOLD"
    return _result("scale_validation", status, "baseline median remains near the 1000 reference band", median_mrs=median, target=1000, tolerance=150)


def validate_no_ceiling(records: list[dict[str, Any]], _: dict[str, dict[str, str]]) -> dict[str, Any]:
    scores = [_number(r.get("mrs_score")) for r in _completed(records)]
    scores = [s for s in scores if s is not None]
    if not scores:
        return _result("no_ceiling", "FAIL", "no completed numeric scores")
    score_max = max(scores)
    status = "PASS" if score_max > 1000.0 and score_max != 100.0 else "HOLD"
    return _result("no_ceiling", status, "open scale produces scores above the 1000 baseline and has no 0-100 cap", score_max=score_max)


def validate_v02_v031_correlation(records: list[dict[str, Any]], manifest: dict[str, dict[str, str]]) -> dict[str, Any]:
    pairs: list[tuple[float, float]] = []
    for record in _completed(records):
        row = manifest.get(str(record.get("task_id", "")))
        if not row:
            continue
        pseudo = _number(row.get("pseudo_mrs_after"))
        mrs = _number(record.get("mrs_score"))
        if pseudo is not None and mrs is not None:
            pairs.append((pseudo, mrs))
    rho = _spearman(pairs)
    if rho is None:
        return _result("v02_v031_correlation", "HOLD", "no comparable v0.2/pseudo scores available", pairs=len(pairs))
    status = "PASS" if rho >= 0.30 else "HOLD"
    notes = "v0.2/pseudo score ranks track MRS Open" if status == "PASS" else "v0.2/pseudo scores do not yet validate MRS Open ranking"
    return _result("v02_v031_correlation", status, notes, pairs=len(pairs), spearman=rho)


def validate_bad_sample_suppression(records: list[dict[str, Any]], _: dict[str, dict[str, str]]) -> dict[str, Any]:
    completed = _completed(records)
    scores = [_number(r.get("mrs_score")) for r in completed]
    scores = [s for s in scores if s is not None]
    if len(scores) < 10:
        return _result("bad_sample_suppression", "HOLD", "too few completed scores", completed=len(scores))
    median = statistics.median(scores)
    bottom = sorted(completed, key=lambda r: float(r.get("mrs_score") or 0.0))[: max(1, len(completed) // 10)]
    flagged_bottom = sum(1 for r in bottom if r.get("penalty_flags"))
    status = "PASS" if min(scores) < median and flagged_bottom > 0 else "HOLD"
    return _result("bad_sample_suppression", status, "bottom-decile records remain below median and include penalty signal", score_min=min(scores), score_median=median, bottom_records=len(bottom), flagged_bottom=flagged_bottom)


def validate_improvement_reward(records: list[dict[str, Any]], _: dict[str, dict[str, str]]) -> dict[str, Any]:
    deltas = [_number(r.get("mrs_delta")) for r in _completed(records)]
    deltas = [d for d in deltas if d is not None]
    if len(deltas) < 10:
        return _result("improvement_reward", "HOLD", "too few delta records", completed=len(deltas))
    median = statistics.median(deltas)
    positive_rate = sum(1 for d in deltas if d > 0) / len(deltas)
    status = "PASS" if median > 0 and positive_rate >= 0.50 else "HOLD"
    return _result("improvement_reward", status, "processed outputs receive positive median reward when D_real improves", median_delta=median, positive_rate=positive_rate)


def validate_loudness_cheat_resistance(records: list[dict[str, Any]], _: dict[str, dict[str, str]]) -> dict[str, Any]:
    flags = Counter(flag for r in _completed(records) for flag in (r.get("penalty_flags") or []))
    loudness_count = flags.get("loudness_anomaly", 0)
    if loudness_count:
        return _result("loudness_cheat_resistance", "PASS", "loudness anomaly penalty is represented in the batch", loudness_anomaly=loudness_count)
    return _result("loudness_cheat_resistance", "HOLD", "current batch has no loudness-cheat positive controls", loudness_anomaly=0, observed_flags=dict(flags))


def validate_stability(records: list[dict[str, Any]], _: dict[str, dict[str, str]]) -> dict[str, Any]:
    grouped: dict[str, list[float]] = defaultdict(list)
    for record in _completed(records):
        before = _number(record.get("mrs_before"))
        sample = str(record.get("sample_id", ""))
        if before is not None and sample:
            grouped[sample].append(before)
    unstable: dict[str, float] = {}
    for sample, values in grouped.items():
        if len(values) >= 2:
            span = max(values) - min(values)
            if span > 0.05:
                unstable[sample] = span
    status = "PASS" if grouped and not unstable else "HOLD"
    return _result("stability", status, "same input sample keeps stable before-score across presets", samples=len(grouped), unstable_samples=unstable)


def validate_hq_damage_sensitivity(records: list[dict[str, Any]], _: dict[str, dict[str, str]]) -> dict[str, Any]:
    high_quality = [r for r in _completed(records) if (_number(r.get("mrs_before")) or 0.0) >= 1100.0]
    negative = [r for r in high_quality if (_number(r.get("mrs_delta")) or 0.0) < 0.0]
    if not high_quality:
        return _result("hq_damage_sensitivity", "HOLD", "no high-quality input samples in this batch", high_quality_records=0)
    status = "PASS" if negative else "HOLD"
    return _result("hq_damage_sensitivity", status, "high-quality samples can receive negative deltas after processing", high_quality_records=len(high_quality), negative_delta_records=len(negative))


VALIDATORS = [
    validate_monotonicity,
    validate_scale_validation,
    validate_no_ceiling,
    validate_v02_v031_correlation,
    validate_bad_sample_suppression,
    validate_improvement_reward,
    validate_loudness_cheat_resistance,
    validate_stability,
    validate_hq_damage_sensitivity,
]


def _decision(tests: list[dict[str, Any]]) -> str:
    statuses = {test["status"] for test in tests}
    if "FAIL" in statuses:
        return "HOLD"
    return "EXPERIMENTAL"


def _write_markdown(path: Path, result: dict[str, Any]) -> None:
    lines = [
        f"# MT-002 Validation Matrix - {result['run_id']}",
        "",
        f"Generated: {result['generated_at']}",
        "",
        "## Result",
        "",
        f"- Decision: `{result['decision']}`",
        f"- MRS version: `{result['mrs_version']}`",
        f"- Tests: `{result['pass_count']} PASS`, `{result['hold_count']} HOLD`, `{result['fail_count']} FAIL`",
        f"- Score records: `{result['record_count']}`",
        "",
        "## Matrix",
        "",
        "| Test | Status | Notes |",
        "|---|---|---|",
    ]
    for test in result["tests"]:
        lines.append(f"| {test['name']} | `{test['status']}` | {test['notes']} |")
    lines += ["", "## Metrics", ""]
    for test in result["tests"]:
        lines.append(f"### {test['name']}")
        metrics = test.get("metrics") or {}
        if metrics:
            for key, value in metrics.items():
                lines.append(f"- {key}: `{value}`")
        else:
            lines.append("- No extra metrics.")
        lines.append("")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def run_validation(records_path: Path, manifest_path: Path | None, run_id: str) -> dict[str, Any]:
    records = _load_jsonl(records_path)
    manifest = _load_manifest(manifest_path)
    tests = [validator(records, manifest) for validator in VALIDATORS]
    counts = Counter(test["status"] for test in tests)
    return {
        "mrs_version": MRS_VERSION,
        "run_id": run_id,
        "decision": _decision(tests),
        "generated_at": utc_now_iso(),
        "records_path": str(records_path),
        "manifest_path": str(manifest_path) if manifest_path else None,
        "record_count": len(records),
        "pass_count": counts.get("PASS", 0),
        "hold_count": counts.get("HOLD", 0),
        "fail_count": counts.get("FAIL", 0),
        "tests": tests,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Run MT-002 MRS validation matrix")
    parser.add_argument("--records", required=True)
    parser.add_argument("--manifest")
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--output-dir", default="reports/mt002_mrs_validation")
    parser.add_argument("--min-runnable-tests", type=int, default=8)
    parser.add_argument("--fail-on-hold", action="store_true")
    args = parser.parse_args()

    result = run_validation(Path(args.records), Path(args.manifest) if args.manifest else None, args.run_id)
    output_dir = Path(args.output_dir) / args.run_id
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "validation_result.json").write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    _write_markdown(output_dir / "validation_result.md", result)
    print(json.dumps({k: result[k] for k in ["run_id", "mrs_version", "decision", "pass_count", "hold_count", "fail_count", "record_count"]}, ensure_ascii=False, indent=2))

    if len(result["tests"]) < args.min_runnable_tests:
        return 2
    if result["fail_count"]:
        return 3
    if args.fail_on_hold and result["hold_count"]:
        return 4
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
