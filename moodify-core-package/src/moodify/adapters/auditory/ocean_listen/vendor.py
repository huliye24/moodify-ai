from __future__ import annotations

from pathlib import Path
from typing import Iterable
import json
import shutil

from .errors import LicenseError
from .provenance import capture_module_manifest, git_head

DEFAULT_VENDOR_ALLOWLIST = (
    "ocean.py",
    "modules/__init__.py",
    "modules/classifier.py",
    "modules/dynamics.py",
    "modules/harmonic_filter.py",
    "modules/instruments.py",
    "modules/lyrics_netease.py",
    "modules/lyrics_sensevoice.py",
    "modules/lyrics_whisper.py",
    "modules/notes.py",
    "modules/per_stem_notes.py",
    "modules/report.py",
    "modules/stems.py",
    "modules/structure.py",
    "modules/visualize.py",
    "modules/voice.py",
    "requirements.txt",
    "requirements-deep.txt",
    "LICENSE",
    "NOTICES",
    "README.md",
)


def vendor_snapshot(
    ocean_root: str | Path,
    destination: str | Path,
    *,
    allowlist: Iterable[str] = DEFAULT_VENDOR_ALLOWLIST,
) -> dict:
    source = Path(ocean_root)
    target = Path(destination)

    for required in ("LICENSE", "NOTICES"):
        if not (source / required).is_file():
            raise LicenseError(f"Required upstream file missing: {source / required}")

    if target.exists() and any(target.iterdir()):
        raise FileExistsError(
            f"Vendor destination is not empty: {target}. "
            "Use a new versioned directory."
        )
    target.mkdir(parents=True, exist_ok=True)

    copied: list[str] = []
    for relative in allowlist:
        src = source / relative
        if not src.is_file():
            continue
        dst = target / relative
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
        copied.append(relative)

    manifest = capture_module_manifest(target, copied)
    manifest.update(
        {
            "source_repository": "ennisaaaaaaaa-stack/ocean-listen",
            "source_commit": git_head(source),
            "vendor_policy": "immutable snapshot; modify through Moodify adapter layer",
            "copied_paths": copied,
        }
    )
    manifest_path = target / "MOODIFY_VENDOR_MANIFEST.json"
    manifest_path.write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    return manifest
