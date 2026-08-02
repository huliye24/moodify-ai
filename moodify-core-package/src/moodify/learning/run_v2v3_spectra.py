"""Full V2/V3 spectrum comparison for the real song (AIR-001).

Scans every V2/V3 candidate under moodify_delivery_v2/final against the
shared source, renders linear/log spectrograms + delta spectrograms,
and produces a numerical band-change table so the spectral changes are
visible both visually and numerically.
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np

from moodify.auditory.comparison import build_delta_spectrograms
from moodify.auditory.profiles import get_profile
from moodify.auditory.service import load_scan_evidence, scan_audio

SONG_DIR = Path("pre-music/Vieillir et devenir nouveau avec toi")
SOURCE = SONG_DIR / "Vieillir et devenir nouveau avec toi.wav"
FINAL = SONG_DIR / "moodify_delivery_v2/final"

CANDIDATES = [
    ("V2-GENTLE", FINAL / "Vieillir et devenir nouveau avec toi_V2_Gentle_Master.wav"),
    ("V2-AUDACITY-FINAL", FINAL / "Vieillir et devenir nouveau avec toi_V2_Audacity_Final.wav"),
    ("V2-FINAL-MASTER", FINAL / "Vieillir et devenir nouveau avec toi_V2_Final_Master.flac"),
    ("V3-DEEPEAR-FINAL", FINAL / "Vieillir et devenir nouveau avec toi_V3_DeepEar_Audacity_Final.wav"),
    ("V3-NETEASE", FINAL / "Vieillir et devenir nouveau avec toi_NETEASE_UPLOAD_V3_DEEPEAR_FINAL.flac"),
]

BASE = Path("outputs/real_song_v2v3_spectra")
CASE_ID = "MFY-CASE-SPECTRA-V2V3"
BEFORE_DIR = Path("outputs/real_song_case/cases/MFY-CASE-REAL-SONG-001/01_before_scan")

BANDS = ["sub_20_60_hz", "bass_60_120_hz", "low_mid_120_250_hz", "mid_250_500_hz",
         "core_mid_500_2000_hz", "presence_2000_5000_hz", "brilliance_5000_10000_hz",
         "air_10000_16000_hz"]


def main() -> int:
    BASE.mkdir(parents=True, exist_ok=True)
    case_root = BASE / "cases" / CASE_ID
    (case_root / "deltas").mkdir(parents=True, exist_ok=True)
    profile = get_profile("MFY-WSE-SCAN-PROFILE-001")

    before = load_scan_evidence(BEFORE_DIR, profile)
    print(f"before: lufs={before.metrics['integrated_lufs']['value']}")

    results = {}
    for cid, cpath in CANDIDATES:
        print(f"scanning {cid} ...")
        scan_audio(CASE_ID, "after", cpath, case_root / "after_scans" / cid, profile)
        after = load_scan_evidence(case_root / "after_scans" / cid, profile)
        # delta spectrogram vs source (loudness-normalized)
        gain = before.metrics["integrated_lufs"]["value"] - after.metrics["integrated_lufs"]["value"]
        build_delta_spectrograms(
            before.arrays, after.arrays, gain_db=gain,
            out_linear=case_root / "deltas" / f"{cid}_delta_linear.png",
            out_log=case_root / "deltas" / f"{cid}_delta_log.png",
        )
        results[cid] = after
        print(f"  done: lufs={after.metrics['integrated_lufs']['value']} "
              f"presence={after.metrics['presence_2000_5000_hz']['value']}")

    # V2 vs V3 direct delta (V3 - V2, normalized to V2 loudness)
    v2 = results["V2-AUDACITY-FINAL"]
    v3 = results["V3-DEEPEAR-FINAL"]
    gain_v3_v2 = v2.metrics["integrated_lufs"]["value"] - v3.metrics["integrated_lufs"]["value"]
    build_delta_spectrograms(
        v2.arrays, v3.arrays, gain_db=gain_v3_v2,
        out_linear=case_root / "deltas" / "V3_minus_V2_delta_linear.png",
        out_log=case_root / "deltas" / "V3_minus_V2_delta_log.png",
    )
    print("V3_minus_V2 delta rendered")

    # ---- numerical table ----
    print("\n========== 频段变化（相对源，响度归一化） ==========")
    header = f"{'band':<24}" + "".join(f"{c:<18}" for c, _ in CANDIDATES)
    print(header)
    print("-" * len(header))
    table = {}
    for band in BANDS:
        row = []
        for cid, _ in CANDIDATES:
            after = results[cid]
            b_before = before.metrics[f"band_energy_{band}"]["value"]
            b_after = after.metrics[f"band_energy_{band}"]["value"]
            g = before.metrics["integrated_lufs"]["value"] - after.metrics["integrated_lufs"]["value"]
            gain2 = 10 ** (2 * g / 20)
            total_b = sum(before.metrics[f"band_energy_{b}"]["value"] for b in BANDS) + 1e-12
            total_a = sum(after.metrics[f"band_energy_{b}"]["value"] for b in BANDS) + 1e-12
            b_ratio = b_before / total_b
            a_norm_ratio = (b_after * gain2) / (total_a * gain2 + 1e-12)
            row.append(a_norm_ratio - b_ratio)
        table[band] = {c: round(row[i], 4) for i, (c, _) in enumerate(CANDIDATES)}
        print(f"{band:<24}" + "".join(f"{table[band][c]:+.4f}      " for c, _ in CANDIDATES))

    # ---- V3 vs V2 direct differences ----
    print("\n========== V3 - V2 直接差异（频段比例，未归一化） ==========")
    print(f"{'band':<24}{'V3-V2':>12}")
    for band in BANDS:
        d = results["V3-DEEPEAR-FINAL"].metrics[band]["value"] - results["V2-AUDACITY-FINAL"].metrics[band]["value"]
        print(f"{band:<24}{d:+.6f}")

    summary = {"before_lufs": before.metrics["integrated_lufs"]["value"],
               "candidates": {cid: {"lufs": r.metrics["integrated_lufs"]["value"],
                                    "presence": r.metrics["presence_2000_5000_hz"]["value"]}
                              for cid, r in results.items()},
               "normalized_band_deltas": table,
               "spectra_dir": str(case_root)}
    (BASE / "v2v3_spectra_summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print("\n->", BASE / "v2v3_spectra_summary.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
