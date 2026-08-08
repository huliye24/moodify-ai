"""Audacity macro runtime error taxonomy (DSK-MFY-AUDACITY-MACRO-RUNTIME-001)."""

from __future__ import annotations


class AudacityError(Exception):
    """Base class for all Audacity bridge errors."""


class AudacityNotRunning(AudacityError):
    """Audacity process is not running and could not be started."""


class AudacityPipeUnavailable(AudacityError):
    """mod-script-pipe named pipes are not available.

    Check that Audacity is running with mod-script-pipe enabled
    (Edit -> Preferences -> Modules) and was restarted after enabling.
    """


class AudacityCommandFailed(AudacityError):
    """Audacity returned BatchCommand finished: Failed!."""

    def __init__(self, command: str, response: str) -> None:
        self.command = command
        self.response = response
        super().__init__(f"Audacity command failed: {command} -> {response[:200]}")


class AudacityMacroNotFound(AudacityError):
    """Requested macro is not registered in the running Audacity instance.

    Moodify never guesses macro scripting IDs from display names; the
    registry must be resolved via GetInfo before execution.
    """


class AudacityMacroNameInvalid(AudacityError):
    """Macro display name violates MFY_<PROCESS>_<VARIANT>_V<NNN>."""


class AudacityOutputMissing(AudacityError):
    """Export2 reported success but the output file does not exist."""
