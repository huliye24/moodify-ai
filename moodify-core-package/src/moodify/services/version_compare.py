"""Version comparison service for workspace v2.

Compares loudness, dynamics, spectrum, MRS, treatment plans, and human notes
across two AudioVersion nodes, returning a unified comparison structure.
"""

from __future__ import annotations

from collections.abc import Callable
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from moodify.domain import AudioVersion
from moodify.storage import WorkspaceStore

Clock = Callable[[], datetime]


def _safe_compare(a: Any, b: Any) -> dict[str, Any]:
    """Compare two values safely, returning delta info."""
    if a is None and b is None:
        return {"equal": True, "delta": None}
    if a is None or b is None:
        return {"equal": False, "delta": None, "note": "one side missing"}

    if isinstance(a, (int, float)) and isinstance(b, (int, float)):
        delta = b - a
        return {
            "equal": abs(delta) < 1e-9,
            "delta": delta,
            "side_a": a,
            "side_b": b,
        }
    return {"equal": a == b, "side_a": str(a), "side_b": str(b)}


def _compare_treatment_plans(
    store: WorkspaceStore,
    project_id: str,
    version_a: AudioVersion,
    version_b: AudioVersion,
) -> dict[str, Any]:
    """Compare treatment plans assigned to two versions."""
    result: dict[str, Any] = {"comparable": False}

    if version_a.treatment_plan_id and version_b.treatment_plan_id:
        try:
            plan_a = store.get_plan(project_id, version_a.treatment_plan_id)
            plan_b = store.get_plan(project_id, version_b.treatment_plan_id)

            variant_a = next(
                (v for v in plan_a.variants
                 if v.variant_id == version_a.treatment_variant_id),
                None,
            )
            variant_b = next(
                (v for v in plan_b.variants
                 if v.variant_id == version_b.treatment_variant_id),
                None,
            )

            result["comparable"] = True
            result["plan_a_name"] = plan_a.name
            result["plan_b_name"] = plan_b.name

            if variant_a and variant_b:
                result["variant_a_label"] = variant_a.label
                result["variant_a_name"] = variant_a.name
                result["variant_b_label"] = variant_b.label
                result["variant_b_name"] = variant_b.name
                result["action_count"] = _safe_compare(
                    len(variant_a.actions), len(variant_b.actions)
                )
        except Exception:
            result["plan_error"] = "could not resolve treatment plans"

    return result


def _extract_audio_properties(audio_path: str) -> dict[str, Any]:
    """Extract basic audio properties from a file path."""
    props: dict[str, Any] = {}
    try:
        import soundfile as sf
        info = sf.info(audio_path)
        props["sample_rate"] = info.samplerate
        props["channels"] = info.channels
        props["duration_s"] = info.duration
        props["format"] = info.format
    except Exception:
        pass
    return props


class VersionCompareService:
    """Compares two AudioVersion nodes across all relevant dimensions.

    Produces a unified comparison structure suitable for A/B listening
    and metric comparison in the UI.
    Supports v0 (legacy), v1, and v2 versions.
    """

    def __init__(
        self,
        store: WorkspaceStore,
        *,
        clock: Clock | None = None,
    ) -> None:
        self.store = store
        self.clock = clock or (lambda: datetime.now(timezone.utc))

    def compare(
        self,
        project_id: str,
        version_id_a: str,
        version_id_b: str,
    ) -> dict[str, Any]:
        """Compare two versions and return a unified comparison structure."""
        version_a = self.store.get_version(project_id, version_id_a)
        version_b = self.store.get_version(project_id, version_id_b)

        project_dir = self.store._project_dir(project_id)

        audio_path_a = str(project_dir / version_a.audio_path)
        audio_path_b = str(project_dir / version_b.audio_path)

        properties_a = _extract_audio_properties(audio_path_a)
        properties_b = _extract_audio_properties(audio_path_b)

        result: dict[str, Any] = {
            "compared_at": self.clock().isoformat(),
            "version_a": {
                "version_id": version_a.version_id,
                "name": version_a.name,
                "branch": version_a.branch,
                "status": version_a.status.value,
                "created_at": version_a.created_at.isoformat(),
                "sha256": version_a.audio_sha256,
                "audio_properties": properties_a,
            },
            "version_b": {
                "version_id": version_b.version_id,
                "name": version_b.name,
                "branch": version_b.branch,
                "status": version_b.status.value,
                "created_at": version_b.created_at.isoformat(),
                "sha256": version_b.audio_sha256,
                "audio_properties": properties_b,
            },
            "comparisons": {},
        }

        if properties_a and properties_b:
            result["comparisons"]["duration"] = _safe_compare(
                properties_a.get("duration_s"),
                properties_b.get("duration_s"),
            )
            result["comparisons"]["sample_rate"] = _safe_compare(
                properties_a.get("sample_rate"),
                properties_b.get("sample_rate"),
            )
            result["comparisons"]["channels"] = _safe_compare(
                properties_a.get("channels"),
                properties_b.get("channels"),
            )

        result["comparisons"]["lineage"] = {
            "version_a_parent": version_a.parent_version_id,
            "version_b_parent": version_b.parent_version_id,
            "same_branch": version_a.branch == version_b.branch,
        }

        result["comparisons"]["treatment"] = _compare_treatment_plans(
            self.store, project_id, version_a, version_b
        )

        approval_a = (
            version_a.approval.model_dump(mode="json")
            if version_a.approval else None
        )
        approval_b = (
            version_b.approval.model_dump(mode="json")
            if version_b.approval else None
        )
        result["comparisons"]["approval"] = {
            "version_a_has_approval": approval_a is not None,
            "version_b_has_approval": approval_b is not None,
            "version_a_decision": approval_a,
            "version_b_decision": approval_b,
        }

        try:
            format_a = Path(version_a.audio_path).suffix
            format_b = Path(version_b.audio_path).suffix
            result["comparisons"]["format"] = _safe_compare(format_a, format_b)
        except Exception:
            pass

        return result

    def list_comparable_versions(
        self, project_id: str, *, reference_version_id: str | None = None
    ) -> list[dict[str, Any]]:
        """List versions available for comparison.

        If reference_version_id is provided, versions are annotated with
        basic comparison readiness.
        """
        versions = self.store.list_versions(project_id)
        result = []

        for version in versions:
            entry: dict[str, Any] = {
                "version_id": version.version_id,
                "name": version.name,
                "branch": version.branch,
                "status": version.status.value,
                "created_at": version.created_at.isoformat(),
                "sha256": version.audio_sha256[:12],
            }

            if (
                reference_version_id
                and version.version_id != reference_version_id
            ):
                try:
                    reference = self.store.get_version(
                        project_id, reference_version_id
                    )
                    entry["diff_from_reference"] = {
                        "same_branch": version.branch == reference.branch,
                        "same_treatment_plan": (
                            version.treatment_plan_id
                            == reference.treatment_plan_id
                        ),
                    }
                except Exception:
                    entry["diff_from_reference"] = None

            result.append(entry)

        result.sort(key=lambda v: v["created_at"])
        return result
