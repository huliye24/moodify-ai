"""V2 vs V3 auditory comparison for the real song (AIR-001).

Compares the user's final versions against the shared source:
  - CANDIDATE-V2: V2_Audacity_Final.wav
  - CANDIDATE-V3: V3_DeepEar_Audacity_Final.wav

Reuses the existing before-scan evidence from the real-song case.
"""

from __future__ import annotations

import json
from pathlib import Path

from moodify.auditory.profiles import get_profile
from moodify.auditory.service import compare_scans, load_scan_evidence, scan_audio

SONG_DIR = Path("pre-music/Vieillir et devenir nouveau avec toi")
SOURCE = SONG_DIR / "Vieillir et devenir nouveau avec toi.wav"
V2 = SONG_DIR / "moodify_delivery_v2/final/Vieillir et devenir nouveau avec toi_V2_Audacity_Final.wav"
V3 = SONG_DIR / "moodify_delivery_v2/final/Vieillir et devenir nouveau avec toi_V3_DeepEar_Audacity_Final.wav"

BASE = Path("outputs/real_song_case")
CASE_ID = "MFY-CASE-REAL-SONG-001"
BEFORE_DIR = BASE / "cases" / CASE_ID / "01_before_scan"


def main() -> int:
    BASE.mkdir(parents=True, exist_ok=True)
    case_root = BASE / "cases" / CASE_ID
    profile = get_profile("MFY-WSE-SCAN-PROFILE-001")

    before = load_scan_evidence(BEFORE_DIR, profile)
    print(f"before scan reused: lufs={before.metrics['integrated_lufs']['value']}")

    plan = {
        "case_id": CASE_ID, "plan_version": "1.0", "plan_id": "V2V3-PLAN",
        "observations": [], "artistic_intent_notes": ["vocal clarity"],
        "technical_goals": [{
            "goal_id": "G_PRESENCE", "metric": "presence_2000_5000_hz",
            "desired_direction": "INCREASE", "minimum_meaningful_change": 0.005,
        }],
        "guardrails": [
            {"guardrail_id": "NO_NEW_CLIPPING", "metric": "clipping_sample_count",
             "comparator": "EQUAL", "threshold": 0, "severity": "BLOCKING"},
            {"guardrail_id": "PRESERVE_DYNAMICS", "metric": "crest_factor_db",
             "comparator": "BASELINE_DELTA_GE", "threshold": -3.0, "severity": "WARNING"},
        ],
        "approved_by": "user", "approved_at": None,
    }

    results = {}
    for cid, cpath in (("CANDIDATE-V2-FINAL", V2), ("CANDIDATE-V3-DEEPEAR", V3)):
        print(f"scanning {cid} ...")
        scan_audio(CASE_ID, "after", cpath, case_root / "06_after_scans" / cid, profile)
        after = load_scan_evidence(case_root / "06_after_scans" / cid, profile)
        compare_scans(before, after, plan, case_root / "05_comparison" / cid,
                      case_id=CASE_ID, candidate_id=cid,
                      source_sha256=before.metrics["source_sha256"]["value"],
                      candidate_sha256="")
        report = json.loads(
            (case_root / "05_comparison" / cid / "comparison_report.json").read_text(encoding="utf-8")
        )
        results[cid] = report

    # ---- summary table ----
    bands = ["sub_20_60_hz", "bass_60_120_hz", "low_mid_120_250_hz", "mid_250_500_hz",
             "core_mid_500_2000_hz", "presence_2000_5000_hz", "brilliance_5000_10000_hz",
             "air_10000_16000_hz"]
    lines = ["# V2 vs V3 听觉对比（响度归一化）", ""]
    lines.append("| 指标 | V2 | V3 |")
    lines.append("|---|---:|---:|")
    for cid, report in results.items():
        j = report["judgment"]
        norm = report["normalization"]
        lines[1] += ""  # placeholder

    summary = {}
    for cid, report in results.items():
        j = report["judgment"]
        norm = report["normalization"]
        summary[cid] = {
            "technical_assessment": j["technical_assessment"],
            "workflow_decision": j["workflow_decision"],
            "goals_met": j["goals_met"],
            "risk_flags": [f["code"] for f in j["risk_flags"]],
            "normalization_gain_db": norm["normalization_gain_db"],
            "after_lufs": report["metrics_delta"]["integrated_lufs"]["after"],
            "crest_after": report["metrics_delta"]["crest_factor_db"]["after"],
            "normalized_band_deltas": {
                b: report["normalized_band_deltas"].get(b) for b in bands
            },
        }

    print("\n========== V2 vs V3 ==========")
    print(f"{'指标':<24}{'V2':>12}{'V3':>12}")
    print("-" * 50)
    for key in ("technical_assessment", "workflow_decision", "normalization_gain_db", "after_lufs"):
        print(f"{key:<24}{str(summary['CANDIDATE-V2-FINAL'][key]):>12}{str(summary['CANDIDATE-V3-DEEPEAR'][key]):>12}")
    print(f"{'goals_met':<24}{str(summary['CANDIDATE-V2-FINAL']['goals_met']):>12}{str(summary['CANDIDATE-V3-DEEPEAR']['goals_met']):>12}")
    print(f"{'risk_flags':<24}{str(summary['CANDIDATE-V2-FINAL']['risk_flags']):>12}{str(summary['CANDIDATE-V3-DEEPEAR']['risk_flags']):>12}")
    print("\n归一化频段 delta (after-before, 响度匹配后):")
    print(f"{'band':<24}{'V2':>10}{'V3':>10}")
    print("-" * 46)
    for b in bands:
        v2 = summary["CANDIDATE-V2-FINAL"]["normalized_band_deltas"].get(b)
        v3 = summary["CANDIDATE-V3-DEEPEAR"]["normalized_band_deltas"].get(b)
        def fmt(v):
            return f"{v:+.4f}" if isinstance(v, (int, float)) else "-"
        print(f"{b:<24}{fmt(v2):>10}{fmt(v3):>10}")

    (BASE / "v2v3_summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print("\n->", BASE / "v2v3_summary.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
