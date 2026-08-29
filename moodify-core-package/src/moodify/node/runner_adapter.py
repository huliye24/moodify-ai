"""Adapter from node queue to the canonical Phase-I Data Factory."""

from __future__ import annotations

from pathlib import Path


def run_data_factory(source_path: Path, output_root: Path, scan_profile_id: str) -> Path:
    try:
        from moodify.data_factory.runner import run_production_case
    except ImportError as exc:
        raise RuntimeError(
            "MFY-DATA-FACTORY-001 is not integrated. Integrate the canonical data_factory package first; "
            "do not implement a second scanner inside moodify.node."
        ) from exc

    return run_production_case(
        Path(source_path),
        Path(output_root),
        scan_profile_id=scan_profile_id,
    )
