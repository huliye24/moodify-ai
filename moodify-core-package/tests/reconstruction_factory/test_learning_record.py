"""Learning record tests (MFY-CR-P07)."""

from __future__ import annotations

import pytest

from moodify.reconstruction_factory.learning_record import (
    RECORD_VERSION,
    build_learning_record,
)
from moodify.reconstruction_factory.rights import (
    RightsRecord,
    default_rights,
    validate_rights,
)

pytestmark = pytest.mark.v01

VERSIONS = {"diagnostic": "era-diag-v1", "objective": "obj-v1", "identity_guard": "ig-v1", "engine": "recon-v1"}


def test_record_deterministic_id():
    a = build_learning_record("T01", "hash_abc", default_rights(), {"era_hint": "1980s"}, VERSIONS)
    b = build_learning_record("T01", "hash_abc", default_rights(), {"era_hint": "1980s"}, VERSIONS)
    assert a.record_id == b.record_id
    assert a.record_id.startswith("rlr_")
    assert len(a.record_id) == 4 + 16


def test_record_version_and_versions_pinned():
    r = build_learning_record("T01", "hash_abc", default_rights(), {}, VERSIONS)
    assert r.record_version == RECORD_VERSION
    assert r.versions == VERSIONS
    assert "diagnostic" in r.versions


def test_rights_defaults_are_conservative():
    r = default_rights()
    assert r.processing_permission is True
    assert r.training_permission is False
    assert r.public_demo_permission is False
    ok, _ = validate_rights(r)
    assert ok


def test_internal_test_cannot_grant_training():
    bad = RightsRecord(
        rights_status="INTERNAL_TEST_ALLOWED",
        processing_permission=True,
        training_permission=True,
    )
    ok, reason = validate_rights(bad)
    assert not ok
    assert "cannot grant training" in reason


def test_owned_can_grant_training():
    owned = RightsRecord(
        rights_status="OWNED",
        processing_permission=True,
        training_permission=True,
    )
    ok, _ = validate_rights(owned)
    assert ok


def test_disallowed_rights_status_blocked():
    bad = RightsRecord(rights_status="SCRAPED", processing_permission=True)
    ok, _ = validate_rights(bad)
    assert not ok


def test_record_json_roundtrip():
    r = build_learning_record("T01", "hash_abc", default_rights(), {"duration_s": 210}, VERSIONS)
    d = r.to_dict()
    assert d["case_id"] == "T01"
    assert d["golden_status"] == "PENDING"
    assert d["record_version"] == RECORD_VERSION
