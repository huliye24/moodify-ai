"""Pairwise judge golden cases (DSK-MFY-PAIRWISE-JUDGE-001).

Deterministic synthesis covering the six required golden scenarios:
CLEAR_A_WIN / CLEAR_B_WIN / NEAR_TIE / A_ANALYSIS_FAILURE /
B_ANALYSIS_FAILURE / HUMAN_OVERRIDE. Reproducible: same RNG seed, same
assets, same hashes. Output: outputs/pairwise_golden/golden_summary.json
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import soundfile as sf

from moodify.evaluation.pairwise.policy import DecisionPolicy
from moodify.evaluation.pairwise.service import record_human_decision, run_pairwise_judge

BASE = Path("outputs/pairwise_golden")
SR = 48000
RNG_SEED = 7


def _synth_clean(rng: np.random.Generator, seconds: float = 6.0) -> np.ndarray:
    t = np.arange(int(SR * seconds)) / SR
    return (
        0.25 * np.sin(2 * np.pi * 55 * t)
        + 0.2 * np.sin(2 * np.pi * 220 * t)
        + 0.15 * np.sin(2 * np.pi * 880 * t)
        + 0.05 * np.sin(2 * np.pi * 6000 * t)
        + 0.01 * rng.standard_normal(len(t))
    ).astype(np.float32)


def _synth_clipped(clean: np.ndarray, gain: float = 1.8) -> np.ndarray:
    return np.clip(clean * gain, -1.0, 1.0).astype(np.float32)


def _synth_loud(clean: np.ndarray, db: float = 1.0) -> np.ndarray:
    return (clean * (10 ** (db / 20))).astype(np.float32)


def _write_corrupt(path: Path) -> None:
    """Write a non-audio file so decode/analysis genuinely fails."""
    path.write_bytes(b"NOT_A_WAV_FILE\x00\x01\x02" * 512)


def _run_case(name: str, case_id: str, a: np.ndarray, b: np.ndarray, rng) -> dict:
    case_dir = BASE / "cases" / case_id
    a_path = BASE / f"{name}_a.wav"
    b_path = BASE / f"{name}_b.wav"
    sf.write(a_path, a, SR)
    sf.write(b_path, b, SR)
    return run_pairwise_judge(
        case_id=case_id,
        case_root=case_dir,
        candidate_a_path=a_path,
        candidate_b_path=b_path,
        policy=DecisionPolicy(),
    )


def _run_case_with_corrupt(name: str, case_id: str, corrupt_side: str, other: np.ndarray, rng) -> dict:
    case_dir = BASE / "cases" / case_id
    a_path = BASE / f"{name}_a.wav"
    b_path = BASE / f"{name}_b.wav"
    sf.write(b_path, other, SR)
    if corrupt_side == "A":
        _write_corrupt(a_path)
        sf.write(b_path, other, SR)
    else:
        sf.write(a_path, other, SR)
        _write_corrupt(b_path)
    return run_pairwise_judge(
        case_id=case_id,
        case_root=case_dir,
        candidate_a_path=a_path,
        candidate_b_path=b_path,
        policy=DecisionPolicy(),
    )


def main() -> None:
    BASE.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(RNG_SEED)
    clean = _synth_clean(rng)

    results: dict[str, dict] = {}

    # 1. CLEAR_A_WIN: A clean, B clipped
    results["CLEAR_A_WIN"] = _run_case("clear_a", "PW-GOLDEN-001", clean, _synth_clipped(clean), rng)

    # 2. CLEAR_B_WIN: reverse
    results["CLEAR_B_WIN"] = _run_case("clear_b", "PW-GOLDEN-002", _synth_clipped(clean), clean, rng)

    # 3. NEAR_TIE: ±1 dB loudness difference only
    near_a = _synth_loud(clean, 1.0)
    near_b = _synth_loud(clean, 0.0)
    results["NEAR_TIE"] = _run_case("near_tie", "PW-GOLDEN-003", near_a, near_b, rng)

    # 4. A_ANALYSIS_FAILURE: corrupt candidate A
    results["A_ANALYSIS_FAILURE"] = _run_case_with_corrupt("a_failure", "PW-GOLDEN-004", "A", clean, rng)

    # 5. B_ANALYSIS_FAILURE: corrupt candidate B
    results["B_ANALYSIS_FAILURE"] = _run_case_with_corrupt("b_failure", "PW-GOLDEN-005", "B", clean, rng)

    # 6. HUMAN_OVERRIDE: judge then override to the opposite side
    base = _run_case("human_override", "PW-GOLDEN-006", clean, _synth_clipped(clean), rng)
    machine_outcome = base["outcome"]
    override = "CHOOSE_B" if machine_outcome == "A_WINS" else "CHOOSE_A"
    human = record_human_decision(
        case_root=BASE / "cases" / "PW-GOLDEN-006",
        pairwise_case_id="PW-GOLDEN-006",
        decision=override,
        machine_outcome=machine_outcome,
        machine_confidence=base["confidence_level"],
        override_reason="golden case: human override",
    )
    results["HUMAN_OVERRIDE"] = {
        "machine": base,
        "human_decision": human["human_decision"],
        "preference_record": human["preference_record"],
    }

    summary = {
        "task": "DSK-MFY-PAIRWISE-JUDGE-001",
        "rng_seed": RNG_SEED,
        "cases": results,
    }
    summary_path = BASE / "golden_summary.json"
    summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"GOLDEN_COMPLETED: {summary_path}")


if __name__ == "__main__":
    main()
