"""Historical compatibility — load, validate, and migrate historical records.

Every compatibility claim is backed by executable evidence: exact load,
evidence-bearing migration, or actionable rejection. Original artifacts are
never overwritten; migration always produces a new file with lineage metadata.

Part of DSK-MFY-AUX-HARDENING-002 Batch C.
"""

from __future__ import annotations

import hashlib
import json
import shutil
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from moodify_runtime.schema_registry import (
    current_version,
    is_supported,
    validate_record_type,
)
from moodify_runtime.utils import utc_now_iso


@dataclass
class MigrationResult:
    """Outcome of a migration attempt."""
    success: bool = False
    record_type: str = ""
    source_version: str = ""
    target_version: str = ""
    source_path: str = ""
    target_path: str = ""
    source_hash: str = ""
    target_hash: str = ""
    lineage: dict[str, Any] = field(default_factory=dict)
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    migrated_at: str = field(default_factory=utc_now_iso)
    tool_identity: str = "moodify_runtime.historical_compatibility v1.0.0"

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class LoadResult:
    """Outcome of a historical record load attempt."""
    success: bool = False
    record_type: str = ""
    schema_version: str = ""
    data: dict[str, Any] = field(default_factory=dict)
    unknown_fields: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


# ── Required fields per record type ───────────────────────────────────
_REQUIRED_FIELDS: dict[str, set[str]] = {
    "treatment": {"record_file", "song_id", "preset"},
    "treatment_summary": {"schema_version", "summary_type", "record_count", "presets"},
    "workspace_project": {"project_id", "name"},
    "workspace_brief": {"brief_id", "project_id"},
    "rights_manifest": {"schema_version", "gate_id", "assets"},
    "approval": {"approval_id", "reviewer", "action"},
    "delivery": {"delivery_id", "job_id", "candidate_id"},
    "craft_record": {"craft_id"},
    "proposal": {"proposal_id", "status"},
}

# ── Migration maps: source_version → target_version ───────────────────
# Each entry is a callable that transforms the record dict.
_MIGRATION_MAP: dict[str, dict[str, str]] = {
    "treatment": {"0.1.0": "0.2.0"},
    "treatment_summary": {},
    "workspace_project": {},
    "workspace_brief": {},
    "rights_manifest": {},
    "approval": {},
    "delivery": {},
    "craft_record": {},
    "proposal": {},
}


def _sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _hash_file(path: Path) -> str:
    if not path.is_file():
        return ""
    return _sha256_hex(path.read_bytes())


# ═══════════════════════════════════════════════════════════════════════
# Load
# ═══════════════════════════════════════════════════════════════════════


