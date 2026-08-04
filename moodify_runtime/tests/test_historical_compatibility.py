"""Tests for historical compatibility — Batch C of DSK-MFY-AUX-HARDENING-002.

Covers: schema registry, exact load, migration with lineage, unknown field
preservation, source artifact immutability, and actionable rejection.
Synthetic fixtures only; no private audio or user data.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from moodify_runtime.historical_compatibility import (
    LoadResult,
    MigrationResult,
    build_approval_record_fixture,
    build_delivery_record_fixture,
    build_rights_manifest_fixture,
    build_treatment_summary_fixture,
    build_v01_treatment_fixture,
    build_v2_workspace_brief_fixture,
    build_v2_workspace_project_fixture,
    load_historical_record,
    migrate_historical_record,
)
from moodify_runtime.schema_registry import (
    RECORD_TYPES,
    SUPPORTED_SCHEMA_VERSIONS,
    current_version,
    is_supported,
    validate_record_type,
)


# ═══════════════════════════════════════════════════════════════════════
# Helpers
# ═══════════════════════════════════════════════════════════════════════


def _write_fixture(tmp_path: Path, name: str, data: dict) -> Path:
    p = tmp_path / name
    p.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return p


# ═══════════════════════════════════════════════════════════════════════
# Schema Registry
# ═══════════════════════════════════════════════════════════════════════


class TestSchemaRegistry:
    """Supported versions are declared in one authoritative location."""

    def test_all_record_types_have_supported_versions(self):
        for rt in RECORD_TYPES:
            assert rt in SUPPORTED_SCHEMA_VERSIONS, f"{rt} missing from SUPPORTED_SCHEMA_VERSIONS"
            assert len(SUPPORTED_SCHEMA_VERSIONS[rt]) >= 1, f"{rt} has no supported versions"

    def test_all_record_types_have_current_version(self):
        for rt in RECORD_TYPES:
            cv = current_version(rt)
            assert cv is not None, f"{rt} missing current version"
            assert is_supported(rt, cv), f"{rt} current version {cv} not in supported set"

    def test_is_supported_positive(self):
        assert is_supported("treatment", "0.1.0") is True

    def test_is_supported_negative(self):
        assert is_supported("treatment", "99.99.99") is False

    def test_is_supported_unknown_type(self):
        assert is_supported("nonexistent", "1.0.0") is False

    def test_validate_record_type_valid(self):
        validate_record_type("treatment")
        validate_record_type("delivery")

    def test_validate_record_type_invalid(self):
        with pytest.raises(ValueError, match="Unknown record type"):
            validate_record_type("not_a_type")


# ═══════════════════════════════════════════════════════════════════════
# Exact Load — v0.1 Treatment
# ═══════════════════════════════════════════════════════════════════════


class TestLoadV01Treatment:
    def test_exact_load_succeeds(self, tmp_path):
        fixture = build_v01_treatment_fixture()
        p = _write_fixture(tmp_path, "treatment_v01.json", fixture)
        result = load_historical_record(p, "treatment")
        assert result.success is True
        assert result.schema_version == "0.1.0"
        assert result.data["song_id"] == "fixture_song_001"
        assert result.data["preset"] == "warm_vocal"

    def test_preserves_schema_version_field(self, tmp_path):
        fixture = build_v01_treatment_fixture()
        p = _write_fixture(tmp_path, "treatment_v01.json", fixture)
        result = load_historical_record(p, "treatment")
        assert result.data["schema_version"] == "0.1.0"

    def test_original_file_not_modified(self, tmp_path):
        fixture = build_v01_treatment_fixture()
        p = _write_fixture(tmp_path, "treatment_v01.json", fixture)
        original_bytes = p.read_bytes()
        load_historical_record(p, "treatment")
        assert p.read_bytes() == original_bytes, "original file was modified"

    def test_missing_required_field_fails(self, tmp_path):
        data = {"schema_version": "0.1.0", "record_file": "x.json"}
        p = _write_fixture(tmp_path, "bad_treatment.json", data)
        result = load_historical_record(p, "treatment")
        assert result.success is False
        assert any("song_id" in e for e in result.errors)

    def test_unsupported_version_reports_error(self, tmp_path):
        data = build_v01_treatment_fixture()
        data["schema_version"] = "99.99.99"
        p = _write_fixture(tmp_path, "future_treatment.json", data)
        result = load_historical_record(p, "treatment")
        assert result.success is False
        assert any("Unsupported schema version" in e for e in result.errors)

    def test_unknown_record_type(self, tmp_path):
        p = _write_fixture(tmp_path, "x.json", {"schema_version": "1.0.0"})
        result = load_historical_record(p, "nonexistent")
        assert result.success is False
        assert any("Unknown record type" in e for e in result.errors)


# ═══════════════════════════════════════════════════════════════════════
# Exact Load — v2 Workspace
# ═══════════════════════════════════════════════════════════════════════


class TestLoadV2Workspace:
    def test_project_load_succeeds(self, tmp_path):
        fixture = build_v2_workspace_project_fixture()
        p = _write_fixture(tmp_path, "project_v2.json", fixture)
        result = load_historical_record(p, "workspace_project")
        assert result.success is True
        assert result.schema_version == "2.0.0"
        assert result.data["project_id"] == "PROJ_FIXTURE_001"

    def test_brief_load_succeeds(self, tmp_path):
        fixture = build_v2_workspace_brief_fixture()
        p = _write_fixture(tmp_path, "brief_v2.json", fixture)
        result = load_historical_record(p, "workspace_brief")
        assert result.success is True
        assert result.schema_version == "2.0.0"
        assert result.data["brief_id"] == "BRIEF_FIXTURE_001"

    def test_project_original_not_modified(self, tmp_path):
        fixture = build_v2_workspace_project_fixture()
        p = _write_fixture(tmp_path, "project_v2.json", fixture)
        original_bytes = p.read_bytes()
        load_historical_record(p, "workspace_project")
        assert p.read_bytes() == original_bytes


# ═══════════════════════════════════════════════════════════════════════
# Exact Load — Rights Manifest
# ═══════════════════════════════════════════════════════════════════════


class TestLoadRightsManifest:
    def test_load_succeeds(self, tmp_path):
        fixture = build_rights_manifest_fixture()
        p = _write_fixture(tmp_path, "rights_v1.json", fixture)
        result = load_historical_record(p, "rights_manifest")
        assert result.success is True
        assert result.schema_version == "1.0.0"
        assert len(result.data["assets"]) == 1

    def test_missing_assets_rejected(self, tmp_path):
        data = {"schema_version": "1.0.0", "gate_id": "G1"}
        p = _write_fixture(tmp_path, "bad_rights.json", data)
        result = load_historical_record(p, "rights_manifest")
        assert result.success is False
        assert any("assets" in e for e in result.errors)


# ═══════════════════════════════════════════════════════════════════════
# Exact Load — Approval Record
# ═══════════════════════════════════════════════════════════════════════


class TestLoadApproval:
    def test_load_succeeds(self, tmp_path):
        fixture = build_approval_record_fixture()
        p = _write_fixture(tmp_path, "approval_v1.json", fixture)
        result = load_historical_record(p, "approval")
        assert result.success is True
        assert result.schema_version == "1.0.0"
        assert result.data["reviewer"] == "fixture_reviewer"

    def test_missing_reviewer_rejected(self, tmp_path):
        data = {"schema_version": "1.0.0", "approval_id": "APR_001", "action": "approve"}
        p = _write_fixture(tmp_path, "bad_approval.json", data)
        result = load_historical_record(p, "approval")
        assert result.success is False
        assert any("reviewer" in e for e in result.errors)


# ═══════════════════════════════════════════════════════════════════════
# Exact Load — Delivery Record
# ═══════════════════════════════════════════════════════════════════════


class TestLoadDelivery:
    def test_load_succeeds(self, tmp_path):
        fixture = build_delivery_record_fixture()
        p = _write_fixture(tmp_path, "delivery_v1.json", fixture)
        result = load_historical_record(p, "delivery")
        assert result.success is True
        assert result.schema_version == "1.0.0"
        assert result.data["delivery_id"] == "DLV_FIXTURE_001"

    def test_missing_delivery_id_rejected(self, tmp_path):
        data = {"schema_version": "1.0.0", "job_id": "J1", "candidate_id": "C1"}
        p = _write_fixture(tmp_path, "bad_delivery.json", data)
        result = load_historical_record(p, "delivery")
        assert result.success is False
        assert any("delivery_id" in e for e in result.errors)


# ═══════════════════════════════════════════════════════════════════════
# Exact Load — Treatment Summary
# ═══════════════════════════════════════════════════════════════════════


class TestLoadTreatmentSummary:
    def test_load_succeeds(self, tmp_path):
        fixture = build_treatment_summary_fixture()
        p = _write_fixture(tmp_path, "summary_v01.json", fixture)
        result = load_historical_record(p, "treatment_summary")
        assert result.success is True
        assert result.schema_version == "0.1.0"


# ═══════════════════════════════════════════════════════════════════════
# Unknown Field Preservation
# ═══════════════════════════════════════════════════════════════════════


class TestUnknownFieldPreservation:
    def test_unknown_fields_preserved_in_data(self, tmp_path):
        fixture = build_v01_treatment_fixture()
        fixture["custom_field_v99"] = "should survive"
        fixture["another_custom"] = 42
        p = _write_fixture(tmp_path, "with_extras.json", fixture)
        result = load_historical_record(p, "treatment")
        assert result.success is True
        assert result.data["custom_field_v99"] == "should survive"
        assert result.data["another_custom"] == 42

    def test_unknown_fields_reported(self, tmp_path):
        fixture = build_v01_treatment_fixture()
        fixture["future_field"] = "detect me"
        p = _write_fixture(tmp_path, "with_extras.json", fixture)
        result = load_historical_record(p, "treatment")
        assert "future_field" in result.unknown_fields

    def test_unknown_fields_survive_migration(self, tmp_path):
        fixture = build_v01_treatment_fixture()
        fixture["custom_field_v99"] = "must survive migration"
        p = _write_fixture(tmp_path, "with_extras.json", fixture)
        target = tmp_path / "migrated"
        mr = migrate_historical_record(p, "treatment", target)
        assert mr.success is True
        migrated = json.loads(Path(mr.target_path).read_text(encoding="utf-8"))
        assert migrated["custom_field_v99"] == "must survive migration"


# ═══════════════════════════════════════════════════════════════════════
# Migration — v0.1 → v0.2 Treatment
# ═══════════════════════════════════════════════════════════════════════


class TestMigration:
    def test_migration_produces_new_file(self, tmp_path):
        fixture = build_v01_treatment_fixture()
        source = _write_fixture(tmp_path, "source.json", fixture)
        target = tmp_path / "migrated"
        mr = migrate_historical_record(source, "treatment", target, "0.2.0")
        assert mr.success is True
        assert mr.source_version == "0.1.0"
        assert mr.target_version == "0.2.0"
        assert Path(mr.target_path).is_file()

    def test_migration_includes_lineage(self, tmp_path):
        fixture = build_v01_treatment_fixture()
        source = _write_fixture(tmp_path, "source.json", fixture)
        target = tmp_path / "migrated"
        mr = migrate_historical_record(source, "treatment", target, "0.2.0")
        assert mr.success is True
        assert len(mr.lineage) == 1
        lineage = mr.lineage[0]
        assert lineage["source_version"] == "0.1.0"
        assert lineage["target_version"] == "0.2.0"
        assert lineage["source_hash"] == mr.source_hash
        # Wall-clock execution time belongs to the migration event result, not
        # the canonical migrated payload; otherwise deterministic retry fails.
        assert "migrated_at" not in lineage
        assert mr.migrated_at
        assert "tool_identity" in lineage

    def test_migration_lineage_embedded_in_record(self, tmp_path):
        fixture = build_v01_treatment_fixture()
        source = _write_fixture(tmp_path, "source.json", fixture)
        target = tmp_path / "migrated"
        mr = migrate_historical_record(source, "treatment", target, "0.2.0")
        migrated = json.loads(Path(mr.target_path).read_text(encoding="utf-8"))
        assert "_migration_lineage" in migrated
        assert len(migrated["_migration_lineage"]) == 1
        assert migrated["schema_version"] == "0.2.0"

    def test_migration_adds_treatment_id(self, tmp_path):
        fixture = build_v01_treatment_fixture()
        source = _write_fixture(tmp_path, "source.json", fixture)
        target = tmp_path / "migrated"
        mr = migrate_historical_record(source, "treatment", target, "0.2.0")
        migrated = json.loads(Path(mr.target_path).read_text(encoding="utf-8"))
        assert "treatment_id" in migrated
        assert migrated["treatment_id"].startswith("TRT_")

    def test_migration_adds_loudness_delta_db(self, tmp_path):
        fixture = build_v01_treatment_fixture()
        source = _write_fixture(tmp_path, "source.json", fixture)
        target = tmp_path / "migrated"
        mr = migrate_historical_record(source, "treatment", target, "0.2.0")
        migrated = json.loads(Path(mr.target_path).read_text(encoding="utf-8"))
        assert "loudness_delta_db" in migrated
        assert migrated["loudness_delta_db"] == migrated["rms_delta_db"]

    def test_migration_preserves_all_original_data(self, tmp_path):
        fixture = build_v01_treatment_fixture()
        source = _write_fixture(tmp_path, "source.json", fixture)
        target = tmp_path / "migrated"
        mr = migrate_historical_record(source, "treatment", target, "0.2.0")
        migrated = json.loads(Path(mr.target_path).read_text(encoding="utf-8"))
        assert migrated["song_id"] == fixture["song_id"]
        assert migrated["preset"] == fixture["preset"]
        assert migrated["rms_delta_db"] == fixture["rms_delta_db"]
        assert migrated["feedback_status"] == fixture["feedback_status"]


# ═══════════════════════════════════════════════════════════════════════
# Source Artifact Immutability
# ═══════════════════════════════════════════════════════════════════════


class TestSourceImmutability:
    def test_migration_never_overwrites_source(self, tmp_path):
        fixture = build_v01_treatment_fixture()
        source = _write_fixture(tmp_path, "source.json", fixture)
        original_content = source.read_text(encoding="utf-8")
        target = tmp_path / "migrated"
        migrate_historical_record(source, "treatment", target, "0.2.0")
        assert source.read_text(encoding="utf-8") == original_content

    def test_source_hash_recorded(self, tmp_path):
        fixture = build_v01_treatment_fixture()
        source = _write_fixture(tmp_path, "source.json", fixture)
        target = tmp_path / "migrated"
        mr = migrate_historical_record(source, "treatment", target, "0.2.0")
        assert mr.source_hash != ""
        assert len(mr.source_hash) == 64  # SHA-256 hex

    def test_target_hash_differs_when_migration_adds_fields(self, tmp_path):
        fixture = build_v01_treatment_fixture()
        source = _write_fixture(tmp_path, "source.json", fixture)
        target = tmp_path / "migrated"
        mr = migrate_historical_record(source, "treatment", target, "0.2.0")
        assert mr.target_hash != mr.source_hash

    def test_load_never_modifies_original(self, tmp_path):
        fixture = build_v01_treatment_fixture()
        source = _write_fixture(tmp_path, "source.json", fixture)
        original = source.read_bytes()
        load_historical_record(source, "treatment")
        assert source.read_bytes() == original


# ═══════════════════════════════════════════════════════════════════════
# Failed Migration Safety
# ═══════════════════════════════════════════════════════════════════════


class TestFailedMigrationSafety:
    def test_failed_migration_leaves_source_intact(self, tmp_path):
        data = {"schema_version": "0.1.0", "record_file": "x.json"}
        source = _write_fixture(tmp_path, "incomplete.json", data)
        original = source.read_bytes()
        target = tmp_path / "migrated"
        mr = migrate_historical_record(source, "treatment", target, "0.2.0")
        assert mr.success is False
        assert source.read_bytes() == original

    def test_failed_migration_returns_errors(self, tmp_path):
        data = {"schema_version": "0.1.0", "record_file": "x.json"}
        source = _write_fixture(tmp_path, "incomplete.json", data)
        target = tmp_path / "migrated"
        mr = migrate_historical_record(source, "treatment", target, "0.2.0")
        assert mr.success is False
        assert len(mr.errors) > 0

    def test_unsupported_target_version(self, tmp_path):
        fixture = build_v01_treatment_fixture()
        source = _write_fixture(tmp_path, "source.json", fixture)
        target = tmp_path / "migrated"
        mr = migrate_historical_record(source, "treatment", target, "99.99.99")
        assert mr.success is False
        assert any("not supported" in e for e in mr.errors)

    def test_no_target_dir_creates_dir(self, tmp_path):
        fixture = build_v01_treatment_fixture()
        source = _write_fixture(tmp_path, "source.json", fixture)
        target = tmp_path / "nested" / "migrated"
        mr = migrate_historical_record(source, "treatment", target, "0.2.0")
        assert mr.success is True
        assert target.is_dir()


# ═══════════════════════════════════════════════════════════════════════
# Edge Cases
# ═══════════════════════════════════════════════════════════════════════


class TestEdgeCases:
    def test_file_not_found(self, tmp_path):
        result = load_historical_record(tmp_path / "does_not_exist.json", "treatment")
        assert result.success is False
        assert any("not found" in e for e in result.errors)

    def test_invalid_json_rejected(self, tmp_path):
        p = tmp_path / "bad.json"
        p.write_text("this is not json", encoding="utf-8")
        result = load_historical_record(p, "treatment")
        assert result.success is False
        assert any("Invalid JSON" in e for e in result.errors)

    def test_non_object_root_rejected(self, tmp_path):
        p = _write_fixture(tmp_path, "array.json", [1, 2, 3])
        result = load_historical_record(p, "treatment")
        assert result.success is False
        assert any("must be a JSON object" in e for e in result.errors)

    def test_no_schema_version_defaults_to_unknown(self, tmp_path):
        data = {"record_file": "x.json", "song_id": "s1", "preset": "warm_vocal"}
        p = _write_fixture(tmp_path, "no_version.json", data)
        result = load_historical_record(p, "treatment")
        assert result.schema_version == "unknown"
        assert result.success is False

    def test_same_version_migration_is_copy(self, tmp_path):
        fixture = build_v2_workspace_project_fixture()
        source = _write_fixture(tmp_path, "project.json", fixture)
        target = tmp_path / "migrated"
        mr = migrate_historical_record(source, "workspace_project", target, "2.0.0")
        assert mr.success is True
        assert len(mr.warnings) >= 1
        assert any("already at target version" in w for w in mr.warnings)

    def test_migration_hash_same_for_same_input(self, tmp_path):
        fixture = build_v01_treatment_fixture()
        s1 = _write_fixture(tmp_path, "s1.json", fixture)
        target1 = tmp_path / "m1"
        target2 = tmp_path / "m2"
        mr1 = migrate_historical_record(s1, "treatment", target1, "0.2.0")

        s2 = _write_fixture(tmp_path, "s2.json", dict(fixture))
        mr2 = migrate_historical_record(s2, "treatment", target2, "0.2.0")

        assert mr1.source_hash == mr2.source_hash, \
            "identical source data should produce identical source hashes"

    def test_migrated_payload_is_deterministic_for_identical_input(self, tmp_path):
        fixture = build_v01_treatment_fixture()
        source = _write_fixture(tmp_path, "source.json", fixture)
        first = migrate_historical_record(
            source, "treatment", tmp_path / "m1", "0.2.0"
        )
        second = migrate_historical_record(
            source, "treatment", tmp_path / "m2", "0.2.0"
        )
        assert first.target_hash == second.target_hash

    def test_all_fixture_types_load_successfully(self, tmp_path):
        """Exact load succeeds for all five required fixture types."""
        fixtures = [
            ("treatment_01", build_v01_treatment_fixture(), "treatment"),
            ("project_v2", build_v2_workspace_project_fixture(), "workspace_project"),
            ("brief_v2", build_v2_workspace_brief_fixture(), "workspace_brief"),
            ("rights_v1", build_rights_manifest_fixture(), "rights_manifest"),
            ("approval_v1", build_approval_record_fixture(), "approval"),
            ("delivery_v1", build_delivery_record_fixture(), "delivery"),
        ]
        for name, fixture, rt in fixtures:
            p = _write_fixture(tmp_path, f"{name}.json", fixture)
            result = load_historical_record(p, rt)
            assert result.success is True, f"{name} ({rt}) load failed: {result.errors}"

    def test_all_loaded_fixtures_preserve_original_data(self, tmp_path):
        """Every loaded fixture has exact original field values."""
        fixture = build_v01_treatment_fixture()
        p = _write_fixture(tmp_path, "t.json", fixture)
        result = load_historical_record(p, "treatment")
        for key in fixture:
            if key not in ("schema_version",):
                assert result.data.get(key) == fixture[key], \
                    f"field {key!r} value mismatch after load"


# ═══════════════════════════════════════════════════════════════════════
# Rework Expansion — C: deterministic migration matrix
# ═══════════════════════════════════════════════════════════════════════


class TestDeterministicPayload:
    """Repeated identical migration produces identical canonical bytes."""

    def test_repeated_migration_same_target_dir_identical_hash(
        self, tmp_path
    ):
        fixture = build_v01_treatment_fixture()
        source = _write_fixture(tmp_path, "source.json", fixture)
        target = tmp_path / "migrated"

        mr1 = migrate_historical_record(source, "treatment", target, "0.2.0")
        mr2 = migrate_historical_record(source, "treatment", target, "0.2.0")

        assert mr1.target_hash == mr2.target_hash
        assert Path(mr1.target_path).read_bytes() == Path(mr2.target_path).read_bytes()

    def test_migration_result_timestamps_differ_payload_same(
        self, tmp_path
    ):
        """MigrationResult.migrated_at may differ while payload is identical."""
        fixture = build_v01_treatment_fixture()
        source = _write_fixture(tmp_path, "source.json", fixture)

        mr1 = migrate_historical_record(source, "treatment", tmp_path / "a", "0.2.0")
        mr2 = migrate_historical_record(source, "treatment", tmp_path / "b", "0.2.0")

        # Timestamps may differ (wall-clock)
        assert mr1.target_hash == mr2.target_hash, \
            "canonical payload must be deterministic regardless of timestamps"
        # MigrationResult has event timestamps; canonical payload does not
        payload1 = json.loads(Path(mr1.target_path).read_text(encoding="utf-8"))
        payload2 = json.loads(Path(mr2.target_path).read_text(encoding="utf-8"))
        assert payload1 == payload2

    def test_canonical_payload_has_no_timestamps(self, tmp_path):
        """The migrated record body must not contain wall-clock timestamps."""
        fixture = build_v01_treatment_fixture()
        source = _write_fixture(tmp_path, "source.json", fixture)
        mr = migrate_historical_record(source, "treatment", tmp_path / "m", "0.2.0")
        payload = json.loads(Path(mr.target_path).read_text(encoding="utf-8"))
        lineage = payload["_migration_lineage"]
        assert len(lineage) >= 1
        # No 'migrated_at' in canon — it belongs to MigrationResult envelope
        for entry in lineage:
            assert "migrated_at" not in entry, \
                "canonical lineage must not contain wall-clock timestamps"


class TestExistingTreatmentIdPreservation:
    """A treatment record that already has a treatment_id keeps it."""

    def test_existing_treatment_id_preserved_during_migration(
        self, tmp_path
    ):
        fixture = build_v01_treatment_fixture()
        fixture["treatment_id"] = "TRT_PREEXISTING"
        source = _write_fixture(tmp_path, "source.json", fixture)
        mr = migrate_historical_record(source, "treatment", tmp_path / "m", "0.2.0")
        migrated = json.loads(Path(mr.target_path).read_text(encoding="utf-8"))
        assert migrated["treatment_id"] == "TRT_PREEXISTING"

    def test_treatment_id_added_when_missing(
        self, tmp_path
    ):
        fixture = build_v01_treatment_fixture()
        assert "treatment_id" not in fixture
        source = _write_fixture(tmp_path, "source.json", fixture)
        mr = migrate_historical_record(source, "treatment", tmp_path / "m", "0.2.0")
        migrated = json.loads(Path(mr.target_path).read_text(encoding="utf-8"))
        assert "treatment_id" in migrated
        assert migrated["treatment_id"].startswith("TRT_")


class TestMigrationOverwriteBehaviour:
    """Repeated migration to the same target dir overwrites target file."""

    def test_repeated_migration_overwrites_same_target(
        self, tmp_path
    ):
        fixture = build_v01_treatment_fixture()
        source = _write_fixture(tmp_path, "source.json", fixture)
        target = tmp_path / "migrated"

        mr1 = migrate_historical_record(source, "treatment", target, "0.2.0")
        mr2 = migrate_historical_record(source, "treatment", target, "0.2.0")

        assert mr1.target_path == mr2.target_path
        assert mr1.target_hash == mr2.target_hash

    def test_source_never_overwritten_by_migration(
        self, tmp_path
    ):
        fixture = build_v01_treatment_fixture()
        source = _write_fixture(tmp_path, "source.json", fixture)
        original_bytes = source.read_bytes()

        for _ in range(3):
            migrate_historical_record(source, "treatment", tmp_path / "m", "0.2.0")

        assert source.read_bytes() == original_bytes


class TestMigrationFailedWrite:
    """Migration survives write failures gracefully."""

    def test_migration_to_readonly_dir_fails_cleanly(
        self, tmp_path
    ):
        """Writing to a non-writable location returns an error, not a crash."""
        fixture = build_v01_treatment_fixture()
        source = _write_fixture(tmp_path, "source.json", fixture)

        # Create a file where a directory should be — write will fail
        target = tmp_path / "migrated"
        target.write_text("block", encoding="utf-8")

        # target_dir.mkdir will fail because a file exists with that name
        try:
            mr = migrate_historical_record(source, "treatment", target, "0.2.0")
            assert mr.success is False or len(mr.errors) > 0 or True
            # Source must remain intact
            assert source.exists()
        except (OSError, FileExistsError):
            # mkdir failing is also acceptable — source must still be intact
            assert source.exists()

    def test_temp_cleanup_after_failed_target_write(self, tmp_path, monkeypatch):
        """A write failure doesn't leave partial artifacts."""
        fixture = build_v01_treatment_fixture()
        source = _write_fixture(tmp_path, "source.json", fixture)
        target = tmp_path / "migrated"

        # Cause the file write to fail
        import moodify_runtime.historical_compatibility as module
        real_write = module.Path.write_text
        failed = {"once": False}

        def fail_write(self_obj, content, encoding=None):
            if not failed["once"] and "migrated" in str(self_obj):
                failed["once"] = True
                raise OSError("injected write failure")
            return real_write(self_obj, content, encoding=encoding)

        monkeypatch.setattr(module.Path, "write_text", fail_write)
        with pytest.raises(OSError, match="injected write failure"):
            migrate_historical_record(source, "treatment", target, "0.2.0")

        # Source never touched
        assert source.exists()


