"""v01_delivery.py — MAP v0.2 Delivery Manifest & Reproducibility (MHP-875/876).

Generates:
  - manifest.json: artifact inventory with paths, sizes, SHA256 hashes
  - metadata.json: reproducibility metadata (git, python, packages, platform)
  - environment.txt: pip-freeze-style dependency listing
  - validation_report.json: standalone QualityGate extract
  - MAP_CHAIN_VERSION: version identifier file
"""

from __future__ import annotations

import hashlib
import json
import os
import platform
import subprocess
import sys
from pathlib import Path
from typing import Any


MAP_CHAIN_VERSION = "0.2.0"
MAP_CHAIN_VERSION_FILENAME = "MAP_CHAIN_VERSION"


def _sha256_hex(file_path: str) -> str:
    """Compute SHA-256 hex digest of a file."""
    h = hashlib.sha256()
    try:
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(65536), b""):
                h.update(chunk)
    except Exception:
        return ""
    return h.hexdigest()


def _file_size(file_path: str) -> int:
    try:
        return os.path.getsize(file_path)
    except Exception:
        return 0


def write_delivery_manifest(
    output_dir: str,
    run_id: str,
    artifacts: list[dict[str, Any]],
    pipeline_info: dict[str, Any],
) -> str:
    """Write manifest.json — artifact inventory with hashes (MHP-875).

    Args:
        output_dir: Delivery directory.
        run_id: Unique run identifier.
        artifacts: List of artifact dicts with keys:
            path, role, format, sample_rate, channels, duration_s.
        pipeline_info: Dict with version, stages, preset, elapsed_s.

    Returns:
        Absolute path to manifest.json.
    """
    manifest_path = os.path.join(output_dir, "manifest.json")
    manifest_dir = os.path.dirname(manifest_path)
    if manifest_dir:
        os.makedirs(manifest_dir, exist_ok=True)

    artifact_entries = []
    for art in artifacts:
        art_path = art.get("path", "")
        entry = {
            "path": os.path.basename(art_path) if art_path else "",
            "role": art.get("role", ""),
            "size_bytes": _file_size(art_path) if art_path else 0,
            "sha256": _sha256_hex(art_path) if art_path else "",
        }
        for opt in ("format", "sample_rate", "channels", "duration_s"):
            if opt in art:
                entry[opt] = art[opt]
        artifact_entries.append(entry)

    manifest = {
        "map_chain_version": MAP_CHAIN_VERSION,
        "run_id": run_id,
        "generated_at": _utc_now_iso(),
        "artifacts": artifact_entries,
        "pipeline": {
            "version": pipeline_info.get("version", "0.1.0"),
            "stages": pipeline_info.get("stages", []),
            "preset": pipeline_info.get("preset", ""),
            "elapsed_s": pipeline_info.get("elapsed_s", 0),
        },
    }

    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)

    return os.path.abspath(manifest_path)


# -- MHP-876: Reproducibility Metadata ----------------------------------------


def _git_hash() -> str:
    try:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            capture_output=True, text=True, timeout=5,
        )
        if result.returncode == 0:
            return result.stdout.strip()
    except Exception:
        pass
    return ""


def _git_branch() -> str:
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            capture_output=True, text=True, timeout=5,
        )
        if result.returncode == 0:
            return result.stdout.strip()
    except Exception:
        pass
    return ""


def _installed_packages() -> dict[str, str]:
    """Collect versions of key audio/scientific packages."""
    key_packages = [
        "numpy", "scipy", "pedalboard", "matplotlib", "soundfile",
        "librosa", "jsonschema",
    ]
    versions: dict[str, str] = {}
    for pkg in key_packages:
        try:
            mod = __import__(pkg)
            versions[pkg] = getattr(mod, "__version__", "unknown")
        except ImportError:
            pass
    return versions


def write_metadata(
    output_dir: str,
    run_id: str,
    input_path: str = "",
) -> tuple[str, str]:
    """Write metadata.json and environment.txt (MHP-876).

    Returns:
        (metadata_path, environment_path) absolute paths.
    """
    os.makedirs(output_dir, exist_ok=True)

    packages = _installed_packages()

    metadata = {
        "run_id": run_id,
        "map_chain_version": MAP_CHAIN_VERSION,
        "generated_at": _utc_now_iso(),
        "git_hash": _git_hash(),
        "git_branch": _git_branch(),
        "python_version": sys.version.split()[0],
        "platform": platform.platform(),
        "hostname": platform.node(),
        "packages": packages,
    }
    if input_path:
        metadata["input_sha256"] = _sha256_hex(input_path)

    metadata_path = os.path.join(output_dir, "metadata.json")
    with open(metadata_path, "w", encoding="utf-8") as f:
        json.dump(metadata, f, ensure_ascii=False, indent=2)

    # environment.txt
    env_lines = [
        f"python=={sys.version.split()[0]}",
        f"platform=={platform.platform()}",
    ]
    for pkg, ver in sorted(packages.items()):
        env_lines.append(f"{pkg}=={ver}")
    env_path = os.path.join(output_dir, "environment.txt")
    with open(env_path, "w", encoding="utf-8") as f:
        f.write("\n".join(env_lines) + "\n")

    return os.path.abspath(metadata_path), os.path.abspath(env_path)


def write_validation_report(
    output_dir: str,
    quality_gate: dict[str, Any],
) -> str:
    """Write standalone validation_report.json (MHP-877)."""
    report_path = os.path.join(output_dir, "validation_report.json")
    os.makedirs(output_dir, exist_ok=True)
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(quality_gate, f, ensure_ascii=False, indent=2)
    return os.path.abspath(report_path)


def write_version_file(output_dir: str) -> str:
    """Write MAP_CHAIN_VERSION file."""
    version_path = os.path.join(output_dir, MAP_CHAIN_VERSION_FILENAME)
    os.makedirs(output_dir, exist_ok=True)
    with open(version_path, "w", encoding="utf-8") as f:
        f.write(f"map_chain_v{MAP_CHAIN_VERSION}\n")
    return os.path.abspath(version_path)


def _utc_now_iso() -> str:
    from datetime import datetime, timezone
    return datetime.now(timezone.utc).isoformat()
