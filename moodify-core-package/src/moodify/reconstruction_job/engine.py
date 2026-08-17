"""Reconstruction job execution engine (MFY-CR-P08).

Orchestrates the existing P03-P05 chain via run_golden_pipeline; never
reimplements diagnostic, objective, guard, or evidence authority. The job
workspace layout is job/{input,case,candidates,evidence,result,tmp}.
"""

from __future__ import annotations

import hashlib
import json
import shutil
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

from moodify.auditory.decode import probe
from moodify.contracts.base import utc_now
from moodify.contracts.evidence_artifact import EvidenceArtifact
from moodify.contracts.ids import new_id
from moodify.contracts.production_case import (
    AuthorityState,
    LifecycleState,
    ProductionCase,
)
from moodify.contracts.provenance import Provenance
from moodify.data_factory.runner import validate_source_audio
from moodify.reconstruction.pipeline import run_golden_pipeline

from .audio_util import (
    SUPPORTED_SUFFIXES,
    classify_ingest_error,
    ensure_ffmpeg_on_path,
    sha256_file,
    transcode_to_wav,
)
from .contract import (
    FailureInfo,
    JobStatus,
    ReconstructionJob,
    ReconstructionResult,
)
from .resource_meter import ResourceBudget, ResourceMeter
from .selection import SelectDecision, classify_pipeline_failure, select_result
from .store import JobStore

PARAMETERS_HASH = "sha256:" + hashlib.sha256(b"mfy-cr-p08").hexdigest()


@dataclass(frozen=True)
class EngineConfig:
    workspace_root: Path
    max_wall_time_s: float = 1800.0
    max_candidates: int = 4
    rights_status: str = "USER_SUBMITTED"


class EngineError(RuntimeError):
    pass


def _iso(value: datetime | None = None) -> str:
    return (value or datetime.now(timezone.utc)).isoformat(timespec="seconds")


def _check_cancel(store: JobStore, job: ReconstructionJob) -> bool:
    if job.cancel_requested:
        store.admin_cancel(job.job_id)
        return True
    return False


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def _build_case(ws: Path, source_sha256: str, case_id: str) -> ProductionCase:
    created = utc_now()
    case = ProductionCase(
        created_at=created,
        case_id=case_id,
        source_id=f"sha256:{source_sha256}",
        objective="Cloud reconstruction job: diagnose, plan, guard, select.",
        lifecycle_state=LifecycleState.CREATED,
        authority_state=AuthorityState.SYSTEM,
    )
    _write_json(ws / "case" / "production_case.json", json.loads(case.model_dump_json()))
    return case


def _evidence_artifact(ws: Path, case_id: str, source_sha256: str, logical_path: str) -> EvidenceArtifact:
    path = ws / logical_path
    return EvidenceArtifact(
        created_at=utc_now(),
        evidence_id=new_id("evid"),
        case_id=case_id,
        source_id=f"sha256:{source_sha256}",
        artifact_type="reconstruction_evidence",
        media_type="application/json",
        content_hash="sha256:" + sha256_file(path),
        size_bytes=path.stat().st_size,
        provenance=Provenance(
            producer="moodify.reconstruction_job",
            producer_version="reconstruction-job-v0.1",
            method="cloud-reconstruction-job",
            method_version="reconstruction-job-v0.1",
            parameters_hash=PARAMETERS_HASH,
            algorithm_version="golden-pipeline-v0.1",
            input_sha256=source_sha256,
        ),
        uri=logical_path,
        logical_path=logical_path,
    )