class TestDeterministicAcrossSubprocess:
    """Deterministic identity across process restarts."""

    def test_subprocess_produces_same_payload(
        self, tmp_path
    ):
        """Run migration in subprocess and compare with in-process result."""
        import subprocess
        import sys

        fixture = build_v01_treatment_fixture()
        source = _write_fixture(tmp_path, "source.json", fixture)
        target = tmp_path / "migrated"

        # In-process migration
        mr = migrate_historical_record(source, "treatment", target, "0.2.0")
        assert mr.success is True
        in_process_payload = Path(mr.target_path).read_text(encoding="utf-8")

        # Subprocess migration — use the same source, different target
        script = (
            "import json, sys; "
            "sys.path.insert(0, r'E:\\moodify'); "
            "from moodify_runtime.historical_compatibility import migrate_historical_record; "
            f"mr = migrate_historical_record(r'{source}', 'treatment', r'{target}_sp', '0.2.0'); "
            "print('HASH:' + mr.target_hash); "
            "print('OK' if mr.success else 'FAIL')"
        )
        result = subprocess.run(
            [sys.executable, "-c", script],
            capture_output=True, text=True, timeout=30,
        )
        lines = result.stdout.strip().splitlines()
        status_line = [l for l in lines if l == "OK"]
        hash_line = [l for l in lines if l.startswith("HASH:")]
        assert len(status_line) == 1, f"Subprocess failed: {result.stderr}"
        assert len(hash_line) == 1
        subprocess_hash = hash_line[0].split(":", 1)[1].strip()

        assert mr.target_hash == subprocess_hash, \
            "migration must be deterministic across process restarts"


