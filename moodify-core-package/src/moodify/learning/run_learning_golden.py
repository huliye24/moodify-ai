"""Learning golden case (DSK-MFY-AUDITORY-INTELLIGENCE-RECLASSIFICATION-001).

Demonstrates the full loop with one accepted and one rejected candidate:
source → before scan → observation → plan → two candidates → interventions →
after scans → comparisons → human listening → preference → learning record →
rights review → eligibility → controlled dataset export.
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import soundfile as sf

from moodify.auditory.profiles import get_profile
from moodify.auditory.service import compare_scans, load_scan_evidence, scan_audio
from moodify.learning.exports import export_learning_records, validate_export_bundle
from moodify.learning.models import (
    AuditoryObservation,
    CandidateOutcome,
    HumanListeningEvaluation,
    InterventionRecord,
    PairwisePreference,
    RightsMetadata,
)
from moodify.learning.service import (
    build_learning_record,
    commit_learning_record,
    review_learning_record,
)
from moodify.learning.store import CaseLearningStore

BASE = Path("outputs/auditory_golden_learning")
CASE_ID = "MFY-CASE-LEARN-001"
SR = 48000


def main() -> int:
    BASE.mkdir(parents=True, exist_ok=True)
    case_root = BASE / "cases" / CASE_ID
    store = CaseLearningStore(case_root)
    profile = get_profile("MFY-WSE-SCAN-PROFILE-001")

    # ---- deterministic synthetic source ----
    rng = np.random.default_rng(11)
    t = np.arange(SR * 10) / SR
    src = (
        0.25 * np.sin(2 * np.pi * 60 * t)
        + 0.2 * np.sin(2 * np.pi * 250 * t)
        + 0.15 * np.sin(2 * np.pi * 900 * t)
        + 0.04 * np.sin(2 * np.pi * 5500 * t)
        + 0.008 * rng.standard_normal(len(t))
    )
    src = np.stack([src, src * 0.97], axis=1).astype(np.float32)
    # candidate A: presence lift (accepted path)
    cand_a = np.clip(src + 0.07 * np.sin(2 * np.pi * 4000 * t)[:, None], -1, 1).astype(np.float32)
    # candidate B: overprocessed (rejected path: heavy limiting)
    cand_b = np.clip(np.tanh(src * 3.2), -1, 1).astype(np.float32)
    src_path = BASE / "golden_source.wav"
    cand_a_path = BASE / "candidate_a.wav"
    cand_b_path = BASE / "candidate_b.wav"
    sf.write(src_path, src, SR)
    sf.write(cand_a_path, cand_a, SR)
    sf.write(cand_b_path, cand_b, SR)

    # ---- before scan ----
    scan_audio(CASE_ID, "before", src_path, case_root / "01_before_scan", profile)
    print("AUDITORY_BEFORE_SCAN_COMPLETED")

    # ---- observation ----
    store.save_observation(AuditoryObservation(
        observation_id="OBS-AIR-LOW", case_id=CASE_ID, observation_type="AIR_BAND_LOW",
        source_stage="BEFORE", severity="INFO", confidence="MEDIUM",
        rationale="air band below mid-band reference in synthetic mix",
    ))
    print("AUDITORY_OBSERVATION_RECORDED")

    # ---- plan ----
    plan = {
        "case_id": CASE_ID, "plan_version": "1.0", "plan_id": "LEARN-PLAN",
        "observations": ["OBS-AIR-LOW"], "artistic_intent_notes": ["presence"],
        "technical_goals": [{
            "goal_id": "G_PRESENCE", "metric": "presence_2000_5000_hz",
            "desired_direction": "INCREASE", "minimum_meaningful_change": 0.01,
        }],
        "guardrails": [{
            "guardrail_id": "NO_NEW_CLIPPING", "metric": "clipping_sample_count",
            "comparator": "EQUAL", "threshold": 0, "severity": "BLOCKING",
        }],
        "approved_by": "golden", "approved_at": None,
    }
    (BASE / "plan.json").write_text(json.dumps(plan, ensure_ascii=False, indent=2), encoding="utf-8")

    # ---- two interventions + after scans + comparisons ----
    for cid, cpath, app, op in (
        ("CANDIDATE-A", cand_a_path, "synthetic-presence", "presence lift 4kHz"),
        ("CANDIDATE-B", cand_b_path, "synthetic-overprocess", "heavy tanh limiting"),
    ):
        store.save_intervention(InterventionRecord(
            intervention_id=f"INT-{cid}", case_id=CASE_ID, candidate_id=cid,
            parent_audio_sha256="", producing_application=app,
            processing_operator="golden", execution_mode="SCRIPTED_TOOL",
            hypothesis=op, intended_goals=["G_PRESENCE"], status="COMPLETED",
        ))
        print(f"INTERVENTION_RECORDED {cid}")
        scan_audio(CASE_ID, "after", cpath, case_root / "06_after_scans" / cid, profile)
        before = load_scan_evidence(case_root / "01_before_scan", profile)
        after = load_scan_evidence(case_root / "06_after_scans" / cid, profile)
        compare_scans(before, after, plan, case_root / "05_comparison" / cid,
                      case_id=CASE_ID, candidate_id=cid,
                      source_sha256=before.metrics["source_sha256"]["value"],
                      candidate_sha256="")
        print(f"AUDITORY_COMPARISON_COMPLETED {cid}")

    # ---- human listening evaluation (simulated, recorded as evidence) ----
    store.save_evaluation(HumanListeningEvaluation(
        evaluation_id="EV-GOLDEN", case_id=CASE_ID, candidate_ids=["CANDIDATE-A", "CANDIDATE-B"],
        evaluator_id="golden-listener", comparison_mode="A_B_BLIND",
        preferred_candidate_id="CANDIDATE-A", audible_difference="CLEAR",
        goal_achieved="YES", artistic_damage_detected=False,
        reasons=["candidate A clearer presence", "candidate B overprocessed"],
        confidence="HIGH", approval_status="APPROVED",
    ))
    print("HUMAN_LISTENING_EVALUATION_RECORDED")

    # ---- preferences + outcomes (accepted + rejected) ----
    store.append_preference(PairwisePreference(
        case_id=CASE_ID, preferred_candidate_id="CANDIDATE-A",
        other_candidate_id="CANDIDATE-B", basis="HUMAN_LISTENING",
    ))
    store.append_outcome(CandidateOutcome(
        case_id=CASE_ID, candidate_id="CANDIDATE-A", outcome="ACCEPTED",
        technical_assessment="IMPROVED", workflow_decision="PASS_TO_LISTENING",
        artistic_decision="APPROVED", reasons=["presence goal met"],
    ))
    store.append_outcome(CandidateOutcome(
        case_id=CASE_ID, candidate_id="CANDIDATE-B", outcome="OVERPROCESSED",
        technical_assessment="DEGRADED", workflow_decision="REJECT_TECHNICAL",
        artistic_decision="REJECTED", reasons=["clipping introduced"],
    ))
    print("PAIRWISE_PREFERENCE_RECORDED")

    # ---- learning record: build -> review -> commit ----
    record = build_learning_record(store, CASE_ID)
    print(f"LEARNING_RECORD_BUILT {record.learning_record_id} status={record.learning_status}")

    rights = RightsMetadata(
        audio_origin="SYNTHETIC", rights_holder="moodify-lab",
        processing_authorization="YES", research_use_authorized="YES",
        model_training_authorized="YES", derivative_data_authorized="YES",
        commercial_training_authorized="YES", retention_policy="LAB",
        consent_reference="synthetic-asset-policy", reviewed_by="golden-reviewer",
    )
    reviewed = review_learning_record(store, CASE_ID, rights)
    print(f"LEARNING_RECORD_REVIEWED eligibility={reviewed.training_eligibility}")

    committed = commit_learning_record(store, CASE_ID, "golden-reviewer")
    print(f"LEARNING_RECORD_{'COMMITTED' if committed.learning_status == 'COMMITTED' else 'EXCLUDED'}")

    # ---- controlled dataset export (only ELIGIBLE records) ----
    export_dir = BASE / "exports" / "MFY-AUDITORY-DATASET-001"
    manifest = export_learning_records([committed], export_dir, "MFY-AUDITORY-DATASET-001")
    problems = validate_export_bundle(export_dir, "MFY-AUDITORY-DATASET-001")
    if problems:
        print("EXPORT_VERIFICATION_FAILED", problems)
        return 1
    print(f"DATASET_EXPORT_COMPLETED included={manifest['included_count']}")

    summary = {
        "case_id": CASE_ID,
        "learning_record_id": committed.learning_record_id,
        "learning_status": committed.learning_status,
        "training_eligibility": committed.training_eligibility,
        "accepted_candidates": ["CANDIDATE-A"],
        "rejected_candidates": ["CANDIDATE-B"],
        "dataset_export": f"{export_dir}/MFY-AUDITORY-DATASET-001_manifest.json",
        "bundle_root": str(BASE.resolve()),
    }
    (BASE / "learning_golden_summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print("LEARNING_GOLDEN_SUMMARY ->", BASE / "learning_golden_summary.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
