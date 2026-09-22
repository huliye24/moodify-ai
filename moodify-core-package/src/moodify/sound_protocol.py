"""MSP/0.1: a small, explicit agent-to-Core audio processing contract."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from moodify.v01_presets import get_preset, list_presets

PROTOCOL = "moodify.sound/0.1"
FIELDS = {"protocol", "source", "preset", "output_dir"}


class ProtocolError(ValueError):
    pass


def validate_job(data: Any, base_dir: Path) -> dict[str, Any]:
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
    if source.suffix.lower() not in {".wav", ".flac", ".mp3", ".aiff", ".aif", ".m4a"}:
        raise ProtocolError("unsupported audio extension")
    output = output_dir / f"{source.stem}_{data['preset']}.wav"
    if output.exists():
        raise ProtocolError(f"refusing to overwrite existing output: {output}")
    return {"protocol": PROTOCOL, "source": str(source), "preset": data["preset"],
            "output_dir": str(output_dir), "expected_output": str(output)}


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
    """Execute through the existing Core pipeline; never implement DSP in the CLI."""
    from moodify.v01_pipeline import process_audio

    result = process_audio(job["source"], job["preset"], job["output_dir"])
    if not result.success:
        raise ProtocolError(result.error or "Core processing failed")
    output = Path(result.output_path)
    if not output.is_file():
        raise ProtocolError("Core reported success without an output file")
    return {
        "protocol": PROTOCOL,
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
