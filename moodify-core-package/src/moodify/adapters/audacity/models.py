"""Data models for the Audacity macro runtime (DSK-MFY-AUDACITY-MACRO-RUNTIME-001)."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import datetime, timezone

MACRO_NAME_PATTERN = re.compile(r"^MFY_[A-Z0-9_]+_V\d{3}$")


@dataclass(frozen=True)
class MacroRegistration:
    """A macro registered in the running Audacity instance."""

    display_name: str  # e.g. MFY_REFINE_BALANCED_V001
    scripting_id: str  # e.g. Macro_MFY_REFINE_BALANCED_V001

    @staticmethod
    def is_valid_name(name: str) -> bool:
        return MACRO_NAME_PATTERN.match(name) is not None


@dataclass(frozen=True)
class AudacityCommandInfo:
    """One entry from GetInfo Type=Commands."""

    scripting_id: str
    display_name: str
    help_url: str = ""


@dataclass
class ExecutionRecord:
    """Full evidence record for one macro execution (mandated by the task spec)."""

    case_id: str
    source_path: str
    source_sha256: str
    macro_display_name: str
    macro_scripting_id: str
    macro_file_path: str
    macro_sha256: str
    audacity_version: str
    plugin_inventory: dict = field(default_factory=dict)
    started_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    completed_at: str = ""
    raw_command_log: list[str] = field(default_factory=list)
    raw_audacity_response: list[str] = field(default_factory=list)
    output_path: str = ""
    output_sha256: str = ""
    execution_status: str = "RUNNING"

    def finish(self, status: str) -> None:
        self.completed_at = datetime.now(timezone.utc).isoformat()
        self.execution_status = status