def load_historical_record(
    path: str | Path,
    record_type: str,
) -> LoadResult:
    """Load a historical record and validate its schema version.

    Unknown fields are preserved and reported. Malformed or unsupported
    records return a failed LoadResult with actionable error messages.
    The original file is never modified.
    """
    path = Path(path)
    result = LoadResult(record_type=record_type)
    base_errors: list[str] = []

    try:
        validate_record_type(record_type)
    except ValueError as exc:
        base_errors.append(str(exc))
        result.errors = base_errors
        return result

    if not path.is_file():
        base_errors.append(f"File not found: {path}")
        result.errors = base_errors
        return result

    try:
        raw = path.read_text(encoding="utf-8")
    except OSError as exc:
        base_errors.append(f"Cannot read file: {exc}")
        result.errors = base_errors
        return result

    try:
        data = json.loads(raw)
    except json.JSONDecodeError as exc:
        base_errors.append(f"Invalid JSON: {exc}")
        result.errors = base_errors
        return result

    if not isinstance(data, dict):
        base_errors.append("Record root must be a JSON object")
        result.errors = base_errors
        return result

    schema_version = data.get("schema_version", "unknown")
    result.schema_version = schema_version
    result.data = data

    if not is_supported(record_type, schema_version):
        current = current_version(record_type)
        supported_list = sorted(
            _SUPPORTED_VERSIONS_FOR_TYPE(record_type)
        )
        base_errors.append(
            f"Unsupported schema version {schema_version!r} for {record_type}. "
            f"Supported: {supported_list}. Current: {current}."
        )

    # Check required fields
    required = _REQUIRED_FIELDS.get(record_type, set())
    missing = required - set(data.keys())
    if missing:
        base_errors.append(
            f"Missing required fields for {record_type} v{schema_version}: "
            f"{sorted(missing)}"
        )

    # Detect unknown fields (fields not in the known required set)
    known_fields = _REQUIRED_FIELDS.get(record_type, set()) | {
        "schema_version", "record_type", "created_at", "updated_at",
        "rms_delta_db", "after_gain_match_db", "warning_level", "crest_delta",
        "dynamic_range_delta_db", "correlation_delta", "presence_delta_db",
        "air_delta_db", "feedback_status", "better_than_before", "clarity",
        "warmth", "space", "harshness_control", "plastic_feel_control",
        "artifact_control", "target_fit", "volume_matched", "task_id",
        "summary_type", "record_count", "presets", "records",
        "feedback_overview", "known_absent", "errors", "status",
        "description", "client_id", "project_id", "name", "brief_id",
        "gate_id", "assets", "reviewer", "action", "reason", "approval_id",
        "board_id", "operator_job_id", "mrs_delta", "over_dark_level",
        "gate_decision", "delivery_id", "job_id", "candidate_id",
        "final_audio_path", "report_path", "archive_path", "operator_decision",
        "delivered_at", "notes", "human_approved", "approved_by",
        "rights_manifest", "rights_asset_id", "craft_id",
        "adoption_status", "source", "source_run_id", "promotion_evidence",
        "proposal_id", "craft_data", "version_history", "processing_chain",
        "expected_improvement", "mrs_score", "mrs_score_delta",
        "risk_conditions", "failure_cases", "operator_notes",
        "human_approval", "rights_evidence", "output_path",
        "source_job_id", "source_candidate_id", "audio_class",
        "source_proposal_id", "preset",
    }
    unknown = [k for k in data if k not in known_fields]
    result.unknown_fields = unknown

    if not base_errors:
        result.success = True
    else:
        result.errors = base_errors

    return result


def _SUPPORTED_VERSIONS_FOR_TYPE(record_type: str) -> set[str]:
    from moodify_runtime.schema_registry import SUPPORTED_SCHEMA_VERSIONS
    return SUPPORTED_SCHEMA_VERSIONS.get(record_type, set())


# ═══════════════════════════════════════════════════════════════════════
# Migration
# ═══════════════════════════════════════════════════════════════════════


