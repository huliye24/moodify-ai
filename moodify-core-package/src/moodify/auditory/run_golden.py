"""Golden case runner (DSK-MFY-AUDITORY-SCAN-001).

Generates the synthetic source + candidate, runs the full evidence loop
through the service layer, and writes the complete bundle to
outputs/auditory_golden/. Reproducible: same assets, same hashes.
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import soundfile as sf

from moodify.auditory.profiles import get_profile
from moodify.auditory.service import (
    compare_scans,
    load_scan_evidence,
    register_candidate,
    scan_audio,
)

BASE = Path("outputs/auditory_golden")
CASE_ID = "MFY-CASE-GOLDEN-001"
CANDIDATE_ID = "GOLDEN-001"
SR = 48000


def main() -> None:
    BASE.mkdir(parents=True, exist_ok=True)
    profile = get_profile("MFY-WSE-SCAN-PROFILE-001")

    # 1. synthetic source + candidate (deterministic RNG)
    rng = np.random.default_rng(7)
    t = np.arange(SR * 12) / SR
    src = (
        0.25 * np.sin(2 * np.pi * 55 * t)
        + 0.2 * np.sin(2 * np.pi * 220 * t)
        + 0.15 * np.sin(2 * np.pi * 880 * t)
        + 0.05 * np.sin(2 * np.pi * 6000 * t)
        + 0.01 * rng.standard_normal(len(t))
    )
    src = np.stack([src, src * 0.98], axis=1).astype(np.float32)
    cand = np.clip(src + 0.08 * np.sin(2 * np.pi * 4000 * t)[:, None], -1, 1).astype(np.float32)
    source_path = BASE / "golden_source.wav"
    candidate_path = BASE / "golden_candidate.wav"
    sf.write(source_path, src, SR)
    sf.write(candidate_path, cand, SR)

    # 2. before scan
    before_dir = BASE / "cases" / CASE_ID / "01_before_scan"
    scan_audio(CASE_ID, "before", source_path, before_dir, profile)
    print("AUDITORY_BEFORE_SCAN_COMPLETED")

    # 3. candidate registration
    reg_dir = BASE / "cases" / CASE_ID / "03_processing" / "candidates"
    candidate = register_candidate(
        case_id=CASE_ID, candidate_id=CANDIDATE_ID, source_case_id=CASE_ID,
        candidate_path=candidate_path, parent_source_sha256="",
        producing_application="synthetic", processing_method="SYNTHETIC_PRESENCE_LIFT",
        registry_path=reg_dir,
    )
    print("CANDIDATE_REGISTERED", candidate.candidate_sha256[:12])

    # 4. after scan
    after_dir = BASE / "cases" / CASE_ID / "04_after_scan"
    scan_audio(CASE_ID, "after", candidate_path, after_dir, profile)
    print("AUDITORY_AFTER_SCAN_COMPLETED")

    # 5. plan (presence goal + no-clipping guardrail)
    plan = {
        "case_id": CASE_ID, "plan_version": "1.0", "plan_id": "GOLDEN-PLAN-001",
        "observations": [], "artistic_intent_notes": [],
        "technical_goals": [{
            "goal_id": "INCREASE_PRESENCE",
            "metric": "presence_2000_5000_hz",
            "desired_direction": "INCREASE",
            "minimum_meaningful_change": 0.01,
            "rationale": "vocal presence lift",
        }],
        "guardrails": [{
            "guardrail_id": "NO_NEW_CLIPPING",
            "metric": "clipping_sample_count",
            "comparator": "EQUAL", "threshold": 0, "severity": "BLOCKING",
        }],
        "approved_by": "golden", "approved_at": None,
    }
    (BASE / "plan.json").write_text(json.dumps(plan, ensure_ascii=False, indent=2), encoding="utf-8")

    # 6. comparison
    before = load_scan_evidence(before_dir, profile)
    after = load_scan_evidence(after_dir, profile)
    cmp_dir = BASE / "cases" / CASE_ID / "05_comparison"
    result = compare_scans(
        before, after, plan, cmp_dir,
        case_id=CASE_ID, candidate_id=CANDIDATE_ID,
        source_sha256=candidate.parent_source_sha256 or before.metrics["source_sha256"]["value"],
        candidate_sha256=candidate.candidate_sha256,
    )
    j = result["judgment"]
    print(f"AUDITORY_COMPARISON_COMPLETED {j.technical_assessment}/{j.workflow_decision}")

    # 7. evidence verification (re-hash all artifacts)
    from moodify.auditory.manifests import verify_manifest_hashes
    problems = []
    for manifest in [
        before_dir / "scan_manifest.json",
        after_dir / "scan_manifest.json",
        cmp_dir / "comparison_manifest.json",
    ]:
        problems += verify_manifest_hashes(json.loads(manifest.read_text(encoding="utf-8")))
    if problems:
        print("EVIDENCE_VERIFICATION_FAILED", problems)
        return 1
    print("EVIDENCE_VERIFIED")

    summary = {
        "case_id": CASE_ID,
        "candidate_id": CANDIDATE_ID,
        "source_sha256": candidate.source_case_id and before.metrics["source_sha256"]["value"],
        "candidate_sha256": candidate.candidate_sha256,
        "technical_assessment": j.technical_assessment,
        "workflow_decision": j.workflow_decision,
        "human_listening_required": j.human_listening_required,
        "artistic_approval_granted": j.artistic_approval_granted,
        "bundle_root": str(BASE.resolve()),
    }
    (BASE / "golden_summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print("GOLDEN_SUMMARY ->", BASE / "golden_summary.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
