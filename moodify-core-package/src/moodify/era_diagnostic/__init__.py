"""Era Diagnostic v0.1 (MFY-CR-P03).

A diagnostic layer that answers, for a recording's measurable evidence:

    which observed phenomena *may* come from historical recording, transfer,
    medium or production-chain technical limitations?

It never authorizes processing. Findings use the four-state vocabulary of the
Classic Reconstruction Constitution (PRESERVE / RECONSTRUCT / BYPASS /
HUMAN_REQUIRED) only indirectly: a diagnostic is OBSERVED / POSSIBLE /
ARTISTIC / INSUFFICIENT / NOT_APPLICABLE and carries explicit confidence.
"""

from __future__ import annotations

from moodify.era_diagnostic.contract import (
    ConfidenceLevel,
    EraDiagnosticFinding,
    FindingStatus,
    category_name,
)
from moodify.era_diagnostic.engine import DETECTOR_INPUTS, run_era_diagnostic
from moodify.era_diagnostic.report import build_markdown_report, build_report_dict
from moodify.era_diagnostic.thresholds import ERA_DIAGNOSTIC_POLICY_V1

__all__ = [
    "ConfidenceLevel",
    "EraDiagnosticFinding",
    "FindingStatus",
    "ERA_DIAGNOSTIC_POLICY_V1",
    "DETECTOR_INPUTS",
    "category_name",
    "run_era_diagnostic",
    "build_report_dict",
    "build_markdown_report",
]

ERA_DIAGNOSTIC_VERSION = "era-diagnostic-v0.1"
