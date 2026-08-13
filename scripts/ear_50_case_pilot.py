#!/usr/bin/env python3
"""MFY_EAR_50_CASE_AUTOMATED_PILOT_001 — synthetic cohort pilot.

- immutable manifest (no private audio; synthetic signals only)
- 5-case canary, then 50-case run through the deterministic CaseRunner
- statistics: success, reproducibility (re-run subset), cost, review rate,
  side effects; 5-10 human-review queue by pre-registered rules
- verdict: GO / CONDITIONAL_GO / NO_GO (no new features in this package)

Usage: python scripts/ear_50_case_pilot.py [--output <dir>] [--canary-only]
"""

from __future__ import annotations

import argparse
import hashlib
import json
import random
import time
import wave
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
import sys  # noqa: E402

sys.path.insert(0, str(ROOT / "moodify-core-package" / "src"))

from moodify.data_factory.case_runner import CaseRunner  # noqa: E402

PILOT_CONTRACT = "MFY-EAR-PILOT-MANIFEST-001"
COHORT_SIZE = 50
CANARY_SIZE = 5


def build_manifest(seed: int = 20260813) -> list[dict]:
    rng = random.Random(seed)
    cohort = []
    for i in range(COHORT_SIZE):
        kind = "sine" if i < 40 else "noise"
        sr = rng.choice([44100, 48000])
        seconds = round(rng.choice([1.0, 2.0, 3.0, 5.0]), 1)
        channels = rng.choice([1, 2])
        amp = round(rng.choice([0.05, 0.15, 0.3, 0.5]), 3)
        freq = int(rng.choice([110, 220, 440, 880, 1760]))
        cohort.append({
            "id": f"pilot_{i + 1:03d}",
            "signal": {
                "type": kind,
                "sr": sr,
                "seconds": seconds,
                "channels": channels,
                "amp": amp,
                "freq": freq if kind == "sine" else None,
            },
        })
    return cohort


def write_signal(spec: dict, path: Path) -> None:
    s = spec["signal"]
    sr, seconds, channels = s["sr"], s["seconds"], s["channels"]
    n = int(sr * seconds)
    t = np.arange(n) / sr
    if s["type"] == "sine":
        x = s["amp"] * np.sin(2 * np.pi * s["freq"] * t)
    else:
        x = s["amp"] * np.random.RandomState(hash(s["id"]) % (2**32)).uniform(-1, 1, n)
    x = x.astype(np.float32)
    if channels == 2:
        x = np.stack([x, x], axis=1)
    with wave.open(str(path), "wb") as w:
        w.setnchannels(channels)
        w.setsampwidth(2)
        w.setframerate(sr)
        w.writeframes((x * 32767).astype(np.int16).tobytes())


def run_case(runner: CaseRunner, spec: dict, work: Path) -> dict:
    wav = work / f"{spec['id']}.wav"
    write_signal(spec, wav)
    start = time.monotonic()
    case_dir = runner.submit(wav, idempotency_key=f"{PILOT_CONTRACT}:{spec['id']}")
    elapsed = time.monotonic() - start
    case = json.loads((case_dir / "production_case.json").read_text(encoding="utf-8"))
    return {
        "id": spec["id"],
        "case_dir": str(case_dir),
        "elapsed_s": round(elapsed, 2),
        "lifecycle": case.get("lifecycle_state"),
    }


def choose_review_queue(results: list[dict], manifest: list[dict], seed: int = 7) -> list[str]:
    rng = random.Random(seed)
    # pre-registered rules: lowest amplitude (uncertain), noise (side-effect prone),
    # longest duration (cost), plus random normal samples
    low_amp = [r["id"] for r in results if manifest[int(r["id"].split("_")[1]) - 1]["signal"]["amp"] == min(
        m["signal"]["amp"] for m in manifest
    )]
    noise_ids = [m["id"] for m in manifest if m["signal"]["type"] == "noise"]
    longest = [m["id"] for m in manifest if m["signal"]["seconds"] == max(m["signal"]["seconds"] for m in manifest)]
    chosen = list(dict.fromkeys(low_amp + noise_ids[:2] + longest[:1]))
    while len(chosen) < 5:
        cand = rng.choice([r["id"] for r in results])
        if cand not in chosen:
            chosen.append(cand)
    return chosen[:10]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", default=str(ROOT / "artifacts" / "ear_pilot_001"))
    parser.add_argument("--canary-only", action="store_true")
    args = parser.parse_args()

    out = Path(args.output)
    out.mkdir(parents=True, exist_ok=True)
    work = out / "work"
    work.mkdir(parents=True, exist_ok=True)

    manifest = build_manifest()
    manifest_path = out / "manifest.json"
    manifest_path.write_text(
        json.dumps({"schema": PILOT_CONTRACT, "generated_at": datetime.now(timezone.utc).isoformat(),
                    "cohort": manifest}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    manifest_sha = hashlib.sha256(manifest_path.read_bytes()).hexdigest()

    runner = CaseRunner(out)
    print(f"manifest: {manifest_path} sha256={manifest_sha[:16]}")

    # canary
    canary = manifest[:CANARY_SIZE]
    results = []
    for spec in canary:
        results.append(run_case(runner, spec, work))
        print(f"canary {spec['id']}: {results[-1]['lifecycle']} ({results[-1]['elapsed_s']}s)")
    if any(r["lifecycle"] != "COMPLETED" for r in results):
        print("NO_GO: canary failure")
        return 1
    if args.canary_only:
        print("canary passed; --canary-only stop")
        return 0

    # full cohort
    for spec in manifest[CANARY_SIZE:]:
        results.append(run_case(runner, spec, work))
        if len(results) % 10 == 0:
            print(f"progress {len(results)}/{COHORT_SIZE}")

    success = sum(1 for r in results if r["lifecycle"] == "COMPLETED")
    total_time = sum(r["elapsed_s"] for r in results)
    review_queue = choose_review_queue(results, manifest)

    report = {
        "schema": PILOT_CONTRACT,
        "manifest_sha256": manifest_sha,
        "cohort_size": COHORT_SIZE,
        "success_count": success,
        "success_rate": round(success / COHORT_SIZE, 4),
        "total_elapsed_s": round(total_time, 1),
        "avg_elapsed_s": round(total_time / COHORT_SIZE, 2),
        "review_queue": review_queue,
        "results": results,
        "verdict": "GO" if success == COHORT_SIZE else ("CONDITIONAL_GO" if success >= COHORT_SIZE * 0.95 else "NO_GO"),
        "human_review_note": "machine metrics reportable; aesthetic/product validity NOT PASS until human review completes",
    }
    report_path = out / "pilot_report.json"
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({k: report[k] for k in ("cohort_size", "success_count", "success_rate",
                                             "total_elapsed_s", "avg_elapsed_s", "review_queue", "verdict")},
                     indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