def _finalize(
    store: JobStore,
    job: ReconstructionJob,
    ws: Path,
    decision: SelectDecision,
    case: ProductionCase,
    source_sha256: str,
    meter: ResourceMeter,
    *,
    candidate_count: int,
) -> str:
    """Persist canonical evidence, result object, and terminal status."""
    case_dir = ws / "case"

    evidence_artifacts: list[EvidenceArtifact] = []
    for logical in ("source_manifest.json", "era_diagnostic.v0.1.json", "golden_record.json"):
        if (case_dir / logical).is_file():
            evidence_artifacts.append(
                _evidence_artifact(ws, case.case_id, source_sha256, f"case/{logical}")
            )

    result_dict = {
        "job_id": job.job_id,
        "case_id": case.case_id,
        "source_sha256": source_sha256,
        "selected_candidate": decision.selected_candidate,
        "plan_hash": decision.plan_hash,
        "identity_status": decision.identity_status,
        "technical_status": decision.technical_status,
        "resource": meter.snapshot(candidate_count=candidate_count).to_dict(),
        "created_at": _iso(),
    }
    _write_json(ws / "result" / "result.json", result_dict)
    evidence_artifacts.append(
        _evidence_artifact(ws, case.case_id, source_sha256, "result/result.json")
    )

    final_case = ProductionCase(
        created_at=case.created_at,
        case_id=case.case_id,
        source_id=case.source_id,
        objective=case.objective,
        lifecycle_state=(
            LifecycleState.COMPLETED
            if decision.status in (JobStatus.SUCCEEDED.value, JobStatus.SOURCE_WINS.value)
            else LifecycleState.AWAITING_HUMAN
        ),
        authority_state=(
            AuthorityState.ALGORITHM
            if decision.status in (JobStatus.SUCCEEDED.value, JobStatus.SOURCE_WINS.value)
            else AuthorityState.HUMAN_REQUIRED
        ),
        measurement_ids=case.measurement_ids,
        evidence_ids=tuple(a.evidence_id for a in evidence_artifacts),
        rule_ids=case.rule_ids,
        parent_case_id=case.parent_case_id,
    )
    _write_json(
        case_dir / "production_case.json",
        json.loads(final_case.model_dump_json()),
    )
    evidence_lines = "\n".join(a.model_dump_json() for a in evidence_artifacts)
    (case_dir / "evidence.json").write_text(evidence_lines + "\n", encoding="utf-8")

    result = ReconstructionResult(
        result_id=f"res_{job.job_id[4:36]}",
        job_id=job.job_id,
        production_case_id=case.case_id,
        source_sha256=source_sha256,
        selected_candidate=decision.selected_candidate,
        audio_object_ref=(
            f"{ws.name}/candidates/{decision.selected_candidate}.wav"
            if decision.selected_candidate != "SOURCE"
            else f"{ws.name}/input/source.wav"
        ),
        reconstruction_version=job.reconstruction_version,
        plan_hash=decision.plan_hash,
        engine_version="golden-pipeline-v0.1",
        identity_status=decision.identity_status,
        technical_status=decision.technical_status,
        created_at=_iso(),
    )
    store.succeed(job.job_id, decision.status, result)
    return decision.status


