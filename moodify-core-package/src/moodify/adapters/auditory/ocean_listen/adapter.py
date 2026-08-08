"""Ocean Listen auditory sensor adapter (DSK-MFY-OCEAN-ABSORPTION-001).

Wires OceanRunner into the case ANALYZING stage without bypassing Moodify's
control spine: source identity is verified, evidence is registered atomically
and idempotently under `<case_root>/06_ocean_listen/`, and the sensor can
never approve, intervene, or move a case forward on its own.

Ocean Listen is a sensor, not an authority.
"""

from __future__ import annotations

import hashlib
import json
import os
import sys
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from moodify.adapters.auditory.ocean_listen.config import (
    PINNED_OCEAN_COMMIT,
    OceanRunOptions,
)
from moodify.adapters.auditory.ocean_listen.runner import OceanRunner

OCEAN_EVIDENCE_DIR = "06_ocean_listen"
REGISTRY_SCHEMA = "moodify.evidence-registry/1.0"
ARTIFACT_TYPES = (
    "raw_ocean_report",
    "auditory_observation_v1",
    "ocean_quality_gate",
    "ocean_run_manifest",
    "ocean_stdout",
    "ocean_stderr",
)


class OceanAdapterError(RuntimeError):
    pass


class SourceHashMismatch(OceanAdapterError):
    pass


