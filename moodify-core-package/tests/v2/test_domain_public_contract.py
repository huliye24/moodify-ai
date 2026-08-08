"""Public API contract tests for moodify.domain (DSK-MFY-ORDER-BEAUTY-022).

Guarantees the domain re-export table stays stable: every documented symbol
must resolve from the package root, and duplicate-name drift must not
recur. This test is the regression net for the collection-error family 1
(domain export drift).
"""

from __future__ import annotations

import importlib

import moodify.domain as domain

# The public contract restored from Workspace v2 (git HEAD __init__.py)
PUBLIC_SYMBOLS = [
    "ApprovalDecision",
    "ApprovalActorType",
    "ApprovalOutcome",
    "AudioProject",
    "AudioVersion",
    "CreativeBrief",
    "LegacyReference",
    "ProjectStatus",
    "ProjectThread",
    "ThreadRole",
    "ThreadStatus",
    "ThreadType",
    "TreatmentAction",
    "TreatmentPlan",
    "TreatmentStepType",
    "TreatmentVariant",
    "VersionStatus",
    "ProjectWorkflow",
    "WorkflowAction",
    "WorkflowEvent",
    "WorkflowStage",
]


class TestDomainPublicContract:
    def test_all_public_symbols_resolve(self) -> None:
        missing = [s for s in PUBLIC_SYMBOLS if not hasattr(domain, s)]
        assert not missing, f"missing domain exports: {missing}"

    def test_symbols_importable_from_root(self) -> None:
        for symbol in PUBLIC_SYMBOLS:
            getattr(importlib.import_module("moodify.domain"), symbol)

    def test_audio_project_is_pydantic_aggregate(self) -> None:
        assert domain.AudioProject is not None
        assert hasattr(domain.AudioProject, "model_validate_json")
        assert hasattr(domain.AudioProject, "model_dump_json")

    def test_no_canonical_project_leak_in_root(self) -> None:
        # CanonicalProject experiment lives in its own module; it must not
        # shadow the v2 AudioProject contract in the package root.
        assert not hasattr(domain, "CanonicalProject")

    def test_canonical_experiment_preserved_in_module(self) -> None:
        from moodify.domain.canonical_project import CanonicalProject

        project = CanonicalProject.create("experiment")
        assert project.title == "experiment"
        assert len(project.revisions) == 1
