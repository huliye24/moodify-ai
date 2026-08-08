"""Macro registry — resolved from GetInfo, never guessed (DSK-MFY-AUDACITY-MACRO-RUNTIME-001)."""

from __future__ import annotations

from moodify.adapters.audacity.errors import AudacityMacroNotFound
from moodify.adapters.audacity.models import MacroRegistration

MACRO_PREFIX = "Macro_"


class MacroRegistry:
    """Snapshot of macros registered in the running Audacity instance."""

    def __init__(self, registrations: list[MacroRegistration]) -> None:
        self._by_name = {r.display_name: r for r in registrations}
        self._by_id = {r.scripting_id: r for r in registrations}

    @classmethod
    def from_commands(cls, command_infos) -> "MacroRegistry":
        regs: list[MacroRegistration] = []
        for info in command_infos:
            if not info.scripting_id.startswith(MACRO_PREFIX):
                continue
            display = info.display_name or info.scripting_id[len(MACRO_PREFIX):]
            regs.append(MacroRegistration(display_name=display, scripting_id=info.scripting_id))
        return cls(regs)

    def resolve(self, display_name: str) -> MacroRegistration:
        """Resolve a display name to its scripting id.

        Display names are matched exactly; scripting IDs are derived from the
        live registry only. Unknown macros fail as AUDACITY_MACRO_NOT_FOUND.
        """
        # accept either the display name or the full scripting id
        reg = self._by_name.get(display_name) or self._by_id.get(display_name)
        if reg is None:
            raise AudacityMacroNotFound(
                f"宏未注册：{display_name}。先用 list 查看可用宏，禁止猜测脚本 ID。"
            )
        return reg

    def list(self) -> list[MacroRegistration]:
        return sorted(self._by_name.values(), key=lambda r: r.display_name)

    def __contains__(self, display_name: str) -> bool:
        return display_name in self._by_name or display_name in self._by_id