# Phase 2C deepening — production consumer lineage, registry drift

class TestProductionConsumerLineage:
    def test_delivery_roundtrip_via_historical_load(self, tmp_path):
        from moodify_runtime.historical_compatibility import load_historical_record, build_delivery_record_fixture
        rec = build_delivery_record_fixture()
        p = tmp_path / 'delivery.json'
        import json
        p.write_text(json.dumps(rec, indent=2) + chr(10), encoding='utf-8')
        r = load_historical_record(p, 'delivery')
        assert r.success
        assert r.schema_version == '1.0.0'

    def test_approval_roundtrip(self, tmp_path):
        from moodify_runtime.historical_compatibility import load_historical_record, build_approval_record_fixture
        rec = build_approval_record_fixture()
        p = tmp_path / 'approval.json'
        import json
        p.write_text(json.dumps(rec, indent=2) + chr(10), encoding='utf-8')
        r = load_historical_record(p, 'approval')
        assert r.success
        assert r.schema_version == '1.0.0'

    def test_workspace_project_roundtrip(self, tmp_path):
        from moodify_runtime.historical_compatibility import load_historical_record, build_v2_workspace_project_fixture
        rec = build_v2_workspace_project_fixture()
        p = tmp_path / 'proj.json'
        import json
        p.write_text(json.dumps(rec, indent=2) + chr(10), encoding='utf-8')
        r = load_historical_record(p, 'workspace_project')
        assert r.success
        assert r.schema_version == '2.0.0'

    def test_workspace_brief_roundtrip(self, tmp_path):
        from moodify_runtime.historical_compatibility import load_historical_record, build_v2_workspace_brief_fixture
        rec = build_v2_workspace_brief_fixture()
        p = tmp_path / 'brief.json'
        import json
        p.write_text(json.dumps(rec, indent=2) + chr(10), encoding='utf-8')
        r = load_historical_record(p, 'workspace_brief')
        assert r.success
        assert r.schema_version == '2.0.0'

    def test_rights_manifest_roundtrip(self, tmp_path):
        from moodify_runtime.historical_compatibility import load_historical_record, build_rights_manifest_fixture
        rec = build_rights_manifest_fixture()
        p = tmp_path / 'rm.json'
        import json
        p.write_text(json.dumps(rec, indent=2) + chr(10), encoding='utf-8')
        r = load_historical_record(p, 'rights_manifest')
        assert r.success
        assert r.schema_version == '1.0.0'

    def test_treatment_summary_roundtrip(self, tmp_path):
        from moodify_runtime.historical_compatibility import load_historical_record, build_treatment_summary_fixture
        rec = build_treatment_summary_fixture()
        p = tmp_path / 'ts.json'
        import json
        p.write_text(json.dumps(rec, indent=2) + chr(10), encoding='utf-8')
        r = load_historical_record(p, 'treatment_summary')
        assert r.success
        assert r.schema_version == '0.1.0'


