#!/usr/bin/env python3
"""LUFS_STEREO_REGRESSION_001 - reproduction script.

Read-only. Imports the engine's measurement modules, runs them against
signals whose correct answers are known independently, and prints where the
current tree disagrees. Changes nothing on disk.

    python docs/audits/LUFS_STEREO_REGRESSION_001/reproduce.py

Requires numpy. pyloudnorm is used as the external reference where available;
if it is missing, the F2 section still runs, because that one is decided by
arithmetic rather than by a reference implementation.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import numpy as np

REPO = Path(__file__).resolve().parents[3]
SRC = REPO / "moodify-core-package" / "src"
sys.path.insert(0, str(SRC))

LOUDNESS_PY = SRC / "moodify" / "auditory" / "loudness.py"
METRICS_PY = SRC / "moodify" / "auditory" / "metrics.py"

SEPARATOR = "=" * 72


def banner(text: str) -> None:
    print(f"\n{SEPARATOR}\n{text}\n{SEPARATOR}")


def load_loudness_module():
    spec = importlib.util.spec_from_file_location("audit_loudness", LOUDNESS_PY)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def check_source() -> int:
    """Confirm the divide is still present, by reading the file."""
    banner("1. F1 source check - is the /N normalisation still there?")
    if not LOUDNESS_PY.is_file():
        print(f"  MISSING: {LOUDNESS_PY}")
        return 1
    hits = [
        (number, line)
        for number, line in enumerate(LOUDNESS_PY.read_text(encoding="utf-8").splitlines(), 1)
        if "/ sum(weights)" in line
    ]
    if not hits:
        print("  NOT FOUND - the /N normalisation is gone; this finding is stale.")
        return 1
    for number, line in hits:
        print(f"  {LOUDNESS_PY.name}:{number}")
        print(f"    {line.strip()}")
    print("\n  BS.1770 requires channel powers to be SUMMED (G_i = 1.0).")
    return 0


def build_probes(sr: int, seconds: float = 20.0):
    rng = np.random.default_rng(20261012)
    count = int(sr * seconds)
    t = np.arange(count) / sr
    left = 0.35 * np.sin(2 * np.pi * 440 * t) + 0.10 * rng.standard_normal(count)
    right = 0.30 * np.sin(2 * np.pi * 523.25 * t) + 0.10 * rng.standard_normal(count)
    return {
        "stereo independent": np.stack([left, right], axis=1),
        "stereo dual-mono": np.stack([left, left], axis=1),
        "stereo left only": np.stack([left, np.zeros_like(left)], axis=1),
        "stereo anti-phase": np.stack([left, -left], axis=1),
        "mono": left,
    }


def check_lufs(loudness) -> int:
    banner("2. F1 measurement - integrated LUFS against an independent implementation")
    try:
        import pyloudnorm
    except ImportError:
        print("  SKIPPED: pyloudnorm is not installed.")
        print("  Install it to run this section:  pip install pyloudnorm")
        return 0

    print(f"  {'signal':<24}{'Moodify':>10}{'pyloudnorm':>12}{'diff':>10}")
    worst_stereo = 0.0
    for sr, tag in ((44100, "44.1k"), (48000, "48k")):
        for name, signal in build_probes(sr).items():
            ours = loudness.integrated_loudness_lufs(signal, sr)
            reference = pyloudnorm.Meter(sr).integrated_loudness(
                signal[:, None] if signal.ndim == 1 else signal
            )
            diff = ours - reference
            if not name.endswith("mono") and name != "mono":
                worst_stereo = max(worst_stereo, abs(diff))
            flag = "" if abs(diff) < 0.1 else "   <-- DISAGREES"
            print(f"  {(name + ' @' + tag):<24}{ours:10.3f}{reference:12.3f}{diff:+10.3f}{flag}")

    print()
    if worst_stereo >= 0.1:
        print(f"  FINDING CONFIRMED: stereo disagrees by up to {worst_stereo:.3f} dB,")
        print("  while the mono probe agrees. Mono is unaffected because its divisor is 1 -")
        print("  which is exactly why a mono-only test suite never caught this.")
    else:
        print("  No disagreement above 0.1 dB; this finding appears to be resolved.")
    return 0


def check_peak_rms() -> int:
    banner("3. F2 - sample peak and RMS are measured on a mono downmix")
    from moodify.auditory.metrics import compute_metrics  # noqa: PLC0415

    sr = 44100
    count = sr * 5
    t = np.arange(count) / sr
    left = 0.9 * np.sin(2 * np.pi * 220 * t)
    anti_phase = np.stack([left, -left], axis=1)

    class Probe:  # compute_metrics only reads these three attributes
        duration = count / sr
        sample_rate = sr
        channels = 2

    reported = compute_metrics(anti_phase, sr, Probe())

    correct_peak = 20 * np.log10(np.max(np.abs(anti_phase)))
    correct_rms = 20 * np.log10(np.sqrt(np.mean(anti_phase ** 2)))
    downmix_peak = np.max(np.abs(anti_phase.mean(axis=1)))

    print("  signal: anti-phase stereo (L = -R), 5 s @ 44.1 kHz")
    print(f"  {'metric':<26}{'engine':>12}{'correct':>12}")
    print(f"  {'true_peak_dbfs':<26}{reported['true_peak_dbfs']['value']:>12.2f}{correct_peak:>12.2f}"
          "   (engine is per-channel here)")
    print(f"  {'sample_peak_dbfs':<26}{reported['sample_peak_dbfs']['value']:>12.2f}{correct_peak:>12.2f}")
    print(f"  {'rms_dbfs':<26}{reported['rms_dbfs']['value']:>12.2f}{correct_rms:>12.2f}")
    print(f"  {'crest_factor_db':<26}{reported['crest_factor_db']['value']:>12.2f}"
          f"{correct_peak - correct_rms:>12.2f}")
    print(f"  {'plr_db':<26}{reported['plr_db']['value']:>12.2f}"
          f"{reported['true_peak_dbfs']['value'] - correct_rms:>12.2f}")
    print()
    print(f"  mono downmix max |L+R|/2 = {downmix_peak:.6f}")
    print("  Anti-phase content cancels completely in the sum, so a signal at nearly")
    print("  full scale is reported as silence. This is not a bias; it is a failure.")

    if reported["rms_dbfs"]["value"] < -100:
        print("\n  FINDING CONFIRMED.")
        return 0
    print("\n  Not reproduced; F2 appears to be resolved.")
    return 0


def main() -> int:
    print(f"repository: {REPO}")
    loudness = load_loudness_module()
    check_source()
    check_lufs(loudness)
    check_peak_rms()
    banner("Summary")
    print("  F1  stereo LUFS low by ~3 dB   - see section 2")
    print("  F2  peak/RMS on mono downmix   - see section 3")
    print("  F3  crest factor false positive follows from F2")
    print()
    print("  No files were modified by this script.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
