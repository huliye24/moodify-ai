"""Canonical Music Project — experimental single-source-of-truth model.

This is an experimental dataclass model created in the working tree as a
replacement candidate for the v2 AudioProject pydantic aggregate. It has no
consumers yet and is preserved here (moved out of project.py by
DSK-MFY-ORDER-BEAUTY-022) so the v2 contract (AudioProject) is restored
without discarding this experiment. Do not delete until a decision is made.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from enum import StrEnum
from pathlib import Path
from uuid import uuid4


class AssetKind(StrEnum):
    AUDIO = "audio"
    MIDI = "midi"
    SCORE = "score"
    LYRICS = "lyrics"
    STEM = "stem"
    OTHER = "other"


class DecisionStatus(StrEnum):
    PROPOSED = "proposed"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    DEFERRED = "deferred"


class RunStatus(StrEnum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class AssetRef:
    asset_id: str
    kind: AssetKind = AssetKind.AUDIO
    path: str = ""
    sha256: str = ""
    role: str = "source"
    metadata: dict = field(default_factory=dict)


@dataclass
class Decision:
    decision_id: str
    status: DecisionStatus = DecisionStatus.PROPOSED
    description: str = ""
    rationale: str = ""
    owner: str = ""
    constraints: dict = field(default_factory=dict)


@dataclass
class Plan:
    plan_id: str
    intent: dict = field(default_factory=dict)
    steps: list[dict] = field(default_factory=list)
    dry_run: bool = False
    estimated_duration_s: float = 0.0
    warnings: list[str] = field(default_factory=list)


@dataclass
class Artifact:
    artifact_id: str
    kind: str = ""
    path: str = ""
    sha256: str = ""
    metadata: dict = field(default_factory=dict)


@dataclass
class Run:
    run_id: str
    plan_id: str = ""
    status: RunStatus = RunStatus.PENDING
    artifacts: list[Artifact] = field(default_factory=list)
    evidence_path: str = ""
    elapsed_seconds: float = 0.0
    exit_code: int = -1
    errors: list[str] = field(default_factory=list)


@dataclass
class Revision:
    revision_id: str
    parent_revision_id: str = ""
    description: str = ""
    author: str = ""
    created_at: str = ""


@dataclass
class Evidence:
    evidence_id: str
    run_id: str = ""
    command: list[str] = field(default_factory=list)
    exit_code: int = -1
    artifacts: list[dict] = field(default_factory=list)
    source_hashes: dict[str, str] = field(default_factory=dict)


@dataclass
class CanonicalProject:
    schema_version: str = "1.0.0"
    project_id: str = ""
    title: str = ""
    assets: list[AssetRef] = field(default_factory=list)
    decisions: list[Decision] = field(default_factory=list)
    plans: list[Plan] = field(default_factory=list)
    runs: list[Run] = field(default_factory=list)
    revisions: list[Revision] = field(default_factory=list)
    evidence: list[Evidence] = field(default_factory=list)
    metadata: dict = field(default_factory=dict)

    @classmethod
    def create(cls, title: str, project_id: str | None = None) -> CanonicalProject:
        return cls(
            project_id=project_id or str(uuid4()),
            title=title,
            revisions=[Revision(revision_id="1", description="Initialized")],
        )

    def add_asset(self, path: str, kind: AssetKind = AssetKind.AUDIO) -> AssetRef:
        aid = str(uuid4())[:8]
        sha = hashlib.sha256(Path(path).read_bytes()).hexdigest() if Path(path).exists() else ""
        ref = AssetRef(asset_id=aid, kind=kind, path=path, sha256=sha)
        self.assets.append(ref)
        return ref

    def add_plan(self, intent: dict) -> Plan:
        p = Plan(plan_id=str(uuid4())[:8], intent=intent)
        self.plans.append(p)
        return p

    def add_run(self, plan_id: str) -> Run:
        r = Run(run_id=str(uuid4())[:8], plan_id=plan_id)
        self.runs.append(r)
        return r
