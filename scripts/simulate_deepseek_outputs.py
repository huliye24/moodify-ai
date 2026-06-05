"""Simulate DeepSeek v4 outputs for testing the validate→select pipeline.

This generates mock worker responses so the AEP worker protocol can be tested
end-to-end without calling the DeepSeek API.

Part of ECHAIN-MOODIFY-DATA-LOOP-014 / MHP-797.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

# Simulated DeepSeek v4 decisions — one per task line, following the output contract.
# Generated based on the actual data signals in the summary.
SIMULATED_OUTPUTS: list[dict] = [
    # Runtime task — fatal error detected.
    {
        "task_id": "20260605_000141:runtime",
        "loop": "runtime_reliability",
        "severity": "high",
        "reason": "Fatal FileNotFoundError for daily_run.log blocks operator review and auto-report generation.",
        "next_action": "Add daily_run.log existence check at phase start; emit log or skip with warning.",
        "needs_human_review": False,
    },
    # Craft task — wide_space on piano triggered over_dark. Negative delta is mild.
    {
        "task_id": "TASK_SMP_58C86AEACFD2BF8D_wide_space:craft",
        "loop": "craft_preset_selection",
        "severity": "medium",
        "reason": "wide_space on piano triggered over_dark. Delta is small and negative — preset may be too dark for this class.",
        "next_action": "Down-rank wide_space for piano class; test bright_master as substitute.",
        "needs_human_review": False,
    },
    # Score calibration — warm_vocal has massive sign disagreement (pseudo -20 vs open +83).
    {
        "task_id": "TASK_SMP_D2536D072BD30E33_warm_vocal:score",
        "loop": "scoring_calibration",
        "severity": "high",
        "reason": "Extreme sign disagreement: pseudo MRS dropped 20 points while MRS Open gained 83. Calibration is broken.",
        "next_action": "Flag warm_vocal preset for calibration review; log disagreement for MRS weight tuning.",
        "needs_human_review": True,
    },
    # Score calibration — clean_master has mild sign disagreement (pseudo +1.7 vs open -0.1).
    {
        "task_id": "TASK_SMP_D2536D072BD30E33_clean_master:score",
        "loop": "scoring_calibration",
        "severity": "medium",
        "reason": "Mild sign disagreement: pseudo delta +1.75 vs MRS Open delta -0.1. Both magnitudes are very small.",
        "next_action": "Log as low-priority calibration note; no threshold change needed yet.",
        "needs_human_review": False,
    },
    # Craft task — clean_master on vocal_folk triggered over_dark with near-zero delta.
    {
        "task_id": "TASK_SMP_D2536D072BD30E33_clean_master:craft",
        "loop": "craft_preset_selection",
        "severity": "medium",
        "reason": "clean_master on vocal_folk triggered over_dark. Delta near zero — preset may add darkness without gain.",
        "next_action": "Block clean_master for vocal_folk; test warm_vocal or wide_space as replacements.",
        "needs_human_review": False,
    },
    # Score calibration — wide_space also has massive sign disagreement (pseudo -18 vs open +82).
    {
        "task_id": "TASK_SMP_D2536D072BD30E33_wide_space:score",
        "loop": "scoring_calibration",
        "severity": "high",
        "reason": "Extreme sign disagreement: pseudo MRS dropped 18 points while MRS Open gained 82. Same pattern as warm_vocal.",
        "next_action": "Group warm_vocal and wide_space calibrations into one MHP; both show same pseudo-vs-open gap.",
        "needs_human_review": True,
    },
    # Operator report — summary assessment.
    {
        "task_id": "20260605_000141:operator",
        "loop": "operator_report",
        "severity": "medium",
        "reason": "Run completed with 4 tasks, 0 failures, but has 3 scoring disagreements, 2 flagged presets, and 1 fatal error.",
        "next_action": "HOLD batch. Fix daily_run.log fatal error, run scoring calibration, then re-evaluate craft flags.",
        "needs_human_review": True,
    },
]


def write_outputs(path: Path) -> int:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for item in SIMULATED_OUTPUTS:
            f.write(json.dumps(item, ensure_ascii=False, sort_keys=True) + "\n")
    print(f"Wrote {len(SIMULATED_OUTPUTS)} simulated outputs to {path}")
    return 0


def main(argv: list[str] | None = None) -> int:
    if argv is None:
        argv = sys.argv[1:]
    if not argv:
        print("Usage: python3 scripts/simulate_deepseek_outputs.py <output_dir>", file=sys.stderr)
        return 1
    out_dir = Path(argv[0])
    return write_outputs(out_dir / "model_outputs.jsonl")


if __name__ == "__main__":
    raise SystemExit(main())