def migrate_historical_record(
    source_path: str | Path,
    record_type: str,
    target_dir: str | Path,
    target_version: str | None = None,
) -> MigrationResult:
    """Migrate a historical record to a target schema version.

    The original file is **never** overwritten. Migration produces a new file
    under ``target_dir`` with full lineage metadata embedded in the record.

    Lineage includes:
      - source and target versions
      - source identity (path + SHA-256 hash)
      - target identity (path + SHA-256 hash)
      - tool identity and version
      - migration timestamp

    Failed migration leaves the source file intact and returns an error-bearing
    ``MigrationResult``.
    """
    source_path = Path(source_path)
    target_dir = Path(target_dir)
    result = MigrationResult(
        success=False,
        record_type=record_type,
        source_version="",
        target_version=target_version or "",
        source_path=str(source_path),
    )

    # 1. Load
    load = load_historical_record(source_path, record_type)
    if not load.success:
        result.errors = load.errors
        return result

    result.source_version = load.schema_version

    # 2. Determine target version
    if target_version is None:
        target_version = current_version(record_type)
    if target_version is None:
        result.errors.append(f"No current version for {record_type}")
        return result

    result.target_version = target_version

    if not is_supported(record_type, target_version):
        result.errors.append(
            f"Target version {target_version!r} is not supported for {record_type}"
        )
        return result

    if load.schema_version == target_version:
        # No migration needed, but still produce a copy with lineage
        result.warnings.append(
            f"Source is already at target version {target_version}; "
            f"copying with lineage metadata"
        )

    # 3. Compute source hash
    result.source_hash = _hash_file(source_path)

    # 4. Apply migration transforms
    data = dict(load.data)
    migration_path = f"{load.schema_version}->{target_version}"
    data = _apply_migration(record_type, load.schema_version, target_version, data)

    # 5. Update schema version and add lineage
    data["schema_version"] = target_version
    if "_migration_lineage" not in data:
        data["_migration_lineage"] = []
    data["_migration_lineage"].append({
        "source_version": load.schema_version,
        "target_version": target_version,
        "source_hash": result.source_hash,
        "source_path": str(source_path.resolve()),
        "migration_path": migration_path,
        "tool_identity": result.tool_identity,
        "migrated_at": result.migrated_at,
    })

    # 6. Write migrated record to target directory
    target_dir = Path(target_dir)
    target_dir.mkdir(parents=True, exist_ok=True)
    stem = source_path.stem
    target_path = target_dir / f"{stem}_migrated_{target_version}.json"

    target_content = json.dumps(data, ensure_ascii=False, indent=2) + "\n"
    target_path.write_text(target_content, encoding="utf-8")

    result.target_path = str(target_path)
    result.target_hash = _hash_file(target_path)
    result.lineage = data["_migration_lineage"]
    result.success = True

    return result


def _apply_migration(
    record_type: str,
    source_version: str,
    target_version: str,
    data: dict[str, Any],
) -> dict[str, Any]:
    """Apply version-specific migration transforms. Returns modified copy."""
    result = dict(data)

    if record_type == "treatment" and source_version == "0.1.0" and target_version == "0.2.0":
        # v0.1.0 → v0.2.0: add treatment_id if not present
        if "treatment_id" not in result:
            import uuid
            result["treatment_id"] = f"TRT_{uuid.uuid4().hex[:12].upper()}"
        # Add v0.2.0 fields with safe defaults
        result.setdefault("processing_chain_version", "v01")
        result.setdefault("mrs_open_v031_delta", None)
        if "rms_delta_db" in result:
            result["loudness_delta_db"] = result["rms_delta_db"]

    return result


# ═══════════════════════════════════════════════════════════════════════
# Synthetic Fixture Builders
# ═══════════════════════════════════════════════════════════════════════


def build_v01_treatment_fixture(
    song_id: str = "fixture_song_001",
    preset: str = "warm_vocal",
) -> dict[str, Any]:
    """Build a synthetic v0.1 Treatment record fixture."""
    return {
        "schema_version": "0.1.0",
        "record_type": "treatment",
        "record_file": f"{song_id}_{preset}.json",
        "song_id": song_id,
        "preset": preset,
        "task_id": f"task_{song_id}_{preset}",
        "rms_delta_db": 5.2,
        "after_gain_match_db": -5.2,
        "warning_level": "moderate",
        "crest_delta": -1.3,
        "dynamic_range_delta_db": -4.1,
        "correlation_delta": -0.04,
        "presence_delta_db": 1.5,
        "air_delta_db": 0.9,
        "feedback_status": "completed",
        "better_than_before": True,
        "clarity": 4,
        "warmth": 5,
        "space": 4,
        "harshness_control": 4,
        "plastic_feel_control": 3,
        "artifact_control": 4,
        "target_fit": 4,
        "volume_matched": True,
    }


