"""Export/handoff stubs for GUI DAWs — NOT core execution paths."""
from __future__ import annotations


class ReaperProjectExporter:
    """Exports CLIDAWProject as REAPER .rpp. Not a core execution path."""
    name = "reaper-exporter"
    status = "NOT_IMPLEMENTED"


class ArdourProjectExporter:
    name = "ardour-exporter"
    status = "NOT_IMPLEMENTED"


class AudacityMacroExporter:
    name = "audacity-exporter"
    status = "NOT_IMPLEMENTED"


class AuditionHumanHandoff:
    name = "audition-handoff"
    status = "HUMAN_HANDOFF"


EXPORTERS = {
    "reaper": ReaperProjectExporter,
    "ardour": ArdourProjectExporter,
    "audacity": AudacityMacroExporter,
    "audition": AuditionHumanHandoff,
}