@dataclass(frozen=True)
class SensorResult:
    run_id: str
    gate_status: str  # PASS | WARN | FAIL
    gate_warnings: tuple[str, ...]
    gate_errors: tuple[str, ...]
    observation: dict[str, Any] | None
    registry_path: Path
    run_dir: Path


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _canonical_hash(payload: dict[str, Any]) -> str:
    raw = json.dumps(payload, sort_keys=True, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def _iso_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _repo_root() -> Path:
    # adapter.py is at src/moodify/adapters/auditory/ocean_listen/; the git
    # repository root (where third_party/ lives) is six levels up.
    return Path(__file__).resolve().parents[6]


def _resolve_options(
    config: dict[str, Any],
    case_root: Path,
    case_id: str,
) -> OceanRunOptions:
    repo = _repo_root()
    ocean_root = Path(config.get("ocean_root", "third_party/ocean-listen"))
    if not ocean_root.is_absolute():
        ocean_root = repo / ocean_root
    output_root = Path(config.get("output_root", "artifacts/ocean_bridge")) / case_id
    if not output_root.is_absolute():
        output_root = repo / output_root
    profile = config.get("analysis_profile", "shallow")
    lyrics_mode = config.get("lyrics_mode", "disabled")
    allow_unreviewed = bool(config.get("allow_unreviewed_commit", False))
    expected_commit = config.get("upstream_commit") or PINNED_OCEAN_COMMIT
    if not allow_unreviewed:
        expected_commit = PINNED_OCEAN_COMMIT
    python_executable = config.get("python_executable") or sys.executable
    if not Path(python_executable).is_absolute():
        python_executable = str(repo / python_executable)
    return OceanRunOptions(
        ocean_root=ocean_root,
        output_root=output_root,
        cache_root=Path(config["cache_root"]) if config.get("cache_root") else None,
        python_executable=python_executable,
        deep=(profile == "deep"),
        mode=config.get("mode", "auto"),
        lyric=None if lyrics_mode == "disabled" else lyrics_mode,
        lyric_value=config.get("lyric_value"),
        language=config.get("language", "auto"),
        whisper_model=config.get("whisper_model", "small"),
        timeout_seconds=int(config.get("timeout_seconds", 1800)),
        expected_commit=expected_commit,
        analysis_profile=profile,
        lyrics_mode=lyrics_mode,
        allow_unreviewed_commit=allow_unreviewed,
    )


def _deterministic_run_id(source_sha256: str, configuration_hash: str) -> str:
    seed = f"{source_sha256}:{configuration_hash}:{PINNED_OCEAN_COMMIT}"
    return str(uuid.uuid5(uuid.NAMESPACE_URL, seed))


def _existing_registry(registry_path: Path) -> dict[str, Any] | None:
    if not registry_path.is_file():
        return None
    return json.loads(registry_path.read_text(encoding="utf-8"))


def run_sensor(
    case_id: str,
    case_root: Path,
    source_path: Path,
    source_sha256: str,
    config: dict[str, Any],
    spec_hash: str = "",
    fake: bool = False,
) -> SensorResult:
    """Execute the Ocean sensor for a case and register evidence atomically.

    - Source identity is verified against the registered case hash first.
    - A completed run with the same deterministic run_id is returned as-is
      (evidence is immutable; nothing is ever overwritten).
    - Gate FAIL still registers evidence (for the record) but the observation
      is not returned as valid analysis material.
    """
    if not source_path.is_file():
        raise SourceHashMismatch(f"source audio missing: {source_path}")
    actual = _sha256(source_path)
    if actual != source_sha256:
        raise SourceHashMismatch(
            f"source hash mismatch: registered={source_sha256} actual={actual}"
        )

    options = _resolve_options(config, case_root, case_id)
    configuration_hash = _canonical_hash(
        {
            "profile": options.analysis_profile,
            "mode": options.mode,
            "lyrics_mode": options.lyrics_mode,
            "expected_commit": options.expected_commit,
        }
    )
    run_id = _deterministic_run_id(source_sha256, configuration_hash)
    run_dir = options.output_root / run_id
    registry_path = case_root / OCEAN_EVIDENCE_DIR / "evidence_registry.json"

    existing = _existing_registry(registry_path)
    if existing is not None and existing.get("run_id") == run_id:
        return _sensor_result_from_registry(existing, registry_path, run_dir)

    if fake:
        observation = _fake_observation(run_id, source_sha256)
        gate_status, warnings, errors = "PASS", (), ()
        _write_fake_artifacts(run_dir, run_id, source_sha256, observation)
    else:
        result = OceanRunner(options).run(source_path)
        gate = result["quality_gate"]
        gate_status = gate["verdict"]
        warnings = tuple(gate.get("warnings", []))
        errors = tuple(gate.get("errors", []))
        observation = result["observation"] if gate_status != "FAIL" else None

    created_at = _iso_now()
    artifacts: list[dict[str, Any]] = []
    for artifact_type in ARTIFACT_TYPES:
        path = _artifact_path(run_dir, artifact_type)
        artifacts.append(
            {
                "artifact_type": artifact_type,
                "path": str(path),
                "artifact_sha256": _sha256(path) if path.is_file() else "",
                "case_id": case_id,
                "run_id": run_id,
                "source_sha256": source_sha256,
                "specification_hash": spec_hash,
                "upstream_commit": PINNED_OCEAN_COMMIT,
                "configuration_hash": configuration_hash,
                "created_at": created_at,
                "producer": f"ocean-listen@{PINNED_OCEAN_COMMIT[:12]}",
            }
        )

    registry = {
        "schema": REGISTRY_SCHEMA,
        "case_id": case_id,
        "run_id": run_id,
        "source_sha256": source_sha256,
        "specification_hash": spec_hash,
        "upstream_commit": PINNED_OCEAN_COMMIT,
        "configuration_hash": configuration_hash,
        "created_at": created_at,
        "gate": {"status": gate_status, "warnings": list(warnings), "errors": list(errors)},
        "artifacts": artifacts,
    }
    registry_path.parent.mkdir(parents=True, exist_ok=True)
    _atomic_write(registry_path, registry)

    return SensorResult(
        run_id=run_id,
        gate_status=gate_status,
        gate_warnings=warnings,
        gate_errors=errors,
        observation=observation,
        registry_path=registry_path,
        run_dir=run_dir,
    )


def _sensor_result_from_registry(
    registry: dict[str, Any],
    registry_path: Path,
    run_dir: Path,
) -> SensorResult:
    gate = registry.get("gate", {})
    observation = None
    if gate.get("status") != "FAIL":
        observation_path = _artifact_path(run_dir, "auditory_observation_v1")
        if observation_path.is_file():
            observation = json.loads(observation_path.read_text(encoding="utf-8"))
    return SensorResult(
        run_id=registry["run_id"],
        gate_status=gate.get("status", "FAIL"),
        gate_warnings=tuple(gate.get("warnings", [])),
        gate_errors=tuple(gate.get("errors", [])),
        observation=observation,
        registry_path=registry_path,
        run_dir=run_dir,
    )


def _artifact_path(run_dir: Path, artifact_type: str) -> Path:
    mapping = {
        "raw_ocean_report": run_dir / "raw" / "ocean_report.json",
        "auditory_observation_v1": run_dir / "normalized" / "auditory_observation.v1.json",
        "ocean_quality_gate": run_dir / "quality" / "gate_result.json",
        "ocean_run_manifest": run_dir / "evidence" / "run_manifest.json",
        "ocean_stdout": run_dir / "logs" / "stdout.log",
        "ocean_stderr": run_dir / "logs" / "stderr.log",
    }
    return mapping[artifact_type]


def _atomic_write(path: Path, payload: dict[str, Any]) -> None:
    tmp = path.with_suffix(".tmp")
    tmp.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    os.replace(tmp, path)


def _write_fake_artifacts(
    run_dir: Path,
    run_id: str,
    source_sha256: str,
    observation: dict[str, Any],
) -> None:
    raw_dir = run_dir / "raw"
    normalized_dir = run_dir / "normalized"
    quality_dir = run_dir / "quality"
    evidence_dir = run_dir / "evidence"
    logs_dir = run_dir / "logs"
    for directory in (raw_dir, normalized_dir, quality_dir, evidence_dir, logs_dir):
        directory.mkdir(parents=True, exist_ok=True)
    (raw_dir / "ocean_report.json").write_text(
        json.dumps({"status": "ok", "source_sha256": source_sha256}), encoding="utf-8"
    )
    (normalized_dir / "auditory_observation.v1.json").write_text(
        json.dumps(observation, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    (quality_dir / "gate_result.json").write_text(
        json.dumps({"verdict": "PASS", "issues": [], "metrics": {}}), encoding="utf-8"
    )
    (evidence_dir / "run_manifest.json").write_text(
        json.dumps(
            {
                "status": "COMPLETED_WITH_SENSOR_EVIDENCE",
                "run_id": run_id,
                "source_sha256": source_sha256,
                "authority": {
                    "sensor_output_only": True,
                    "may_approve_artistic_decision": False,
                    "may_transition_to_technically_validated": False,
                },
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    (logs_dir / "stdout.log").write_text("fake ocean stdout\n", encoding="utf-8")
    (logs_dir / "stderr.log").write_text("", encoding="utf-8")


def _fake_observation(run_id: str, source_sha256: str) -> dict[str, Any]:
    return {
        "schema_version": "moodify.auditory-observation/1.0",
        "observation_id": f"obs-{run_id[:12]}",
        "run_id": run_id,
        "created_at": _iso_now(),
        "source": {"path": "", "sha256": source_sha256, "size_bytes": 0},
        "analyzer": {"name": "ocean-listen", "commit": PINNED_OCEAN_COMMIT},
        "classification": {"authority": "sensor_only"},
        "global_features": {},
        "stems": [],
        "notes": [],
        "voice": {"status": "experimental"},
        "lyrics": None,
        "timeline": [],
        "artifacts": [],
        "uncertainty": {"labels_are_experimental": True},
        "provenance": {"fake_process": True},
        "quality_gate": {"verdict": "PASS", "issues": [], "metrics": {}},
    }
