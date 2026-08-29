"""Moodify 1.0 release spine: one trustworthy, persistent auditory case."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from moodify.auditory.judgment import evaluate_risk_flags, judge, write_judgment_rules
from moodify.auditory.manifests import sha256_file
from moodify.auditory.profiles import get_profile
from moodify.auditory.reports import build_auditory_report
from moodify.auditory.service import load_scan_evidence, scan_audio
from moodify.contracts import (
    AuthorityState,
    EvidenceArtifact,
    LifecycleState,
    MeasurementRecord,
    ProductionCase,
    Provenance,
)
from moodify.contracts.base import utc_now
from moodify.contracts.ids import new_id
from moodify.contracts.serialization import to_canonical_json

PRODUCT_VERSION = "1.0.0-rc.1"
PROFILE_ID = "MFY-WSE-SCAN-PROFILE-001"


def _digest_bytes(data: bytes) -> str:
    return "sha256:" + hashlib.sha256(data).hexdigest()


def _write_model(path: Path, model) -> None:
    path.write_text(to_canonical_json(model) + "\n", encoding="utf-8")


def analyze_to_case(source: Path, cases_root: Path, *, display_name: str | None = None) -> dict:
    """Analyze without modifying *source* and persist a reopenable case bundle."""
    source = source.resolve(strict=True)
    source_hash = sha256_file(source)
    source_id = f"sha256:{source_hash}"
    case_id = new_id("case")
    case_root = cases_root.resolve() / case_id
    scan_dir = case_root / "scan"
    case_root.mkdir(parents=True, exist_ok=False)

    created = ProductionCase(
        case_id=case_id,
        source_id=source_id,
        objective="auditory analysis",
        lifecycle_state=LifecycleState.ACTIVE,
        authority_state=AuthorityState.SYSTEM,
        created_at=utc_now(),
    )
    _write_model(case_root / "case.json", created)

    try:
        profile = get_profile(PROFILE_ID)
        scan_audio(case_id, "source", source, scan_dir, profile=profile)
        evidence = load_scan_evidence(scan_dir, profile)
        flags = evaluate_risk_flags({}, {}, evidence.metrics)
        technical_judgment = judge({}, {}, evidence.metrics, None, flags)
        rules_path = case_root / "judgment_rules.json"
        write_judgment_rules(rules_path)

        parameters_hash = _digest_bytes(profile.canonical().encode("utf-8"))
        provenance = Provenance(
            producer="Moodify",
            producer_version=PRODUCT_VERSION,
            method="auditory_scan",
            method_version=profile.profile_id,
            parameters_hash=parameters_hash,
        )
        measurements = []
        for name, item in sorted(evidence.metrics.items()):
            if not isinstance(item, dict) or item.get("value") is None:
                continue
            measurements.append(MeasurementRecord(
                measurement_id=new_id("meas"), case_id=case_id,
                source_id=source_id, namespace="moodify.auditory", name=name,
                value=item["value"], unit=item.get("unit") or "unknown",
                confidence=None, provenance=provenance, created_at=utc_now(),
                metadata={"status": item.get("status", "VALID")},
            ))
        (case_root / "measurements.json").write_text(
            json.dumps([json.loads(to_canonical_json(item)) for item in measurements],
                       ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n",
            encoding="utf-8",
        )

        report_path = case_root / "auditory_report.json"
        evidence_index = {
            "metrics.json": "scan/metrics.json",
            "scan_manifest.json": "scan/scan_manifest.json",
            "judgment_rules.json": "judgment_rules.json",
        }
        report = build_auditory_report(
            report_path, source_name=Path(display_name or source.name).name, case_id=case_id,
            source_sha256=source_id, analysis_version=PRODUCT_VERSION,
            overall_status="OK", metrics=evidence.metrics,
            findings=[flag.to_dict() for flag in flags],
            evidence_index=evidence_index,
            summary=("Machine auditory analysis completed. Human listening authority "
                     f"is required. Technical decision: {technical_judgment.workflow_decision}."),
            overall_confidence=min(
                (flag.confidence for flag in flags if flag.confidence is not None),
                default=None,
            ),
        )

        artifact_specs = [
            ("metrics", "application/json", scan_dir / "metrics.json", "scan/metrics.json"),
            ("scan_manifest", "application/json", scan_dir / "scan_manifest.json", "scan/scan_manifest.json"),
            ("judgment_rules", "application/json", rules_path, "judgment_rules.json"),
            ("auditory_report", "application/json", report_path, "auditory_report.json"),
        ]
        artifacts = [EvidenceArtifact(
            evidence_id=new_id("evid"), case_id=case_id, source_id=source_id,
            artifact_type=kind, media_type=media_type,
            content_hash="sha256:" + sha256_file(path),
            size_bytes=path.stat().st_size, provenance=provenance,
            logical_path=logical_path, created_at=utc_now(),
        ) for kind, media_type, path, logical_path in artifact_specs]
        (case_root / "evidence.json").write_text(
            json.dumps([json.loads(to_canonical_json(item)) for item in artifacts],
                       ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n",
            encoding="utf-8",
        )

        completed = ProductionCase(
            case_id=case_id, source_id=source_id, objective="auditory analysis",
            lifecycle_state=LifecycleState.COMPLETED,
            authority_state=AuthorityState.HUMAN_REQUIRED,
            measurement_ids=tuple(item.measurement_id for item in measurements),
            evidence_ids=tuple(item.evidence_id for item in artifacts),
            created_at=created.created_at,
        )
        _write_model(case_root / "case.json", completed)
        return {"case": json.loads(to_canonical_json(completed)), "report": report}
    except Exception:
        failed = ProductionCase(
            case_id=case_id, source_id=source_id, objective="auditory analysis",
            lifecycle_state=LifecycleState.FAILED,
            authority_state=AuthorityState.HUMAN_REQUIRED,
            created_at=created.created_at,
        )
        _write_model(case_root / "case.json", failed)
        raise


def reopen_case(cases_root: Path, case_id: str) -> dict:
    """Load public persisted case/report data; canonical validation blocks traversal."""
    ProductionCase.model_validate_json((cases_root / case_id / "case.json").read_text(encoding="utf-8"))
    case = json.loads((cases_root / case_id / "case.json").read_text(encoding="utf-8"))
    report = json.loads((cases_root / case_id / "auditory_report.json").read_text(encoding="utf-8"))
    return {"case": case, "report": report}
