"""Layered test gates for Moodify (DSK-MFY-ORDER-BEAUTY-022 Stage D).

Layers:
- collect : full collection must succeed (exit 0, zero collection errors)
- fast    : no external binaries, no real audio — safe on every change
- core    : domain, services, CLI/API contracts
- integration : may require explicit environment conditions; skips must be auditable

Usage:
  python tools/test_gates.py [layer...]   (default: collect fast core integration)
Exit code 0 if all requested layers pass, 1 otherwise.
"""

from __future__ import annotations

import json
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

LAYERS: dict[str, tuple[str, ...]] = {
    "collect": ("--collect-only", "-q"),
    "fast": (
        "-q",
        "--ignore=tests/v2",
        "--ignore=tests/test_transcription.py",
        "--ignore=tests/test_transcription_stems.py",
        "-m", "not v01 and not legacy and not experimental",
    ),
    "core": (
        "-q",
        "tests/v2",
        "-m", "not v01 and not legacy and not experimental",
    ),
    "integration": (
        "-q",
        "tests/test_transcription.py",
        "tests/test_transcription_stems.py",
        "-m", "not v01",
    ),
}


def run_layer(name: str, args: tuple[str, ...]) -> dict:
    t0 = time.perf_counter()
    proc = subprocess.run(
        [sys.executable, "-m", "pytest", *args],
        cwd=ROOT, capture_output=True, text=True,
    )
    elapsed = time.perf_counter() - t0
    tail = proc.stdout.splitlines()[-1] if proc.stdout else proc.stderr.splitlines()[-1] if proc.stderr else ""
    return {
        "layer": name,
        "exit_code": proc.returncode,
        "elapsed_s": round(elapsed, 2),
        "summary": tail,
    }


def main() -> int:
    requested = sys.argv[1:] or list(LAYERS)
    results = []
    failed = 0
    for name in requested:
        if name not in LAYERS:
            print(f"ERROR: unknown layer {name!r}; valid: {', '.join(LAYERS)}")
            return 2
        result = run_layer(name, LAYERS[name])
        results.append(result)
        status = "PASS" if result["exit_code"] == 0 else "FAIL"
        if result["exit_code"] != 0:
            failed += 1
        print(f"  [{status}] {result['layer']:12s} {result['elapsed_s']:6.2f}s  {result['summary']}")

    evidence_dir = ROOT / "docs" / "testing" / "gates"
    evidence_dir.mkdir(parents=True, exist_ok=True)
    stamp = time.strftime("%Y%m%dT%H%M%S")
    manifest = {
        "schema": "test-gates/0.1",
        "python": sys.version.split()[0],
        "stamp": stamp,
        "results": results,
    }
    target = evidence_dir / f"gates_{stamp}.json"
    target.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\n  evidence: {target}")
    print(f"  overall: {'PASS' if failed == 0 else f'{failed} FAILED'}")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
