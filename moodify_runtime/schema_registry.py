"""Authoritative schema version declarations for Moodify record types.

Every supported schema version is declared in exactly one place. Compatibility
claims must reference this registry, not scattered string literals.

Part of DSK-MFY-AUX-HARDENING-002 Batch C.
"""

from __future__ import annotations

# ── Record types ─────────────────────────────────────────────────────
RECORD_TYPES = (
    "treatment",
    "treatment_summary",
    "workspace_project",
    "workspace_brief",
    "rights_manifest",
    "approval",
    "delivery",
    "craft_record",
    "proposal",
)

# ── Supported schema versions per record type ────────────────────────
SUPPORTED_SCHEMA_VERSIONS: dict[str, set[str]] = {
    "treatment": {"0.1.0", "0.2.0"},
    "treatment_summary": {"0.1.0"},
    "workspace_project": {"2.0.0"},
    "workspace_brief": {"2.0.0"},
    "rights_manifest": {"1.0.0"},
    "approval": {"1.0.0"},
    "delivery": {"1.0.0"},
    "craft_record": {"1.0.0"},
    "proposal": {"1.0.0"},
}

# ── Current (latest) version per record type ─────────────────────────
CURRENT_SCHEMA_VERSIONS: dict[str, str] = {
    "treatment": "0.2.0",
    "treatment_summary": "0.1.0",
    "workspace_project": "2.0.0",
    "workspace_brief": "2.0.0",
    "rights_manifest": "1.0.0",
    "approval": "1.0.0",
    "delivery": "1.0.0",
    "craft_record": "1.0.0",
    "proposal": "1.0.0",
}


def is_supported(record_type: str, schema_version: str) -> bool:
    """Return True if *schema_version* is a supported version for *record_type*."""
    supported = SUPPORTED_SCHEMA_VERSIONS.get(record_type, set())
    return schema_version in supported


def current_version(record_type: str) -> str | None:
    """Return the current (latest) schema version for *record_type*."""
    return CURRENT_SCHEMA_VERSIONS.get(record_type)


def validate_record_type(record_type: str) -> None:
    """Raise ValueError if *record_type* is not a known record type."""
    if record_type not in RECORD_TYPES:
        raise ValueError(
            f"Unknown record type {record_type!r}. Known: {sorted(RECORD_TYPES)}"
        )
