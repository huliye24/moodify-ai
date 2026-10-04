"""Create and reopen a Song Project (Project Model 0.1).

Non-destructive by construction: the user's source file is only ever read. The
project keeps its own copy under ``source/`` and records the digest of that
copy, so a project can be re-verified long after the original moved away.
"""

from __future__ import annotations

import shutil
from pathlib import Path

from pydantic import ValidationError

from ..contracts.base import utc_now
from ..contracts.hashing import sha256_file
from ..contracts.ids import new_id, validate_id
from ..contracts.serialization import from_canonical_json, to_canonical_json
from ..sound_protocol import AUDIO_EXTENSIONS
from .errors import (
    ProjectError,
    ProjectExistsError,
    ProjectIntegrityError,
    ProjectValidationError,
)
from .models import AssetKind, ProjectAsset, ProjectManifest

MANIFEST_NAME = "project.json"
SOURCE_DIR = "source"

#: Directory skeleton created for every project. The reserved directories
#: anticipate capabilities that Project Model 0.1 does not implement.
PROJECT_DIRECTORIES = (
    "stems",
    "analysis",
    "transcription",
    "score",
    "edits",
    "session",
    "renders",
    "verification",
    "exports",
    "provenance",
)

#: Media type recorded for each supported source extension. Keys mirror
#: :data:`moodify.sound_protocol.AUDIO_EXTENSIONS`; a test asserts they agree.
_MEDIA_TYPES = {
    ".wav": "audio/wav",
    ".flac": "audio/flac",
    ".mp3": "audio/mpeg",
    ".aiff": "audio/aiff",
    ".aif": "audio/aiff",
    ".m4a": "audio/mp4",
}


def project_root(projects_root: Path, project_id: str) -> Path:
    """Return the canonical directory for *project_id* under *projects_root*."""
    validate_id(project_id, "project")
    return Path(projects_root) / project_id


def create_project(
    source: Path,
    projects_root: Path,
    *,
    display_name: str | None = None,
) -> ProjectManifest:
    """Create a new project around *source*; the source file is never modified.

    Raises :class:`ProjectExistsError` rather than touching an existing
    directory, and leaves no half-written project behind on failure.
    """
    source_path = _validated_source(source)
    project_id = new_id("project")
    asset_id = new_id("asset")
    root = project_root(Path(projects_root), project_id)

    # Claiming the directory is the only step that may not be undone; from here
    # on a failure means the directory we created is removed again.
    _claim_project_dir(root)

    try:
        _create_skeleton(root)

        suffix = source_path.suffix.lower()
        logical_path = f"{SOURCE_DIR}/original{suffix}"
        destination = _resolve_inside(root, logical_path)

        shutil.copyfile(source_path, destination)

        # Hash both sides: the copy must be byte-identical to the original.
        source_digest = sha256_file(source_path)
        copy_digest = sha256_file(destination)
        if source_digest != copy_digest:
            raise ProjectIntegrityError(
                "copied source digest does not match the original source"
            )

        created_at = utc_now()
        asset = ProjectAsset(
            asset_id=asset_id,
            kind=AssetKind.SOURCE,
            logical_path=logical_path,
            original_name=source_path.name,
            media_type=_media_type(suffix),
            content_hash=copy_digest,
            size_bytes=destination.stat().st_size,
            created_at=created_at,
        )
        manifest = ProjectManifest(
            project_id=project_id,
            display_name=display_name,
            source=asset,
            assets={"source": asset_id},
            created_at=created_at,
        )
        (root / MANIFEST_NAME).write_text(
            to_canonical_json(manifest) + "\n", encoding="utf-8"
        )
        return manifest
    except ProjectError:
        _discard(root)
        raise
    except OSError as exc:
        _discard(root)
        raise ProjectError(f"failed to create project: {exc}") from exc


def load_project(project_root: Path) -> ProjectManifest:
    """Reopen a project and verify it still matches what it recorded.

    Verification failure is loud: a project is evidence-bearing state, so a
    changed source is an error, never a silent re-hash.
    """
    root = Path(project_root)
    manifest_path = root / MANIFEST_NAME
    if not manifest_path.is_file():
        raise ProjectValidationError(f"no {MANIFEST_NAME} under {root}")

    try:
        manifest = from_canonical_json(
            ProjectManifest, manifest_path.read_text(encoding="utf-8")
        )
    except ValidationError as exc:
        raise ProjectValidationError(f"invalid project manifest: {exc}") from exc

    _verify_source(root, manifest.source)
    return manifest


def _validated_source(source: Path) -> Path:
    """Resolve *source* and reject anything that is not a supported audio file."""
    candidate = Path(source)
    try:
        resolved = candidate.resolve(strict=True)
    except OSError as exc:
        raise ProjectValidationError(f"source does not exist: {candidate}") from exc
    if not resolved.is_file():
        raise ProjectValidationError(f"source is not a file: {candidate}")
    suffix = resolved.suffix.lower()
    if suffix not in AUDIO_EXTENSIONS:
        raise ProjectValidationError(f"unsupported audio extension: {suffix or candidate.name!r}")
    return resolved


def _media_type(suffix: str) -> str:
    media_type = _MEDIA_TYPES.get(suffix)
    if media_type is None:
        raise ProjectValidationError(f"no media type registered for extension: {suffix!r}")
    return media_type


def _is_within(base: Path, candidate: Path) -> bool:
    """True when *candidate* is *base* or lives beneath it (both resolved)."""
    try:
        candidate.relative_to(base)
    except ValueError:
        return False
    return True


def _resolve_inside(root: Path, logical_path: str) -> Path:
    """Resolve a project-relative logical path, refusing anything outside *root*.

    Persisted logical paths are untrusted input, so containment is decided on
    resolved paths rather than on string prefixes.
    """
    if not logical_path or logical_path.startswith(("/", "\\")):
        raise ProjectValidationError(f"logical path must be project-relative: {logical_path!r}")
    if Path(logical_path).is_absolute():
        raise ProjectValidationError(f"logical path must be project-relative: {logical_path!r}")

    base = Path(root).resolve()
    candidate = (base / logical_path).resolve()
    if not _is_within(base, candidate):
        raise ProjectValidationError(f"logical path escapes the project root: {logical_path!r}")
    return candidate


def _claim_project_dir(root: Path) -> None:
    """Create the project directory itself, never overwriting an existing one."""
    try:
        root.mkdir(parents=True, exist_ok=False)
    except FileExistsError as exc:
        raise ProjectExistsError(f"project already exists: {root}") from exc


def _create_skeleton(root: Path) -> None:
    """Create the standard subdirectories inside a freshly claimed project."""
    for name in (SOURCE_DIR, *PROJECT_DIRECTORIES):
        (root / name).mkdir()


def _verify_source(root: Path, asset: ProjectAsset) -> None:
    path = _resolve_inside(root, asset.logical_path)
    if not path.exists():
        raise ProjectIntegrityError(f"project source is missing: {asset.logical_path}")
    if not path.is_file():
        raise ProjectIntegrityError(f"project source is not a file: {asset.logical_path}")

    actual_size = path.stat().st_size
    if actual_size != asset.size_bytes:
        raise ProjectIntegrityError(
            f"project source size changed: recorded {asset.size_bytes}, found {actual_size}"
        )

    actual_hash = sha256_file(path)
    if actual_hash != asset.content_hash:
        raise ProjectIntegrityError(
            f"project source digest changed: recorded {asset.content_hash}, found {actual_hash}"
        )


def _discard(root: Path) -> None:
    """Remove a project directory this call created. Never the user's input."""
    shutil.rmtree(root, ignore_errors=True)
