"""Golden cases for N-track ranking (DSK-MFY-NTRACK-RANKER-001).

Deterministic synthetic WAV candidates (fixed RNG seed) exercise the
seven required scenarios end to end through the real scan pipeline.
Run: python -m moodify.evaluation.ntrack.golden
Output: outputs/ntrack_golden/golden_summary.json
"""

from __future__ import annotations

import json
import math
import random
import struct
import sys
import wave
from pathlib import Path

from moodify.evaluation.ntrack.service import record_human_ranking, run_ntrack_ranking

RNG_SEED = 7
OUT_DIR = Path(__file__).resolve().parents[4] / "outputs" / "ntrack_golden"


def _write_tone(path: Path, seconds: float = 2.0, gain: float = 1.0,
                freq: float = 440.0, rate: int = 48000, noise: float = 0.0) -> None:
    rng = random.Random(RNG_SEED)
    with wave.open(str(path), "wb") as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(rate)
        frames = bytearray()
        for i in range(int(rate * seconds)):
            value = 12000 * gain * math.sin(2 * math.pi * freq * i / rate)
            if noise > 0:
                value += (rng.random() - 0.5) * 2.0 * noise * 12000
            value = max(-32768, min(32767, int(value)))
            frames += struct.pack("<h", value)
        wav.writeframes(bytes(frames))


def _write_corrupt(path: Path) -> None:
    path.write_bytes(b"NOT_A_WAV" * 256)


def _case_root(tmp: Path, name: str) -> Path:
    root = tmp / name
    root.mkdir(parents=True, exist_ok=True)
    return root


def golden_clear_top3(tmp: Path) -> dict:
    """ALBUM_10_CLEAR_TOP3: 10 tracks, 3 clearly strong."""
    tracks = []
    for i in range(10):
        p = tmp / f"clear_top3_{i}.wav"
        if i < 3:
            _write_tone(p, gain=0.35, freq=440.0 + i * 30, noise=0.002)  # near -14 LUFS, clean
        else:
            _write_tone(p, gain=1.0 + i * 0.15, freq=200.0 + i * 50, noise=0.01 * (i + 1))
        tracks.append(p)
    result = run_ntrack_ranking("GC-1", _case_root(tmp, "clear_top3"), tracks, top_k=3)
    top3 = [c["candidate_id"] for c in result["ranking"][:3]]
    ok = result["eligible_count"] == 10 and len(top3) == 3
    return {"name": "ALBUM_10_CLEAR_TOP3", "ok": ok,
            "top3_ids": top3, "eligible": result["eligible_count"],
            "top3_membership_conf": [c["confidence"] for c in result["ranking"][:3]]}


def golden_tied_middle(tmp: Path) -> dict:
    """ALBUM_12_TIED_MIDDLE: 12 tracks, middle 3 near-identical."""
    tracks = []
    for i in range(12):
        p = tmp / f"tied_middle_{i}.wav"
        if 4 <= i <= 6:
            _write_tone(p, gain=0.35, freq=440.0, noise=0.002)  # near-identical middle
        else:
            _write_tone(p, gain=0.30 + 0.02 * i, freq=300.0 + i * 25, noise=0.002 + 0.001 * i)
        tracks.append(p)
    result = run_ntrack_ranking("GC-2", _case_root(tmp, "tied_middle"), tracks, top_k=3)
    ok = len(result["tie_bands"]) >= 1
    return {"name": "ALBUM_12_TIED_MIDDLE", "ok": ok,
            "tie_bands": result["tie_bands"],
            "ranking_ids": [c["candidate_id"] for c in result["ranking"]]}


def golden_redundant_top(tmp: Path) -> dict:
    """ALBUM_REDUNDANT_TOP_TRACKS: top 2 sonic twins displace in album mode."""
    tracks = []
    for i in range(6):
        p = tmp / f"redundant_top_{i}.wav"
        if i == 0:
            _write_tone(p, gain=0.35, freq=440.0, noise=0.002)
        elif i == 1:
            # Sonic twin: near-identical profile, distinct bytes (no dup gate).
            _write_tone(p, gain=0.35, freq=441.0, noise=0.002)
        elif i in (2, 3):
            _write_tone(p, gain=0.36, freq=2200.0 if i == 2 else 900.0, noise=0.002)
        else:
            _write_tone(p, gain=0.15, freq=300.0 + (i - 4) * 20, noise=0.002)
        tracks.append(p)
    case_root = _case_root(tmp, "redundant_top")
    result = run_ntrack_ranking("GC-3", case_root, tracks,
                                mode="ALBUM_SELECTION", top_k=3)
    raw_top = [c["candidate_id"] for c in result["ranking"]]
    album_ids = list(result["album_rerank"]["selected_candidate_ids"])
    candidates = json.loads((case_root / "05_ntrack" / "candidates.json").read_text(encoding="utf-8"))
    hashes = {c["ranking_candidate_id"]: c["source_hash"] for c in candidates["candidates"]}
    twins = sorted(raw_top[:2], key=lambda cid: hashes[cid])
    ok = (
        hashes[raw_top[0]] != hashes[raw_top[1]]  # twins distinct bytes
        and album_ids != raw_top[:3]  # album order differs from raw strength
        and album_ids[0] == raw_top[0]  # quality floor: strongest stays on top
        and any("redundancy" in explanation for explanation in result["album_rerank"]["explanations"])
    )
    return {"name": "ALBUM_REDUNDANT_TOP_TRACKS", "ok": ok,
            "twins_hash_distinct": hashes[raw_top[0]] != hashes[raw_top[1]],
            "raw_top_ids": raw_top, "album_selected_ids": album_ids,
            "explanations": list(result["album_rerank"]["explanations"])}


