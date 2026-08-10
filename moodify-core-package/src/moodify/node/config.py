"""Configuration for the low-resource Moodify production node."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class NodeConfig:
    state_dir: Path = Path("/var/lib/moodify")
    output_root: Path = Path("/var/lib/moodify/data_factory")
    poll_seconds: float = 10.0
    lease_seconds: int = 6 * 60 * 60
    min_available_memory_mb: int = 300
    min_free_disk_gb: float = 3.0
    scan_profile_id: str = "MFY-WSE-SCAN-PROFILE-001"

    @property
    def db_path(self) -> Path:
        return self.state_dir / "node.sqlite3"

    @classmethod
    def from_env(cls) -> "NodeConfig":
        return cls(
            state_dir=Path(os.getenv("MOODIFY_NODE_STATE_DIR", "/var/lib/moodify")),
            output_root=Path(os.getenv("MOODIFY_NODE_OUTPUT_ROOT", "/var/lib/moodify/data_factory")),
            poll_seconds=float(os.getenv("MOODIFY_NODE_POLL_SECONDS", "10")),
            lease_seconds=int(os.getenv("MOODIFY_NODE_LEASE_SECONDS", str(6 * 60 * 60))),
            min_available_memory_mb=int(os.getenv("MOODIFY_NODE_MIN_AVAILABLE_MB", "300")),
            min_free_disk_gb=float(os.getenv("MOODIFY_NODE_MIN_FREE_DISK_GB", "3")),
            scan_profile_id=os.getenv("MOODIFY_NODE_SCAN_PROFILE", "MFY-WSE-SCAN-PROFILE-001"),
        )
