"""One-song Phase-I data-factory orchestrator.

The runner coordinates existing authoritative auditory functions. It does not
reimplement measurement, comparison, or judgment logic.
"""

from __future__ import annotations

import json
import shutil
from datetime import timezone
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path

import numpy as np

from moodify.auditory.decode import decode, probe
from moodify.auditory.errors import AudioDecodeFailed, AudioEmpty
from moodify.auditory.manifests import sha256_file
from moodify.auditory.profiles import get_profile
from moodify.auditory.service import (
    compare_scans,
    load_scan_evidence,
    register_candidate,
    scan_audio,
)
from moodify.contracts.base import utc_now
from moodify.contracts.ids import new_id
from moodify.contracts.production_case import AuthorityState, LifecycleState, ProductionCase

from .human_review import write_review_template
from .intervention import execute_intervention
from .models import DATA_PROTOCOL_VERSION, PLAN_GENERATOR_VERSION
from .plan_generator import generate_abc_plans


def _package_version() -> str:
    try:
        return version("moodify")
    except PackageNotFoundError:
        return "uninstalled-worktree"


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def validate_source_audio(
    path: Path,
    *,
    min_duration_s: float = 0.5,
    min_decoded_s: float = 0.1,
    analysis_sample_rate: int = 22050,
) -> None:
    """Reject degenerate audio before it produces a meaningless case.

    ffprobe tolerates truncated containers, so duration alone is not enough:
    verify that decoding actually yields a meaningful amount of non-silent
    audio. Raises AudioDecodeFailed/AudioEmpty on invalid input.
    """
    info = probe(path)
    if info.duration_seconds < min_duration_s:
        raise AudioDecodeFailed(
            f"source audio too short: {info.duration_seconds:.3f}s < {min_duration_s}s"
        )
    decoded = decode(path, analysis_sample_rate=analysis_sample_rate)
    seconds = decoded.samples.shape[0] / decoded.sample_rate
    if seconds < min_decoded_s:
        raise AudioEmpty(
            f"source audio decodes to {seconds:.3f}s < {min_decoded_s}s of samples"
        )
    head = decoded.samples[: max(1, int(0.5 * decoded.sample_rate))]
    rms = float(np.sqrt(np.mean(head.astype(np.float64) ** 2)))
    if rms < 1e-4:
        raise AudioEmpty(f"source audio silent in first 0.5s (rms={rms:.2e})")


def run_production_case(
    source_path: Path,
    output_root: Path,
    *,
    case_id: str | None = None,
    scan_profile_id: str = "MFY-WSE-SCAN-PROFILE-001",
) -> Path:
    source_path = Path(source_path)
    if not source_path.is_file():
        raise FileNotFoundError(source_path)

    case_id = case_id or new_id("case")
    profile = get_profile(scan_profile_id)
    case_dir = Path(output_root) / "cases" / case_id
    if case_dir.exists() and any(case_dir.iterdir()):
        raise FileExistsError(f"case already exists and is not empty: {case_dir}")
    case_dir.mkdir(parents=True, exist_ok=True)

    # 00 source: immutable byte copy for a self-contained local evidence bundle.
    source_dir = case_dir / "00_source"
    source_dir.mkdir(parents=True, exist_ok=True)
    preserved_source = source_dir / f"source{source_path.suffix.lower()}"
    shutil.copy2(source_path, preserved_source)
    validate_source_audio(preserved_source)
    source_sha256 = sha256_file(preserved_source)

    # 01 BEFORE scan.
    before_dir = case_dir / "01_source_scan"
    before_output = scan_audio(case_id, "before", preserved_source, before_dir, profile)
    before = load_scan_evidence(before_dir, profile)

    # 02 deterministic ABC plans.
    plans = generate_abc_plans(
        case_id=case_id,
        source_metrics=before_output.metrics,
        source_sha256=source_sha256,
        scan_profile_id=profile.profile_id,
        scan_profile_hash=profile.hash(),
    )
    for plan in plans:
        _write_json(case_dir / "02_plans" / f"plan_{plan.candidate_label}.json", plan.to_dict())

    # 03/04/05 candidate processing, after scan, source-vs-candidate comparison.
    candidate_hashes: dict[str, str] = {}
    for plan in plans:
        label = plan.candidate_label
        candidate_path = case_dir / "03_candidates" / f"candidate_{label}.wav"
        result = execute_intervention(preserved_source, candidate_path, plan)

        registered = register_candidate(
            case_id=case_id,
            candidate_id=plan.candidate_id,
            source_case_id=case_id,
            candidate_path=candidate_path,
            parent_source_sha256=source_sha256,
            producing_application="MoodifyDSPChain",
            producing_application_version=_package_version(),
            processing_operator="MFY-DATA-FACTORY-001",
            processing_method=f"ABC_{plan.strategy}",
            processing_notes=f"{PLAN_GENERATOR_VERSION}; intensity={plan.intensity}",
            registry_path=None,
        )
        candidate_hashes[label] = registered.candidate_sha256
        _write_json(
            case_dir / "03_candidates" / f"candidate_{label}.json",
            {**registered.to_dict(), "intervention_result": result.to_dict()},
        )

        after_dir = case_dir / "04_after_scan" / label
        scan_audio(case_id, "after", candidate_path, after_dir, profile)
        after = load_scan_evidence(after_dir, profile)
        if after.profile_hash != before.profile_hash:
            raise RuntimeError("before/after scan profile hash mismatch")

        compare_scans(
            before,
            after,
            plan.to_dict(),
            case_dir / "05_comparison" / f"source_vs_{label}",
            case_id=case_id,
            candidate_id=plan.candidate_id,
            source_sha256=source_sha256,
            candidate_sha256=registered.candidate_sha256,
        )

    # 06 human authority checkpoint.
    write_review_template(case_id, case_dir / "06_human_review" / "review.json")

    created = utc_now()
    production_case = ProductionCase(
        created_at=created,
        case_id=case_id,
        source_id=f"sha256:{source_sha256}",
        objective="Produce ABC auditory intervention evidence and collect human ranking",
        lifecycle_state=LifecycleState.AWAITING_HUMAN,
        authority_state=AuthorityState.HUMAN_REQUIRED,
    )
    (case_dir / "production_case.json").write_text(
        production_case.model_dump_json(indent=2), encoding="utf-8"
    )

    manifest = {
        "schema_version": "1.0",
        "data_protocol_version": DATA_PROTOCOL_VERSION,
        "case_id": case_id,
        "created_at": created.astimezone(timezone.utc).isoformat(),
        "source_path": str(preserved_source.relative_to(case_dir)),
        "source_sha256": source_sha256,
        "candidate_sha256": candidate_hashes,
        "versions": {
            "moodify_package_version": _package_version(),
            "scan_profile_id": profile.profile_id,
            "scan_profile_hash": profile.hash(),
            "plan_generator_version": PLAN_GENERATOR_VERSION,
            "judgment_authority": "moodify.auditory.judgment",
            "canonical_contract_schema": "1.0",
        },
        "status": "AWAITING_HUMAN",
    }
    _write_json(case_dir / "case_manifest.json", manifest)
    return case_dir
