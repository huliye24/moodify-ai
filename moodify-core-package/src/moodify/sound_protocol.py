"""MSP: a small, explicit agent-to-Core audio contract.

``moodify.sound/0.1`` — preset processing jobs (original contract, unchanged).
``moodify.sound/0.2`` — adds the ``analyze`` job type: a read-only analysis
job that persists a case bundle plus the 0.2 report trio (report.json /
report.md / report.html) without modifying the source audio. Version strings
are exact; unknown keys and unknown versions are rejected, never guessed.
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
JOB_TYPES_V02 = {"analyze", "process"}
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
    required = FIELDS_V02_PROCESS if job_type == "process" else FIELDS_V02
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
