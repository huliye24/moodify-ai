"""Audacity macro runtime — Audacity is the craft executor, Moodify is the brain.

DSK-MFY-AUDACITY-MACRO-RUNTIME-001:
  Moodify analyzes/decides/approves/verifies; Audacity executes fixed macros
  through the mod-script-pipe named-pipe interface (never CLI flags).
"""

from moodify.adapters.audacity.client import AudacityClient
from moodify.adapters.audacity.errors import (
    AudacityCommandFailed,
    AudacityError,
    AudacityMacroNotFound,
    AudacityNotRunning,
    AudacityOutputMissing,
    AudacityPipeUnavailable,
)
from moodify.adapters.audacity.macro_registry import MacroRegistry
from moodify.adapters.audacity.runtime import AudacityMacroRuntime

__all__ = [
    "AudacityClient",
    "AudacityMacroRuntime",
    "MacroRegistry",
    "AudacityError",
    "AudacityCommandFailed",
    "AudacityMacroNotFound",
    "AudacityNotRunning",
    "AudacityOutputMissing",
    "AudacityPipeUnavailable",
]
