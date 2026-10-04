"""Project Model 0.1 — Song Project foundation.

Covers the guarantees a project must hold: the source is copied without
modification, integrity is recorded and re-verified on reopen, persisted paths
cannot escape the project directory, and failure never leaves a misleading
project behind.
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pytest
import soundfile as sf
from pydantic import ValidationError

from moodify.contracts.hashing import sha256_file
from moodify.contracts.ids import ID_KINDS, new_id, validate_id
from moodify.project import (
    PROJECT_DIRECTORIES,
    PROJECT_PROTOCOL,
    RESERVED_SECTIONS,
    ProjectError,
    ProjectExistsError,
    ProjectIntegrityError,
    ProjectManifest,
    ProjectValidationError,
    create_project,
    load_project,
)
from moodify.project import service
from moodify.sound_protocol import AUDIO_EXTENSIONS


def _write_wav(path: Path, seconds: float = 1.0, sr: int = 44100) -> Path:
    t = np.arange(int(sr * seconds)) / sr
    audio = np.stack([0.3 * np.sin(2 * np.pi * 440 * t)] * 2, axis=1)
    sf.write(str(path), audio.astype(np.float32), sr)
    return path


@pytest.fixture
def source_wav(tmp_path: Path) -> Path:
    return _write_wav(tmp_path / "song.wav")


@pytest.fixture
def projects_root(tmp_path: Path) -> Path:
    return tmp_path / "projects"


@pytest.fixture
def project(source_wav: Path, projects_root: Path):
    manifest = create_project(source_wav, projects_root)
    return manifest, projects_root / manifest.project_id


# --- A. create project -------------------------------------------------------

def test_create_project_writes_manifest_and_skeleton(project):
    manifest, root = project
    assert (root / "project.json").is_file()
    assert (root / "source").is_dir()
    for name in PROJECT_DIRECTORIES:
        assert (root / name).is_dir(), f"missing directory: {name}"


def test_create_project_places_source_copy(project):
    manifest, root = project
    copy = root / manifest.source.logical_path
    assert copy.is_file()
    assert copy.parent.name == "source"
    assert manifest.source.logical_path == "source/original.wav"


def test_manifest_type_is_the_public_export(project):
    manifest, _ = project
    assert isinstance(manifest, ProjectManifest)


def test_create_project_records_protocol_and_empty_reserved_sections(project):
    manifest, _ = project
    assert manifest.protocol == PROJECT_PROTOCOL == "moodify.project/0.1"
    assert manifest.schema_version == "1.0"  # canonical contract schema, distinct
    for name in RESERVED_SECTIONS:
        assert getattr(manifest, name) == {}
    assert manifest.assets == {"source": manifest.source.asset_id}


def test_display_name_is_optional_and_recorded(source_wav, projects_root):
    manifest = create_project(source_wav, projects_root, display_name="Demo Song")
    assert manifest.display_name == "Demo Song"
    assert create_project(source_wav, projects_root).display_name is None


# --- B. source integrity -----------------------------------------------------

def test_source_is_copied_byte_for_byte(source_wav, project):
    manifest, root = project
    original_bytes = source_wav.read_bytes()
    assert original_bytes == (root / manifest.source.logical_path).read_bytes()


def test_manifest_hash_matches_original_and_copy(source_wav, project):
    manifest, root = project
    assert manifest.source.content_hash == sha256_file(source_wav)
    assert manifest.source.content_hash == sha256_file(root / manifest.source.logical_path)
    assert manifest.source.size_bytes == source_wav.stat().st_size


def test_user_source_is_left_untouched(source_wav, projects_root):
    before = source_wav.read_bytes()
    create_project(source_wav, projects_root)
    assert source_wav.is_file()
    assert source_wav.read_bytes() == before


# --- C. reopen ---------------------------------------------------------------

def test_freshly_created_project_reopens(project):
    manifest, root = project
    assert load_project(root) == manifest


def test_reopened_manifest_survives_canonical_round_trip(project):
    manifest, root = project
    reopened = load_project(root)
    assert json.loads((root / "project.json").read_text(encoding="utf-8")) == json.loads(
        reopened.model_dump_json()
    )


# --- D. IDs ------------------------------------------------------------------

def test_generated_ids_are_canonical(project):
    manifest, _ = project
    assert validate_id(manifest.project_id, "project") == manifest.project_id
    assert validate_id(manifest.source.asset_id, "asset") == manifest.source.asset_id


@pytest.mark.parametrize("kind", ["case", "meas", "evid", "rule", "finding"])
def test_pre_existing_id_kinds_still_validate(kind):
    assert kind in ID_KINDS
    value = new_id(kind)
    assert validate_id(value, kind) == value


def test_new_id_rejects_unknown_kind():
    with pytest.raises(ValueError):
        new_id("song")


# --- E. unsupported source ---------------------------------------------------

def test_unsupported_extension_is_rejected(tmp_path, projects_root):
    bad = tmp_path / "notes.txt"
    bad.write_text("not audio", encoding="utf-8")
    with pytest.raises(ProjectValidationError):
        create_project(bad, projects_root)


# --- F. missing source -------------------------------------------------------

def test_missing_source_is_rejected(tmp_path, projects_root):
    with pytest.raises(ProjectValidationError):
        create_project(tmp_path / "nope.wav", projects_root)


def test_directory_as_source_is_rejected(tmp_path, projects_root):
    folder = tmp_path / "album.wav"
    folder.mkdir()
    with pytest.raises(ProjectValidationError):
        create_project(folder, projects_root)


# --- G. traversal ------------------------------------------------------------

def test_manifest_with_traversing_logical_path_is_rejected(project):
    """A tampered manifest must not be able to point outside the project."""
    _, root = project
    payload = json.loads((root / "project.json").read_text(encoding="utf-8"))
    payload["source"]["logical_path"] = "../../outside.wav"
    (root / "project.json").write_text(json.dumps(payload), encoding="utf-8")

    with pytest.raises(ProjectValidationError):
        load_project(root)


@pytest.mark.parametrize(
    "logical_path",
    ["../outside.wav", "../../outside.wav", "source/../../outside.wav", "/etc/passwd"],
)
def test_resolved_containment_refuses_escape(tmp_path, logical_path):
    """Containment is decided on resolved paths, not string prefixes.

    Exercised directly because the manifest validator rejects ``..`` first —
    this is the second layer, and it must hold on its own.
    """
    root = tmp_path / "projects" / ("project_" + "a" * 32)
    root.mkdir(parents=True)
    with pytest.raises(ProjectValidationError):
        service._resolve_inside(root, logical_path)


def test_sibling_directory_with_shared_prefix_is_not_inside(tmp_path):
    """``project_x_evil`` must not be treated as living inside ``project_x``."""
    projects = tmp_path / "projects"
    inside = projects / ("project_" + "a" * 32)
    sibling = projects / ("project_" + "a" * 32 + "_evil")
    outside = sibling / "outside.wav"
    inside.mkdir(parents=True)
    sibling.mkdir(parents=True)
    outside.write_bytes(b"payload")

    assert service._resolve_inside(inside, "source/original.wav").is_relative_to(inside)
    with pytest.raises(ProjectValidationError):
        service._resolve_inside(inside, "../project_" + "a" * 32 + "_evil/outside.wav")


def test_backslash_logical_path_is_rejected(project):
    _, root = project
    payload = json.loads((root / "project.json").read_text(encoding="utf-8"))
    payload["source"]["logical_path"] = "source\\original.wav"
    (root / "project.json").write_text(json.dumps(payload), encoding="utf-8")
    with pytest.raises(ProjectValidationError):
        load_project(root)


# --- H. tampered audio -------------------------------------------------------

def test_modified_project_source_fails_integrity(project):
    manifest, root = project
    copy = root / manifest.source.logical_path
    copy.write_bytes(copy.read_bytes() + b"\x00" * 32)

    with pytest.raises(ProjectIntegrityError):
        load_project(root)


def test_truncated_project_source_fails_integrity(project):
    manifest, root = project
    copy = root / manifest.source.logical_path
    copy.write_bytes(copy.read_bytes()[:128])

    with pytest.raises(ProjectIntegrityError):
        load_project(root)


def test_deleted_project_source_fails_loudly(project):
    manifest, root = project
    (root / manifest.source.logical_path).unlink()

    with pytest.raises(ProjectIntegrityError):
        load_project(root)


def test_reopen_never_silently_updates_the_recorded_hash(project):
    manifest, root = project
    copy = root / manifest.source.logical_path
    copy.write_bytes(b"different audio entirely")
    with pytest.raises(ProjectIntegrityError):
        load_project(root)

    recorded = json.loads((root / "project.json").read_text(encoding="utf-8"))
    assert recorded["source"]["content_hash"] == manifest.source.content_hash


# --- I. tampered manifest hash ----------------------------------------------

def test_wrong_content_hash_in_manifest_fails_integrity(project):
    _, root = project
    payload = json.loads((root / "project.json").read_text(encoding="utf-8"))
    payload["source"]["content_hash"] = "sha256:" + "b" * 64  # well-formed, wrong
    (root / "project.json").write_text(json.dumps(payload), encoding="utf-8")

    with pytest.raises(ProjectIntegrityError):
        load_project(root)


def test_malformed_content_hash_is_rejected(project):
    _, root = project
    payload = json.loads((root / "project.json").read_text(encoding="utf-8"))
    payload["source"]["content_hash"] = "sha256:NOTHEX"
    (root / "project.json").write_text(json.dumps(payload), encoding="utf-8")

    with pytest.raises(ProjectValidationError):
        load_project(root)


def test_wrong_protocol_is_rejected(project):
    _, root = project
    payload = json.loads((root / "project.json").read_text(encoding="utf-8"))
    payload["protocol"] = "moodify.project/0.2"
    (root / "project.json").write_text(json.dumps(payload), encoding="utf-8")

    with pytest.raises(ProjectValidationError):
        load_project(root)


def test_missing_manifest_is_rejected(tmp_path):
    with pytest.raises(ProjectValidationError):
        load_project(tmp_path / "not-a-project")


# --- J. extra fields ---------------------------------------------------------

def test_manifest_rejects_extra_fields(project):
    _, root = project
    payload = json.loads((root / "project.json").read_text(encoding="utf-8"))
    payload["extra_domain"] = {}
    (root / "project.json").write_text(json.dumps(payload), encoding="utf-8")

    with pytest.raises(ProjectValidationError):
        load_project(root)


def test_asset_rejects_extra_fields(project):
    _, root = project
    payload = json.loads((root / "project.json").read_text(encoding="utf-8"))
    payload["source"]["surprise"] = 1
    (root / "project.json").write_text(json.dumps(payload), encoding="utf-8")

    with pytest.raises(ProjectValidationError):
        load_project(root)


def test_manifest_cannot_be_mutated_in_place(project):
    manifest, _ = project
    with pytest.raises(ValidationError):
        manifest.project_id = new_id("project")
    with pytest.raises(TypeError):
        manifest.assets["source"] = new_id("asset")


# --- failure behaviour -------------------------------------------------------

def test_existing_project_directory_is_never_overwritten(tmp_path, source_wav, projects_root, monkeypatch):
    fixed = "project_" + "0" * 32
    monkeypatch.setattr(service, "new_id", lambda kind: f"{kind}_" + "0" * 32)

    create_project(source_wav, projects_root)
    marker = projects_root / fixed / "keep.txt"
    marker.write_text("do not delete", encoding="utf-8")

    with pytest.raises(ProjectExistsError):
        create_project(source_wav, projects_root)

    assert marker.read_text(encoding="utf-8") == "do not delete"


def test_failed_creation_leaves_no_project_behind(tmp_path, source_wav, projects_root, monkeypatch):
    def boom(*args, **kwargs):
        raise OSError("simulated copy failure")

    monkeypatch.setattr(service.shutil, "copyfile", boom)

    with pytest.raises(ProjectError):
        create_project(source_wav, projects_root)

    assert list(projects_root.iterdir()) == []


def test_failure_while_building_skeleton_leaves_no_project_behind(
    tmp_path, source_wav, projects_root, monkeypatch
):
    """A half-built skeleton is still a half-written project."""

    def boom(root):
        (root / "analysis").mkdir()
        raise OSError("simulated skeleton failure")

    monkeypatch.setattr(service, "_create_skeleton", boom)

    with pytest.raises(ProjectError):
        create_project(source_wav, projects_root)

    assert list(projects_root.iterdir()) == []


# --- media type registry -----------------------------------------------------

def test_media_types_cover_every_supported_extension():
    assert set(service._MEDIA_TYPES) == AUDIO_EXTENSIONS


def test_each_supported_extension_creates_a_project(tmp_path, projects_root):
    for suffix in sorted(AUDIO_EXTENSIONS):
        src = tmp_path / f"clip{suffix}"
        src.write_bytes(b"payload-" + suffix.encode())
        manifest = create_project(src, projects_root)
        assert manifest.source.logical_path == f"source/original{suffix}"
        assert manifest.source.size_bytes == src.stat().st_size
