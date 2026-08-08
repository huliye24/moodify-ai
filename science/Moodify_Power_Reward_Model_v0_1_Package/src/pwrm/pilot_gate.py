from __future__ import annotations

from typing import Any


DEFAULT_THRESHOLDS = {
    "min_records": 20,
    "min_decisive_labels": 40,
    "max_anomalies": 0,
    "max_track_split_leakage": 0,
    "min_mean_decisive_pair_agreement": 0.67,
    "max_tie_rate": 0.35,
    "max_cant_tell_rate": 0.20,
}


def evaluate_pilot(
    audit: dict[str, Any], thresholds: dict[str, float] | None = None
) -> dict[str, Any]:
    limits = {**DEFAULT_THRESHOLDS, **(thresholds or {})}
    labels = audit.get("label_counts", {})
    decisive = int(labels.get("A", 0)) + int(labels.get("B", 0))
    checks = {
        "record_count": int(audit.get("record_count", 0)) >= limits["min_records"],
        "decisive_label_count": decisive >= limits["min_decisive_labels"],
        "anomaly_count": int(audit.get("anomaly_count", 0)) <= limits["max_anomalies"],
        "track_split_leakage_count": int(audit.get("track_split_leakage_count", 0))
        <= limits["max_track_split_leakage"],
        "agreement": (audit.get("mean_decisive_pair_agreement") or 0)
        >= limits["min_mean_decisive_pair_agreement"],
        "tie_rate": (audit.get("tie_rate") if audit.get("tie_rate") is not None else 1)
        <= limits["max_tie_rate"],
        "cant_tell_rate": (
            audit.get("cant_tell_rate") if audit.get("cant_tell_rate") is not None else 1
        )
        <= limits["max_cant_tell_rate"],
    }
    hard_failures = {
        key for key in ("anomaly_count", "track_split_leakage_count") if not checks[key]
    }
    decision = "stop" if hard_failures else ("go" if all(checks.values()) else "revise")
    return {
        "decision": decision,
        "checks": checks,
        "thresholds": limits,
        "observed": {
            "record_count": audit.get("record_count", 0),
            "decisive_label_count": decisive,
            "anomaly_count": audit.get("anomaly_count", 0),
            "track_split_leakage_count": audit.get("track_split_leakage_count", 0),
            "mean_decisive_pair_agreement": audit.get("mean_decisive_pair_agreement"),
            "tie_rate": audit.get("tie_rate"),
            "cant_tell_rate": audit.get("cant_tell_rate"),
        },
        "note": "Thresholds are preregistered engineering hypotheses for v0.1, not established scientific facts.",
    }