def build_v2_workspace_project_fixture(
    project_id: str = "PROJ_FIXTURE_001",
    name: str = "Fixture Project v2",
) -> dict[str, Any]:
    """Build a synthetic v2 Workspace Project fixture."""
    return {
        "schema_version": "2.0.0",
        "record_type": "workspace_project",
        "project_id": project_id,
        "client_id": "CLIENT_FIXTURE_001",
        "name": name,
        "description": "Synthetic fixture project for compatibility testing.",
        "status": "active",
        "created_at": "2026-06-01T00:00:00Z",
        "updated_at": "2026-06-01T00:00:00Z",
    }


def build_v2_workspace_brief_fixture(
    brief_id: str = "BRIEF_FIXTURE_001",
    project_id: str = "PROJ_FIXTURE_001",
) -> dict[str, Any]:
    """Build a synthetic v2 Workspace Brief fixture."""
    return {
        "schema_version": "2.0.0",
        "record_type": "workspace_brief",
        "brief_id": brief_id,
        "project_id": project_id,
        "target_emotion": "warm",
        "preserve": ["vocal_clarity", "natural_dynamics"],
        "avoid": ["distortion", "pumping"],
        "priority": "standard",
        "created_at": "2026-06-01T00:00:00Z",
    }


def build_rights_manifest_fixture() -> dict[str, Any]:
    """Build a synthetic v1.0 Rights Manifest fixture."""
    return {
        "schema_version": "1.0.0",
        "record_type": "rights_manifest",
        "gate_id": "GATE_FIXTURE_001",
        "assets": [
            {
                "asset_id": "FIXTURE_ASSET_001",
                "source_path": "/fixtures/audio/song_001.wav",
                "status": "ready",
                "rights_holder": "Fixture Rights Holder",
                "license": "synthetic-fixture",
            },
        ],
    }


def build_approval_record_fixture(
    approval_id: str = "APR_FIXTURE_001",
) -> dict[str, Any]:
    """Build a synthetic v1.0 Approval Record fixture."""
    return {
        "schema_version": "1.0.0",
        "record_type": "approval",
        "approval_id": approval_id,
        "board_id": "BOARD_FIXTURE_001",
        "operator_job_id": "JOB_FIXTURE_001",
        "reviewer": "fixture_reviewer",
        "action": "approve",
        "reason": "Synthetic fixture for compatibility testing.",
        "mrs_delta": 5.0,
        "over_dark_level": "low",
        "gate_decision": "approve",
        "created_at": "2026-06-01T00:00:00Z",
    }


def build_delivery_record_fixture(
    delivery_id: str = "DLV_FIXTURE_001",
) -> dict[str, Any]:
    """Build a synthetic v1.0 Delivery Record fixture."""
    return {
        "schema_version": "1.0.0",
        "record_type": "delivery",
        "delivery_id": delivery_id,
        "job_id": "JOB_FIXTURE_001",
        "candidate_id": "CAND_FIXTURE_001",
        "final_audio_path": "/fixtures/output/song_001_processed.wav",
        "report_path": "/fixtures/reports/song_001_report.json",
        "archive_path": "/fixtures/archive/song_001.zip",
        "operator_decision": "approved",
        "delivered_at": "2026-06-01T00:00:00Z",
        "notes": "Synthetic fixture delivery.",
        "human_approved": True,
        "approved_by": "fixture_engineer",
        "rights_manifest": "fixture_manifest.json",
        "rights_asset_id": "FIXTURE_ASSET_001",
    }


def build_treatment_summary_fixture() -> dict[str, Any]:
    """Build a synthetic v0.1 Treatment Summary fixture."""
    return {
        "schema_version": "0.1.0",
        "summary_type": "moodify_treatment_record_summary",
        "record_count": 1,
        "feedback_overview": {
            "total_records": 1,
            "completed_records": 0,
            "pending_records": 1,
            "feedback_coverage": 0.0,
            "better_yes": 0,
            "better_no": 0,
            "better_uncertain": 0,
            "global_better_rate": 0.0,
        },
        "presets": {},
        "records": [],
    }
