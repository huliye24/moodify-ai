"""Analysis and node cache identity authority."""

from __future__ import annotations

from dataclasses import asdict, dataclass

from moodify.auditory.identity import logical_id


@dataclass(frozen=True)
class AnalysisIdentity:
    source_sha256: str
    analysis_profile_id: str
    temporal_profile_id: str
    representation_version: str
    measurement_registry_version: str

    @property
    def logical_id(self) -> str:
        return logical_id("analysis", asdict(self), 24)

    def node_key(self, node_id: str, node_version: str,
                 parameters: dict | None = None,
                 dependency_hashes: dict[str, str] | None = None) -> str:
        return logical_id("node", {
            "analysis": asdict(self),
            "node_id": node_id,
            "node_version": node_version,
            "parameters": parameters or {},
            "dependency_hashes": dependency_hashes or {},
        }, 32)