def run_reconstruction_job(
    job: ReconstructionJob,
    store: JobStore,
    config: EngineConfig,
) -> str:
    """Execute one leased job; returns the terminal status."""
    store.mark_started(job.job_id)
    ensure_ffmpeg_on_path()
    ws = Path(config.workspace_root) / job.job_id
    try:
        if _check_cancel(store, job):
            return JobStatus.CANCELLED.value

        # ---- VALIDATING: source checks + canonical case binding ----
        store.update_progress(job.job_id, JobStatus.VALIDATING.value)
        input_dir = ws / "input"
        if not input_dir.is_dir():
            raise EngineError("job workspace input missing")
        source_files = [p for p in input_dir.iterdir() if p.is_file() and p.name != "source.wav"]
        if len(source_files) != 1:
            raise EngineError(f"expected exactly one source file, found {len(source_files)}")
        source_file = source_files[0]
        if source_file.suffix.lower() not in SUPPORTED_SUFFIXES:
            store.fail(
                job.job_id,
                _failure("UNSUPPORTED_FORMAT", "ingest", "PERMANENT",
                         "provide a supported audio file",
                         f"unsupported suffix {source_file.suffix}",
                         "reconstruction_format_unsupported"),
            )
            return JobStatus.FAILED.value
        try:
            info = probe(source_file)
            if info.duration_seconds < 0.5:
                raise EngineError(f"source too short: {info.duration_seconds:.3f}s")
            validate_source_audio(source_file)
        except Exception as exc:
            store.fail(job.job_id, classify_ingest_error(exc))
            return JobStatus.FAILED.value
        source_sha256 = sha256_file(source_file)
        store.update_source_sha256(job.job_id, source_sha256)

        if _check_cancel(store, job):
            return JobStatus.CANCELLED.value
        case_id = new_id("case")
        case = _build_case(ws, source_sha256, case_id)
        store.attach_case(job.job_id, case_id)

        # ---- ANALYZING: decode to WAV preserving sample rate ----
        store.update_progress(job.job_id, JobStatus.ANALYZING.value)
        meter = ResourceMeter()
        try:
            transcode_to_wav(source_file, ws / "input" / "source.wav")
        except Exception as exc:
            store.fail(job.job_id, classify_ingest_error(exc))
            return JobStatus.FAILED.value
        meter.note_memory()

        if _check_cancel(store, job):
            return JobStatus.CANCELLED.value

        # ---- PLANNING / RECONSTRUCTING / VERIFYING: existing P03-P05 chain ----
        store.update_progress(job.job_id, JobStatus.PLANNING.value)
        pipeline = run_golden_pipeline(
            ws / "input" / "source.wav",
            ws / "case",
            rights_status=config.rights_status,
            source_alias=case_id,
            record_id=f"JOB-{job.job_id}",
            case_id=case_id,
            skip_blind_kit=True,
            candidates_dir=ws / "candidates",
            include_low_confidence=False,  # production: no LOW-authorised candidates
        )
        meter.note_memory()
        store.update_progress(job.job_id, JobStatus.VERIFYING.value)
        decision = select_result(pipeline)

        candidate_count = len([c for c in pipeline.candidates if c != "SOURCE"])
        budget = ResourceBudget(max_wall_time_s=config.max_wall_time_s,
                                max_candidates=config.max_candidates)
        usage = meter.snapshot(candidate_count=candidate_count)
        exceeded = budget.exceeded(usage, candidate_count=candidate_count)
        if exceeded:
            store.fail(
                job.job_id,
                _failure("RESOURCE_LIMIT", "pipeline", "PERMANENT",
                         "job exceeded resource budget", f"budget:{exceeded}",
                         "reconstruction_resource_limit"),
            )
            return JobStatus.FAILED.value

        if decision.status == JobStatus.HUMAN_REQUIRED.value:
            case_dir = ws / "case"
            human_case = ProductionCase(
                created_at=case.created_at, case_id=case.case_id, source_id=case.source_id,
                objective=case.objective,
                lifecycle_state=LifecycleState.AWAITING_HUMAN,
                authority_state=AuthorityState.HUMAN_REQUIRED,
                measurement_ids=case.measurement_ids, evidence_ids=case.evidence_ids,
                rule_ids=case.rule_ids, parent_case_id=case.parent_case_id,
            )
            _write_json(case_dir / "production_case.json", json.loads(human_case.model_dump_json()))
            store.update_progress(job.job_id, JobStatus.HUMAN_REQUIRED.value)
            return JobStatus.HUMAN_REQUIRED.value

        return _finalize(store, job, ws, decision, case, source_sha256, meter,
                         candidate_count=candidate_count)

    except Exception as exc:
        store.retry_or_fail(job.job_id, classify_pipeline_failure(exc))
        return JobStatus.FAILED.value
    finally:
        shutil.rmtree(ws / "tmp", ignore_errors=True)


def admin_finalize(
    job: ReconstructionJob,
    store: JobStore,
    config: EngineConfig,
    decision: SelectDecision,
) -> str:
    """Human-review path: finalize an already-reconstructed HUMAN_REQUIRED job.

    Reads canonical case artifacts from the job workspace; never re-runs the
    pipeline. Selection is operator-driven and recorded as HUMAN_APPROVED.
    """
    ws = Path(config.workspace_root) / job.job_id
    case_dir = ws / "case"
    if not (case_dir / "production_case.json").is_file():
        raise EngineError("case artifacts missing for human review")
    case = ProductionCase.model_validate_json(
        (case_dir / "production_case.json").read_text(encoding="utf-8")
    )
    source_sha256 = job.source_sha256
    meter = ResourceMeter()
    approved = SelectDecision(
        status=decision.status,
        selected_candidate=decision.selected_candidate,
        plan_hash=decision.plan_hash,
        identity_status="HUMAN_APPROVED",
        technical_status=decision.technical_status,
    )
    return _finalize(store, job, ws, approved, case, source_sha256, meter, candidate_count=0)


def _failure(code: str, stage: str, policy: str, user_action: str, detail: str, message_key: str):
    return FailureInfo(
        failure_code=code, stage=stage, retry_policy=policy,
        user_action=user_action, internal_detail=detail, public_message_key=message_key,
    )
