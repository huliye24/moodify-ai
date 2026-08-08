from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .records import write_jsonl


def _load_optional(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def build_deepseek_pack(evidence_dir: Path, output_dir: Path) -> dict[str, Any]:
    audit = _load_optional(evidence_dir / "audit_summary.json")
    baselines = _load_optional(evidence_dir / "baseline_results.json")
    pilot = _load_optional(evidence_dir / "pilot_summary.json")

    tasks = [
        {
            "task_id": "PWRM-D-001",
            "loop": "annotation_reliability",
            "input_type": "evidence_summary",
            "data": {
                "record_count": audit.get("record_count"),
                "label_counts": audit.get("label_counts", {}),
                "tie_rate": audit.get("tie_rate"),
                "cant_tell_rate": audit.get("cant_tell_rate"),
                "mean_decisive_pair_agreement": audit.get("mean_decisive_pair_agreement"),
            },
            "instruction": "Classify whether annotation reliability is ready, revise, or stop. Cite one decisive reason.",
        },
        {
            "task_id": "PWRM-D-002",
            "loop": "data_integrity",
            "input_type": "evidence_summary",
            "data": {
                "anomaly_count": audit.get("anomaly_count"),
                "track_split_leakage_count": audit.get("track_split_leakage_count"),
                "record_count": audit.get("record_count"),
            },
            "instruction": "Classify the data-integrity gate and name one required next action.",
        },
        {
            "task_id": "PWRM-D-003",
            "loop": "baseline_validation",
            "input_type": "evidence_summary",
            "data": {
                "random": baselines.get("random_baseline", {}),
                "loudness_only": baselines.get("loudness_only", {}),
                "interpretable_acoustic": baselines.get("interpretable_acoustic", {}),
            },
            "instruction": "Decide whether the acoustic baseline beats random and loudness-only evidence without overstating causality.",
        },
        {
            "task_id": "PWRM-D-004",
            "loop": "pilot_gate",
            "input_type": "evidence_summary",
            "data": {
                "pilot": pilot,
                "audit": {
                    "anomaly_count": audit.get("anomaly_count"),
                    "tie_rate": audit.get("tie_rate"),
                    "cant_tell_rate": audit.get("cant_tell_rate"),
                },
            },
            "instruction": "Return one bounded Go, Revise, or Stop recommendation for the pilot only.",
        },
    ]

    schema = {
        "type": "object",
        "additionalProperties": False,
        "required": [
            "task_id",
            "loop",
            "decision",
            "severity",
            "reason",
            "next_action",
            "needs_human_review",
        ],
        "properties": {
            "task_id": {"type": "string"},
            "loop": {"type": "string"},
            "decision": {"enum": ["go", "revise", "stop", "inconclusive"]},
            "severity": {"enum": ["low", "medium", "high"]},
            "reason": {"type": "string", "maxLength": 240},
            "next_action": {"type": "string", "maxLength": 240},
            "needs_human_review": {"type": "boolean"},
        },
    }
    prompt = """You are the Data Worker in the X-AWDJ protocol for Moodify PWRM v0.1.

Process exactly one JSON task. Return one JSON object only.
Use only the supplied evidence summary.
Do not claim to inspect audio, code, files, or raw records.
Do not redefine musical power, acceptance thresholds, or the research question.
Do not infer causality from model accuracy.
If evidence is missing, choose decision=inconclusive.
Copy task_id and loop exactly.
Give one reason and one next action.
Human review is mandatory for go and stop decisions.
"""

    output_dir.mkdir(parents=True, exist_ok=True)
    write_jsonl(output_dir / "tasks.jsonl", tasks)
    (output_dir / "prompt.md").write_text(prompt, encoding="utf-8")
    (output_dir / "expected_output_schema.json").write_text(
        json.dumps(schema, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return {"task_count": len(tasks), "output_dir": str(output_dir)}
