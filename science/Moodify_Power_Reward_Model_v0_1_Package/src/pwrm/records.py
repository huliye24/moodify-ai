from __future__ import annotations

import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Iterable

from jsonschema import Draft202012Validator


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            if not line.strip():
                continue
            try:
                value = json.loads(line)
            except json.JSONDecodeError as exc:
                raise ValueError(f"{path}:{line_number}: invalid JSON: {exc}") from exc
            if not isinstance(value, dict):
                raise ValueError(f"{path}:{line_number}: record must be an object")
            records.append(value)
    return records


def write_jsonl(path: Path, records: Iterable[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for record in records:
            handle.write(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n")


def validate_record(record: dict[str, Any], schema: dict[str, Any]) -> list[str]:
    validator = Draft202012Validator(schema)
    errors = sorted(validator.iter_errors(record), key=lambda error: list(error.path))
    messages = []
    for error in errors:
        location = ".".join(str(part) for part in error.path) or "$"
        messages.append(f"{location}: {error.message}")
    return messages


def _label_summary(labels: list[dict[str, Any]]) -> Counter:
    return Counter(str(label.get("preference", "")) for label in labels)


def audit_records(
    records: list[dict[str, Any]],
    schema: dict[str, Any],
    *,
    loudness_delta_max: float = 0.2,
    true_peak_ceiling_dbtp: float = -1.0,
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    anomalies: list[dict[str, Any]] = []
    pair_ids: set[str] = set()
    track_splits: dict[str, set[str]] = defaultdict(set)
    label_totals: Counter = Counter()
    decisive_agreements: list[float] = []

    for index, record in enumerate(records):
        pair_id = str(record.get("pair_id", f"row-{index}"))
        for message in validate_record(record, schema):
            anomalies.append({"pair_id": pair_id, "kind": "schema", "message": message})

        if pair_id in pair_ids:
            anomalies.append({"pair_id": pair_id, "kind": "duplicate_pair_id"})
        pair_ids.add(pair_id)

        source = record.get("source", {})
        governance = record.get("governance", {})
        track_id = str(source.get("track_id", ""))
        split = str(governance.get("dataset_split", ""))
        if track_id and split:
            track_splits[track_id].add(split)

        constraints = record.get("constraints", {})
        if abs(float(constraints.get("lufs_delta", 999.0))) > loudness_delta_max:
            anomalies.append({"pair_id": pair_id, "kind": "loudness_delta_exceeded"})

        for side in ("candidate_a", "candidate_b"):
            candidate = record.get(side, {})
            features = candidate.get("features", {})
            if float(features.get("true_peak_dbTP", 999.0)) > true_peak_ceiling_dbtp:
                anomalies.append({"pair_id": pair_id, "kind": "true_peak_exceeded", "side": side})

        labels = list(record.get("labels", []))
        counts = _label_summary(labels)
        label_totals.update(counts)
        decisive = counts["A"] + counts["B"]
        if decisive:
            decisive_agreements.append(max(counts["A"], counts["B"]) / decisive)

    leakage = {track: sorted(splits) for track, splits in track_splits.items() if len(splits) > 1}
    for track_id, splits in leakage.items():
        anomalies.append(
            {
                "track_id": track_id,
                "kind": "track_split_leakage",
                "splits": splits,
            }
        )

    total_labels = sum(label_totals.values())
    summary = {
        "record_count": len(records),
        "unique_pair_count": len(pair_ids),
        "track_count": len(track_splits),
        "anomaly_count": len(anomalies),
        "track_split_leakage_count": len(leakage),
        "label_counts": dict(label_totals),
        "tie_rate": label_totals["tie"] / total_labels if total_labels else None,
        "cant_tell_rate": label_totals["cant_tell"] / total_labels if total_labels else None,
        "mean_decisive_pair_agreement": (
            sum(decisive_agreements) / len(decisive_agreements)
            if decisive_agreements
            else None
        ),
    }
    return summary, anomalies
