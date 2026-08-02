"""Real-song auditory intelligence case (DSK-MFY-AUDITORY-INTELLIGENCE-RECLASSIFICATION-001).

Runs the full learning-ready loop on 《Vieillir et devenir nouveau avec toi》
with its two real candidates:
  - V1: Audacity Gentle Master (EXTERNAL_GUI_PROCESSING)
  - V2: Moodify full-band EQ master (MOODIFY_DSP)

Rights are intentionally UNKNOWN (real song): the learning record is built,
reviewed and then EXCLUDED with explicit reasons — demonstrating that a real
production case never silently becomes training-eligible.
"""

from __future__ import annotations

import json
from pathlib import Path

from moodify.auditory.profiles import get_profile
from moodify.auditory.service import compare_scans, load_scan_evidence, scan_audio
from moodify.learning.exports import export_learning_records, validate_export_bundle
from moodify.learning.models import (
    AuditoryObservation,
    CandidateOutcome,
    HumanListeningEvaluation,
    InterventionRecord,
    RightsMetadata,
)
from moodify.learning.service import (
    build_learning_record,
    commit_learning_record,
    review_learning_record,
)
from moodify.learning.store import CaseLearningStore

SONG_DIR = Path("pre-music/Vieillir et devenir nouveau avec toi")
SOURCE = SONG_DIR / "Vieillir et devenir nouveau avec toi.wav"
V1 = SONG_DIR / "moodify_delivery/final/Vieillir et devenir nouveau avec toi_Moodify_Audacity_Gentle_Master.wav"
V2 = SONG_DIR / "moodify_delivery_v2/final/Vieillir et devenir nouveau avec toi_V2_Gentle_Master.wav"

BASE = Path("outputs/real_song_case")
CASE_ID = "MFY-CASE-REAL-SONG-001"


