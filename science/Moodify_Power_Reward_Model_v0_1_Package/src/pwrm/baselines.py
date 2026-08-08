from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from typing import Any

import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, brier_score_loss, log_loss, roc_auc_score
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler


FEATURE_NAMES = [
    "rms_dbFS",
    "crest_db",
    "low_ratio",
    "mid_ratio",
    "high_ratio",
    "transient_strength",
    "clarity_proxy",
]


def _target(record: dict[str, Any]) -> int | None:
    counts = Counter(label.get("preference") for label in record.get("labels", []))
    if counts["A"] == counts["B"]:
        return None
    return 1 if counts["A"] > counts["B"] else 0


def _vector(record: dict[str, Any], feature_names: list[str]) -> list[float]:
    features_a = record["candidate_a"]["features"]
    features_b = record["candidate_b"]["features"]
    return [float(features_a[name]) - float(features_b[name]) for name in feature_names]


def _metrics(y_true: np.ndarray, probabilities: np.ndarray) -> dict[str, float | None]:
    predictions = (probabilities >= 0.5).astype(int)
    return {
        "accuracy": float(accuracy_score(y_true, predictions)),
        "roc_auc": float(roc_auc_score(y_true, probabilities)) if len(set(y_true)) == 2 else None,
        "log_loss": float(log_loss(y_true, probabilities, labels=[0, 1])),
        "brier_score": float(brier_score_loss(y_true, probabilities)),
    }


def train_baselines(records: list[dict[str, Any]], output_dir: Path) -> dict[str, Any]:
    usable = [record for record in records if _target(record) is not None]
    train = [record for record in usable if record["governance"]["dataset_split"] == "train"]
    test = [record for record in usable if record["governance"]["dataset_split"] == "test"]
    if len(train) < 8 or len(test) < 4:
        raise ValueError("baseline training requires at least 8 decisive train and 4 decisive test pairs")

    y_train = np.asarray([_target(record) for record in train], dtype=int)
    y_test = np.asarray([_target(record) for record in test], dtype=int)
    if len(set(y_train)) < 2:
        raise ValueError("training labels contain only one class")

    results: dict[str, Any] = {
        "train_pairs": len(train),
        "test_pairs": len(test),
        "random_baseline": _metrics(y_test, np.full(len(y_test), 0.5)),
    }

    for name, features in (
        ("loudness_only", ["lufs_i"]),
        ("interpretable_acoustic", FEATURE_NAMES),
    ):
        x_train = np.asarray([_vector(record, features) for record in train], dtype=float)
        x_test = np.asarray([_vector(record, features) for record in test], dtype=float)
        model = make_pipeline(
            StandardScaler(),
            LogisticRegression(random_state=0, max_iter=2000),
        )
        model.fit(x_train, y_train)
        probabilities = model.predict_proba(x_test)[:, 1]
        results[name] = {
            "features": features,
            **_metrics(y_test, probabilities),
        }

    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "baseline_results.json").write_text(
        json.dumps(results, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return results