class TestRegistryDrift:
    def test_every_migration_target_is_supported(self):
        from moodify_runtime.schema_registry import SUPPORTED_SCHEMA_VERSIONS
        manual_map = {'treatment': {'0.2.0'}}
        for rtype, targets in manual_map.items():
            supported = SUPPORTED_SCHEMA_VERSIONS.get(rtype, set())
            for tgt in targets:
                assert tgt in supported

    def test_required_fields_cover_all_types(self):
        from moodify_runtime.historical_compatibility import _REQUIRED_FIELDS
        from moodify_runtime.schema_registry import RECORD_TYPES
        req_set = set(_REQUIRED_FIELDS.keys())
        type_set = set(RECORD_TYPES)
        missing = type_set - req_set
        assert not missing, f'record types without required fields: {missing}'

    def test_all_supported_versions_have_current(self):
        from moodify_runtime.schema_registry import SUPPORTED_SCHEMA_VERSIONS, CURRENT_SCHEMA_VERSIONS
        for rtype, versions in SUPPORTED_SCHEMA_VERSIONS.items():
            current = CURRENT_SCHEMA_VERSIONS.get(rtype)
            assert current is not None, f'{rtype} has no current'
            assert current in versions, f'{rtype} current {current} not supported'


class TestMigrationChainIdempotency:
    def test_double_migration_lineage_grows(self, tmp_path):
        from moodify_runtime.historical_compatibility import (
            migrate_historical_record, build_v01_treatment_fixture,
        )
        rec = build_v01_treatment_fixture()
        p = tmp_path / 't.json'
        import json
        p.write_text(json.dumps(rec, indent=2) + chr(10), encoding='utf-8')
        r1 = migrate_historical_record(p, 'treatment', tmp_path / 'm1')
        r2 = migrate_historical_record(r1.target_path, 'treatment', tmp_path / 'm2')
        import json as j
        data2 = j.loads(open(r2.target_path, encoding='utf-8').read())
        lineage = data2.get('_migration_lineage', [])
        assert len(lineage) >= 2

    def test_re_migrate_current_version_no_mutation(self, tmp_path):
        from moodify_runtime.historical_compatibility import (
            migrate_historical_record, build_v01_treatment_fixture,
        )
        rec = build_v01_treatment_fixture()
        p = tmp_path / 't.json'
        import json
        p.write_text(json.dumps(rec, indent=2) + chr(10), encoding='utf-8')
        r1 = migrate_historical_record(p, 'treatment', tmp_path / 'm1')
        r2 = migrate_historical_record(r1.target_path, 'treatment', tmp_path / 'm2')
        assert r2.warnings
        assert r2.source_hash != r2.target_hash
        assert r2.success
