"""MSP: a small, explicit agent-to-Core audio contract.

``moodify.sound/0.1`` — preset processing jobs (original contract, unchanged).
``moodify.sound/0.2`` — adds the ``analyze`` job type (read-only analysis that
persists a case bundle plus the 0.2 report trio) and the ``compare`` job type
(reference-vs-candidate comparison: analyzes both files through the same scan
path, validates the pair, and reports loudness-aligned deltas with L2 marked
EXECUTED). Version strings are exact; unknown keys and unknown versions are
rejected, never guessed.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from moodify.v01_presets import get_preset, list_presets

PROTOCOL = "moodify.sound/0.1"
PROTOCOL_V02 = "moodify.sound/0.2"
FIELDS = {"protocol", "source", "preset", "output_dir"}
FIELDS_V02 = {"protocol", "type", "source", "output_dir"}
FIELDS_V02_PROCESS = FIELDS_V02 | {"preset"}
FIELDS_V02_COMPARE = FIELDS_V02 | {"reference"}
JOB_TYPES_V02 = {"analyze", "compare", "process"}
AUDIO_EXTENSIONS = {".wav", ".flac", ".mp3", ".aiff", ".aif", ".m4a"}


class ProtocolError(ValueError):
    pass


def validate_job(data: Any, base_dir: Path) -> dict[str, Any]:
    if isinstance(data, dict) and data.get("protocol") == PROTOCOL_V02:
        return _validate_v02(data, base_dir)
    if not isinstance(data, dict) or set(data) != FIELDS:
        raise ProtocolError(f"job must contain exactly: {', '.join(sorted(FIELDS))}")
    if data["protocol"] != PROTOCOL:
        raise ProtocolError(f"unsupported protocol; expected {PROTOCOL}")
    for key in ("source", "preset", "output_dir"):
        if not isinstance(data[key], str) or not data[key].strip():
            raise ProtocolError(f"{key} must be a non-empty string")
    if get_preset(data["preset"]) is None:
        raise ProtocolError(f"unknown preset; choose one of: {', '.join(list_presets())}")
    source = (base_dir / data["source"]).resolve()
    output_dir = (base_dir / data["output_dir"]).resolve()
    if not source.is_file():
        raise ProtocolError(f"source is not a file: {source}")
    if source.suffix.lower() not in AUDIO_EXTENSIONS:
        raise ProtocolError("unsupported audio extension")
    output = output_dir / f"{source.stem}_{data['preset']}.wav"
    if output.exists():
        raise ProtocolError(f"refusing to overwrite existing output: {output}")
    return {"protocol": PROTOCOL, "source": str(source), "preset": data["preset"],
            "output_dir": str(output_dir), "expected_output": str(output)}


def _validate_v02(data: dict[str, Any], base_dir: Path) -> dict[str, Any]:
    job_type = data.get("type")
    if job_type not in JOB_TYPES_V02:
        raise ProtocolError(
            f"type must be one of: {', '.join(sorted(JOB_TYPES_V02))}")
    if job_type == "process":
        required = FIELDS_V02_PROCESS
    elif job_type == "compare":
        required = FIELDS_V02_COMPARE
    else:
        required = FIELDS_V02
    if set(data) != required:
        raise ProtocolError(
            f"{PROTOCOL_V02} {job_type} job must contain exactly: "
            f"{', '.join(sorted(required))}")
    for key in ("source", "output_dir"):
        if not isinstance(data[key], str) or not data[key].strip():
            raise ProtocolError(f"{key} must be a non-empty string")
    source = (base_dir / data["source"]).resolve()
    output_dir = (base_dir / data["output_dir"]).resolve()
    if not source.is_file():
        raise ProtocolError(f"source is not a file: {source}")
    if source.suffix.lower() not in AUDIO_EXTENSIONS:
        raise ProtocolError("unsupported audio extension")
    job: dict[str, Any] = {
        "protocol": PROTOCOL_V02, "type": job_type,
        "source": str(source), "output_dir": str(output_dir),
    }
    if job_type == "compare":
        if not isinstance(data["reference"], str) or not data["reference"].strip():
            raise ProtocolError("reference must be a non-empty string")
        reference = (base_dir / data["reference"]).resolve()
        if not reference.is_file():
            raise ProtocolError(f"reference is not a file: {reference}")
        if reference.suffix.lower() not in AUDIO_EXTENSIONS:
            raise ProtocolError("unsupported audio extension for reference")
        if reference == source:
            raise ProtocolError("reference and source must be different files")
        job["reference"] = str(reference)
    if job_type == "process":
        if not isinstance(data["preset"], str) or not data["preset"].strip():
            raise ProtocolError("preset must be a non-empty string")
        if get_preset(data["preset"]) is None:
            raise ProtocolError(
                f"unknown preset; choose one of: {', '.join(list_presets())}")
        output = output_dir / f"{source.stem}_{data['preset']}.wav"
        if output.exists():
            raise ProtocolError(f"refusing to overwrite existing output: {output}")
        job["preset"] = data["preset"]
        job["expected_output"] = str(output)
    return job


def load_job(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise ProtocolError(f"cannot read job: {exc}") from exc
    return validate_job(data, path.resolve().parent)


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def execute_job(job: dict[str, Any]) -> dict[str, Any]:
    """Execute through the existing Core; never implement DSP in the CLI."""
    if job.get("protocol") == PROTOCOL_V02 and job.get("type") == "analyze":
        return execute_analyze_job(job)
    if job.get("protocol") == PROTOCOL_V02 and job.get("type") == "compare":
        return execute_compare_job(job)
    return _execute_process_job(job)


def _execute_process_job(job: dict[str, Any]) -> dict[str, Any]:
    from moodify.v01_pipeline import process_audio

    result = process_audio(job["source"], job["preset"], job["output_dir"])
    if not result.success:
        raise ProtocolError(result.error or "Core processing failed")
    output = Path(result.output_path)
    if not output.is_file():
        raise ProtocolError("Core reported success without an output file")
    return {
        "protocol": job.get("protocol", PROTOCOL),
        "status": "processed_review_required",
        "source": job["source"],
        "source_sha256": _sha256(Path(job["source"])),
        "preset": job["preset"],
        "core_parameters": get_preset(job["preset"])["params"],
        "output": str(output.resolve()),
        "output_sha256": _sha256(output),
        "diagnosis": result.diagnosis.to_dict(),
        "review_required": True,
    }


def execute_analyze_job(job: dict[str, Any]) -> dict[str, Any]:
    """Run the shared 1.0 analysis path and assemble the 0.2 report trio.

    Read-only toward the source audio: the case bundle and reports are written
    under ``output_dir``, never beside the source.
    """
    from moodify.auditory.protocol_report import ReportError, write_report_bundle
    from moodify.release import analyze_to_case

    case = analyze_to_case(Path(job["source"]), Path(job["output_dir"]))
    case_root = Path(job["output_dir"]) / case["case"]["case_id"]
    try:
        report = write_report_bundle(case_root)
    except ReportError as exc:
        raise ProtocolError(str(exc)) from exc
    report_path = case_root / "report.json"
    return {
        "protocol": PROTOCOL_V02,
        "type": "analyze",
        "status": "analyzed_review_required",
        "source": job["source"],
        "source_sha256": _sha256(Path(job["source"])),
        "case_id": case["case"]["case_id"],
        "case_root": str(case_root),
        "overall_status": report["technical_state"]["overall"],
        "workflow_decision": report["technical_state"]["workflow_decision"],
        "judgment_boundary": report["judgment_boundary"],
        "plan_status": report["plan"]["status"],
        "reports": {
            "json": str(report_path),
            "json_sha256": _sha256(report_path),
            "markdown": str(case_root / "report.md"),
            "html": str(case_root / "report.html"),
        },
        "review_required": True,
    }


def execute_compare_job(job: dict[str, Any]) -> dict[str, Any]:
    """Run reference-vs-candidate comparison through the shared scan path.

    Both files are analyzed with the same scan profile (two independent case
    bundles), the pair is validated (profile basis, duration tolerance,
    channels — case IDs may differ by design), and loudness-aligned deltas are
    computed. Delta spectrograms and the compare report trio are written to a
    directory derived from both case IDs under ``output_dir``. The L2 layer is
    marked EXECUTED; significance of any delta is still NOT judged (Layer C
    calibration), and no audio is modified.
    """
    from moodify.auditory.comparison import (
        build_delta_spectrograms,
        compute_deltas,
        validate_compare_pair,
    )
    from moodify.auditory.errors import (
        ComparisonChannelMismatch,
        ComparisonDurationMismatch,
        ComparisonEvidenceIncomplete,
        ComparisonInvalid,
        EvidenceHashMismatch,
        ScanProfileMismatch,
    )
    from moodify.auditory.profiles import get_profile
    from moodify.auditory.protocol_report import (
        ReportError,
        build_compare_report,
        write_compare_bundle,
    )
    from moodify.auditory.service import load_scan_evidence
    from moodify.release import PROFILE_ID, analyze_to_case

    output_dir = Path(job["output_dir"])
    reference_case = analyze_to_case(Path(job["reference"]), output_dir)
    candidate_case = analyze_to_case(Path(job["source"]), output_dir)
    reference_case_root = output_dir / reference_case["case"]["case_id"]
    candidate_case_root = output_dir / candidate_case["case"]["case_id"]
    compare_root = output_dir / (
        "compare_" + candidate_case["case"]["case_id"].removeprefix("case_")[:12]
        + "_" + reference_case["case"]["case_id"].removeprefix("case_")[:12]
    )
    try:
        profile = get_profile(PROFILE_ID)
        reference = load_scan_evidence(reference_case_root / "scan", profile)
        candidate = load_scan_evidence(candidate_case_root / "scan", profile)
        pair_checks = validate_compare_pair(reference, candidate)
        deltas = compute_deltas(reference, candidate)
        compare_root.mkdir(parents=True, exist_ok=False)
        build_delta_spectrograms(
            reference.arrays, candidate.arrays,
            gain_db=deltas.normalization_gain_db if deltas.normalization_valid else 0.0,
            out_linear=compare_root / "delta_spectrum_linear.png",
            out_log=compare_root / "delta_spectrum_log.png",
        )
        report = build_compare_report(
            compare_root,
            candidate_case_root=candidate_case_root,
            reference_case_root=reference_case_root,
            reference_evidence=reference,
            deltas=deltas,
            pair_checks=pair_checks,
        )
        write_compare_bundle(compare_root, report)
    except (
        ComparisonInvalid,
        ComparisonDurationMismatch,
        ComparisonChannelMismatch,
        ComparisonEvidenceIncomplete,
        ScanProfileMismatch,
        EvidenceHashMismatch,
        ReportError,
    ) as exc:
        raise ProtocolError(str(exc)) from exc
    report_path = compare_root / "report.json"
    return {
        "protocol": PROTOCOL_V02,
        "type": "compare",
        "status": "compared_review_required",
        "source": job["source"],
        "source_sha256": _sha256(Path(job["source"])),
        "reference": job["reference"],
        "reference_sha256": _sha256(Path(job["reference"])),
        "case_id": candidate_case["case"]["case_id"],
        "reference_case_id": reference_case["case"]["case_id"],
        "compare_root": str(compare_root),
        "loudness_normalization": report["comparison"]["loudness_normalization"],
        "delta_count": len(report["comparison"]["metric_deltas"]),
        "overall_status": report["technical_state"]["overall"],
        "workflow_decision": report["technical_state"]["workflow_decision"],
        "judgment_boundary": report["judgment_boundary"],
        "plan_status": report["plan"]["status"],
        "reports": {
            "json": str(report_path),
            "json_sha256": _sha256(report_path),
            "markdown": str(compare_root / "report.md"),
            "html": str(compare_root / "report.html"),
        },
        "review_required": True,
    }
