"""Tests for studio_session_prep.models — Pydantic v2 data models."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from tools.studio_session_prep.models import (
    AssetEntry,
    AssetKind,
    AssetRole,
    BackupTarget,
    DeliverableContract,
    RecordingSpec,
    SampleRate,
    SessionBrief,
    SessionManifest,
)


class TestSessionBrief:
    def test_minimal_creation(self):
        sb = SessionBrief(
            project_title="Test",
            client_name="Client",
            engineer_name="Engineer",
            studio_location="Studio",
            session_date="2026-08-01",
        )
        assert sb.project_title == "Test"
        assert sb.schema_version == "1.0.0"
        assert sb.session_id is not None

    def test_all_fields(self):
        sb = SessionBrief(
            project_title="Big Project",
            client_name="Client Co",
            engineer_name="Jane Engineer",
            studio_location="Room A",
            session_date="2026-08-01",
            genre="rock",
            target_bpm=140.0,
            target_key="E minor",
            notes="Important session.",
        )
        assert sb.genre == "rock"
        assert sb.target_bpm == 140.0
        assert sb.target_key == "E minor"

    def test_serialization_roundtrip(self):
        sb = SessionBrief(
            project_title="Test",
            client_name="Client",
            engineer_name="Engineer",
            studio_location="Studio",
            session_date="2026-08-01",
        )
        data = sb.model_dump(mode="json")
        assert data["schema_version"] == "1.0.0"
        assert data["tool_version"] == "0.1.0"
        # Re-parse
        sb2 = SessionBrief(**data)
        assert sb2.project_title == sb.project_title

    def test_created_at_is_utc_iso(self):
        sb = SessionBrief(
            project_title="T", client_name="C", engineer_name="E",
            studio_location="S", session_date="2026-08-01",
        )
        assert "T" in sb.created_at
        assert sb.created_at.endswith("Z") or "+" in sb.created_at


class TestRecordingSpec:
    def test_defaults(self):
        rs = RecordingSpec()
        assert rs.sample_rate == SampleRate.SR_48000
        assert rs.bit_depth.value == "24"
        assert rs.target_peak_dbfs == -6.0
        assert rs.channel_count == 2

    def test_custom(self):
        rs = RecordingSpec(
            sample_rate=SampleRate.SR_96000,
            bit_depth="32",
            target_peak_dbfs=-3.0,
        )
        assert rs.sample_rate == SampleRate.SR_96000
        assert rs.target_peak_dbfs == -3.0


class TestBackupTarget:
    def test_valid(self):
        bt = BackupTarget(label="ssd", path="D:/backup")
        assert bt.label == "ssd"

    def test_empty_path_rejected(self):
        with pytest.raises(ValueError):
            BackupTarget(label="bad", path="")


class TestDeliverableContract:
    def test_defaults(self):
        dc = DeliverableContract()
        assert dc.sample_rate_delivery == SampleRate.SR_48000
        assert dc.loudness_target_lufs is None
        assert dc.true_peak_limit_dbtp is None
        assert dc.include_wse_report is True


class TestAssetEntry:
    def test_unverified_by_default(self):
        ae = AssetEntry(role=AssetRole.SOURCE_STEM, kind=AssetKind.AUDIO, filename="test.wav")
        assert not ae.verified()
        assert ae.sha256 is None
        assert ae.sample_rate is None

    def test_verified_after_hash(self):
        ae = AssetEntry(role=AssetRole.SOURCE_STEM, kind=AssetKind.AUDIO, filename="test.wav")
        ae.sha256 = "a" * 64
        assert ae.verified()

    def test_not_verified_with_error(self):
        ae = AssetEntry(role=AssetRole.SOURCE_STEM, kind=AssetKind.AUDIO, filename="test.wav")
        ae.sha256 = "a" * 64
        ae.decode_error = "probe failed"
        assert not ae.verified()

    def test_to_summary(self):
        ae = AssetEntry(role=AssetRole.SOURCE_STEM, kind=AssetKind.AUDIO, filename="test.wav")
        ae.sha256 = "a" * 64
        ae.file_size_bytes = 1024
        summary = ae.to_summary()
        assert summary["role"] == "source_stem"
        assert summary["verified"] is True


class TestSessionManifest:
    def test_create(self):
        sb = SessionBrief(
            project_title="T", client_name="C", engineer_name="E",
            studio_location="S", session_date="2026-08-01",
        )
        manifest = SessionManifest(session_brief=sb, recording_spec=RecordingSpec())
        assert manifest.schema_version == "1.0.0"
        assert len(manifest.assets) == 0

    def test_add_asset(self):
        sb = SessionBrief(
            project_title="T", client_name="C", engineer_name="E",
            studio_location="S", session_date="2026-08-01",
        )
        manifest = SessionManifest(session_brief=sb, recording_spec=RecordingSpec())
        ae = AssetEntry(role=AssetRole.SOURCE_STEM, kind=AssetKind.AUDIO, filename="t.wav")
        manifest.add_asset(ae)
        assert len(manifest.assets) == 1

    def test_find_asset(self):
        sb = SessionBrief(
            project_title="T", client_name="C", engineer_name="E",
            studio_location="S", session_date="2026-08-01",
        )
        manifest = SessionManifest(session_brief=sb, recording_spec=RecordingSpec())
        ae = AssetEntry(role=AssetRole.SOURCE_STEM, kind=AssetKind.AUDIO, filename="find_me.wav")
        manifest.add_asset(ae)
        found = manifest.find_asset("find_me.wav")
        assert found is not None
        assert found.filename == "find_me.wav"
        assert manifest.find_asset("nope.wav") is None

    def test_serialization_roundtrip(self):
        sb = SessionBrief(
            project_title="T", client_name="C", engineer_name="E",
            studio_location="S", session_date="2026-08-01",
        )
        manifest = SessionManifest(
            session_brief=sb,
            recording_spec=RecordingSpec(),
            backup_targets=[BackupTarget(label="ssd", path="D:/b")],
        )
        ae = AssetEntry(role=AssetRole.SOURCE_STEM, kind=AssetKind.AUDIO, filename="t.wav")
        manifest.add_asset(ae)

        data = manifest.model_dump(mode="json")
        manifest2 = SessionManifest(**data)
        assert manifest2.manifest_id == manifest.manifest_id
        assert len(manifest2.assets) == 1
        assert len(manifest2.backup_targets) == 1