def main() -> int:
    BASE.mkdir(parents=True, exist_ok=True)
    case_root = BASE / "cases" / CASE_ID
    store = CaseLearningStore(case_root)
    profile = get_profile("MFY-WSE-SCAN-PROFILE-001")

    # ---- 1. before scan ----
    scan_audio(CASE_ID, "before", SOURCE, case_root / "01_before_scan", profile)
    print("AUDITORY_BEFORE_SCAN_COMPLETED")

    # ---- 2. observation from the real before-scan metrics ----
    before_metrics = json.loads(
        (case_root / "01_before_scan" / "metrics.json").read_text(encoding="utf-8")
    )
    store.save_observation(AuditoryObservation(
        observation_id="OBS-PRESENCE-LOW", case_id=CASE_ID,
        observation_type="PRESENCE_BAND_WEAK",
        source_stage="BEFORE", severity="INFO", confidence="MEDIUM",
        rationale=(
            f"vocals presence 2-5k sits well below the 250-1000Hz body "
            f"(presence_2000_5000_hz ratio {before_metrics.get('presence_2000_5000_hz', {}).get('value')})"
        ),
        evidence_refs=["01_before_scan/metrics.json"],
    ))
    print("AUDITORY_OBSERVATION_RECORDED")

    # ---- 3. plan: presence goal + no-new-damage guardrails ----
    plan = {
        "case_id": CASE_ID, "plan_version": "1.0", "plan_id": "REAL-SONG-PLAN",
        "observations": ["OBS-PRESENCE-LOW"], "artistic_intent_notes": ["vocal clarity"],
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
    (BASE / "plan.json").write_text(json.dumps(plan, ensure_ascii=False, indent=2), encoding="utf-8")

    # ---- 4/5/6. two candidates: interventions, after scans, comparisons ----
    candidates = [
        ("CANDIDATE-V1", V1, "Audacity", "3.7.x", "EXTERNAL_GUI_PROCESSING",
         "Audacity gentle master: -13.8 LUFS target, transparent limiting"),
        ("CANDIDATE-V2", V2, "Moodify", "0.1.0", "MOODIFY_DSP",
         "full-band EQ: 300Hz-2dB + 3.5k/6k presence + air shelf, -15 LUFS, no compression"),
    ]
    for cid, cpath, app, ver, mode, hypothesis in candidates:
        store.save_intervention(InterventionRecord(
            intervention_id=f"INT-{cid}", case_id=CASE_ID, candidate_id=cid,
            parent_audio_sha256="", producing_application=app,
            producing_application_version=ver, processing_operator="user",
            execution_mode=mode, hypothesis=hypothesis, intended_goals=["G_PRESENCE"],
            status="COMPLETED",
        ))
        print(f"INTERVENTION_RECORDED {cid}")
        scan_audio(CASE_ID, "after", cpath, case_root / "06_after_scans" / cid, profile)
        before = load_scan_evidence(case_root / "01_before_scan", profile)
        after = load_scan_evidence(case_root / "06_after_scans" / cid, profile)
        compare_scans(before, after, plan, case_root / "05_comparison" / cid,
                      case_id=CASE_ID, candidate_id=cid,
                      source_sha256=before.metrics["source_sha256"]["value"],
                      candidate_sha256="")
        report = json.loads(
            (case_root / "05_comparison" / cid / "comparison_report.json").read_text(encoding="utf-8")
        )
        print(f"AUDITORY_COMPARISON_COMPLETED {cid}: "
              f"{report['judgment']['technical_assessment']}/{report['judgment']['workflow_decision']}")

    # ---- 7. human listening evaluation (real decision requires the user;
    # recorded here as the system's structured intake) ----
    store.save_evaluation(HumanListeningEvaluation(
        evaluation_id="EV-REAL-SONG", case_id=CASE_ID,
        candidate_ids=["CANDIDATE-V1", "CANDIDATE-V2"],
        evaluator_id="user", comparison_mode="A_B_OPEN",
        preferred_candidate_id=None, audible_difference="UNKNOWN",
        goal_achieved="UNKNOWN", artistic_damage_detected=False,
        reasons=["human listening pending — structured evaluation recorded"],
        confidence="LOW", approval_status="PENDING",
    ))
    print("HUMAN_LISTENING_EVALUATION_RECORDED (pending human confirmation)")

    # ---- 8. outcomes from technical judgment (artistic approval stays false) ----
    for cid in ("CANDIDATE-V1", "CANDIDATE-V2"):
        report = json.loads(
            (case_root / "05_comparison" / cid / "comparison_report.json").read_text(encoding="utf-8")
        )
        j = report["judgment"]
        outcome = {
            ("IMPROVED", "PASS_TO_LISTENING"): "ACCEPTED",
            ("NEUTRAL", "INCONCLUSIVE"): "NEUTRAL",
            ("UNCERTAIN", "INCONCLUSIVE"): "UNCERTAIN",
            ("DEGRADED", "REJECT_TECHNICAL"): "REJECTED",
        }.get((j["technical_assessment"], j["workflow_decision"]), "UNCERTAIN")
        store.append_outcome(CandidateOutcome(
            case_id=CASE_ID, candidate_id=cid, outcome=outcome,
            technical_assessment=j["technical_assessment"],
            workflow_decision=j["workflow_decision"],
            artistic_decision="PENDING",  # never auto-approved
            reasons=j.get("reasons", []),
        ))
    print("CANDIDATE_OUTCOMES_RECORDED")

    # ---- 9. learning record: build -> review -> commit (excluded: real song) ----
    record = build_learning_record(store, CASE_ID)
    print(f"LEARNING_RECORD_BUILT {record.learning_record_id} status={record.learning_status}")

    rights = RightsMetadata(
        audio_origin="USER_PROVIDED", rights_holder="user",
        processing_authorization="YES",  # user asked Moodify to process it
        research_use_authorized="UNKNOWN", model_training_authorized="UNKNOWN",
        derivative_data_authorized="UNKNOWN", commercial_training_authorized="UNKNOWN",
        retention_policy="UNKNOWN", reviewed_by="", reviewed_at="",
    )
    reviewed = review_learning_record(store, CASE_ID, rights)
    print(f"LEARNING_RECORD_REVIEWED eligibility={reviewed.training_eligibility}")

    committed = commit_learning_record(store, CASE_ID, "auditory-loop")
    print(f"LEARNING_RECORD_{'COMMITTED' if committed.learning_status == 'COMMITTED' else 'EXCLUDED'}"
          f" reasons={committed.exclusion_reasons}")

    # ---- 10. controlled export: real song must NOT be exportable without rights ----
    export_dir = BASE / "exports" / "MFY-AUDITORY-DATASET-REAL"
    manifest = export_learning_records([committed], export_dir, "MFY-AUDITORY-DATASET-REAL")
    problems = validate_export_bundle(export_dir, "MFY-AUDITORY-DATASET-REAL")
    if problems:
        print("EXPORT_VERIFICATION_FAILED", problems)
        return 1
    print(f"DATASET_EXPORT_COMPLETED included={manifest['included_count']} "
          f"excluded={manifest['excluded_count']} (fail-closed: real song not exportable)")

    summary = {
        "case_id": CASE_ID,
        "source": str(SOURCE),
        "candidates": {"CANDIDATE-V1": str(V1), "CANDIDATE-V2": str(V2)},
        "learning_record_id": committed.learning_record_id,
        "learning_status": committed.learning_status,
        "training_eligibility": committed.training_eligibility,
        "exclusion_reasons": committed.exclusion_reasons,
        "human_listening_status": "PENDING",
        "bundle_root": str(BASE.resolve()),
    }
    (BASE / "real_song_summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print("REAL_SONG_SUMMARY ->", BASE / "real_song_summary.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
