"""Measurement authority registry (MFY-PHASE1-DEPTH-001).

Machine-readable registry of every Phase-I metric: authority class,
definition, method, reference basis, tolerance, policies and honest
limitations. The YAML is the single source of truth; this module loads
and validates it.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

DEFAULT_REGISTRY_PATH = Path(__file__).resolve().parents[3] / "configs" / "measurement_registry_v1.yaml"

AUTHORITY_CLASSES = {
    "STANDARD_COMPLIANT", "DETERMINISTIC_PHYSICAL", "SPECTRAL_DESCRIPTOR",
    "ESTIMATOR", "PROXY",
}


def load_registry(path: str | Path = DEFAULT_REGISTRY_PATH) -> dict[str, Any]:
    data = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    entries = {k: v for k, v in data.items() if k not in {"schema_version", "algorithm_version"}}
    errors = []
    for metric_id, entry in entries.items():
        if entry.get("authority_class") not in AUTHORITY_CLASSES:
            errors.append(f"{metric_id}: invalid authority_class")
        for field in ("display_name", "unit", "definition", "method", "tolerance"):
            if field not in entry:
                errors.append(f"{metric_id}: missing {field}")
    if errors:
        raise ValueError("registry validation failed: " + "; ".join(errors))
    return {"schema_version": data["schema_version"],
            "algorithm_version": data["algorithm_version"],
            "metrics": entries}


def registry_summary(registry: dict[str, Any]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for entry in registry["metrics"].values():
        cls = entry["authority_class"]
        counts[cls] = counts.get(cls, 0) + 1
    return counts