def golden_partial_failure(tmp: Path) -> dict:
    """PARTIAL_ANALYSIS_FAILURE: one corrupt track isolated."""
    tracks = []
    for i in range(5):
        p = tmp / f"partial_failure_{i}.wav"
        if i == 3:
            _write_corrupt(p)
        else:
            _write_tone(p, gain=0.3 + 0.08 * i, freq=400.0 + i * 40, noise=0.003)
        tracks.append(p)
    result = run_ntrack_ranking("GC-4", _case_root(tmp, "partial_failure"), tracks, top_k=3)
    ok = result["failed_count"] == 1 and result["eligible_count"] == 4 and len(result["ranking"]) == 4
    return {"name": "PARTIAL_ANALYSIS_FAILURE", "ok": ok,
            "eligible": result["eligible_count"], "failed": result["failed_count"],
            "ranking_ids": [c["candidate_id"] for c in result["ranking"]]}


def golden_n_equals_2(tmp: Path) -> dict:
    """N_EQUALS_2: 2-track case delegates to pairwise comparison."""
    a = tmp / "n2_a.wav"
    b = tmp / "n2_b.wav"
    _write_tone(a, gain=0.35, freq=440.0, noise=0.002)
    _write_tone(b, gain=1.6, freq=440.0, noise=0.01)
    result = run_ntrack_ranking("GC-5", _case_root(tmp, "n_equals_2"), [a, b], top_k=1)
    ok = result["eligible_count"] == 2 and result["pairwise_edge_count"] >= 1 and len(result["ranking"]) == 2
    return {"name": "N_EQUALS_2", "ok": ok,
            "pairwise_edge_count": result["pairwise_edge_count"],
            "ranking_ids": [c["candidate_id"] for c in result["ranking"]]}


def golden_human_reorder(tmp: Path) -> dict:
    """HUMAN_REORDER: human edit persisted with derived preferences."""
    tracks = []
    for i in range(5):
        p = tmp / f"human_reorder_{i}.wav"
        _write_tone(p, gain=0.3 + 0.1 * i, freq=350.0 + i * 45, noise=0.003 + 0.001 * i)
        tracks.append(p)
    case_root = _case_root(tmp, "human_reorder")
    result = run_ntrack_ranking("GC-6", case_root, tracks, top_k=3)
    machine_order = [c["candidate_id"] for c in result["ranking"]]
    human_order = list(reversed(machine_order))
    human = record_human_ranking(case_root, "GC-6", human_order, top_k=3)
    ok = human["derived_preference_count"] >= 1
    return {"name": "HUMAN_REORDER", "ok": ok,
            "derived_preference_count": human["derived_preference_count"],
            "machine_first": machine_order[0], "human_first": human_order[0]}


def golden_top5_boundary(tmp: Path) -> dict:
    """TOP5_BOUNDARY_UNCERTAIN: 5th/6th tracks near-identical."""
    tracks = []
    for i in range(8):
        p = tmp / f"top5_boundary_{i}.wav"
        if i in (4, 5):
            _write_tone(p, gain=0.36, freq=480.0, noise=0.002)  # near-identical boundary pair
        else:
            _write_tone(p, gain=0.2 + 0.06 * i, freq=320.0 + i * 55, noise=0.002 + 0.002 * i)
        tracks.append(p)
    result = run_ntrack_ranking("GC-7", _case_root(tmp, "top5_boundary"), tracks, top_k=5)
    boundary = [c for c in result["ranking"] if c["rank"] in (5, 6)]
    ok = any(c["confidence"] == "LOW" for c in boundary) or len(result["tie_bands"]) >= 1
    return {"name": "TOP5_BOUNDARY_UNCERTAIN", "ok": ok,
            "boundary_confidence": [(c["candidate_id"], c["confidence"]) for c in boundary],
            "tie_bands": result["tie_bands"]}


def run_all() -> list[dict]:
    tmp = OUT_DIR / "cases"
    if tmp.exists():
        import shutil
        shutil.rmtree(tmp)
    tmp.mkdir(parents=True, exist_ok=True)
    cases = [
        golden_clear_top3(tmp),
        golden_tied_middle(tmp),
        golden_redundant_top(tmp),
        golden_partial_failure(tmp),
        golden_n_equals_2(tmp),
        golden_human_reorder(tmp),
        golden_top5_boundary(tmp),
    ]
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    summary = {"task": "DSK-MFY-NTRACK-RANKER-001", "rng_seed": RNG_SEED, "cases": cases}
    (OUT_DIR / "golden_summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    return cases


def main() -> int:
    cases = run_all()
    ok = all(c["ok"] for c in cases)
    for case in cases:
        print(f"{case['name']}: ok={case['ok']}")
    print(f"GOLDEN: {'ALL PASS' if ok else 'FAILURES PRESENT'} -> outputs/ntrack_golden/golden_summary.json")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
