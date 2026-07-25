"""Domain models for the Moodify Studio Workspace v2."""

from .audio_version import (
    AudioVersion,
    VersionStatus,
)
from .approval import (
    ApprovalActorType,
    ApprovalDecision,
    ApprovalOutcome,
)
from .creative_brief import CreativeBrief
from .project import AudioProject, LegacyReference, ProjectStatus
from .thread import ProjectThread, ThreadRole, ThreadStatus, ThreadType
from .treatment_plan import (
    TreatmentAction,
    TreatmentPlan,
    TreatmentStepType,
    TreatmentVariant,
)
from .workflow import (
    ProjectWorkflow,
    WorkflowAction,
    WorkflowEvent,
    WorkflowStage,
)

__all__ = [
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
