"""Workspace v2 project CRUD endpoints."""

from __future__ import annotations

from datetime import datetime, timezone
import os
from pathlib import Path
from typing import Any

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse, HTMLResponse
from pydantic import BaseModel, ConfigDict, Field, ValidationError, model_validator

from moodify.domain import (
    ApprovalActorType,
    ApprovalDecision,
    ApprovalOutcome,
    AudioProject,
    AudioVersion,
    CreativeBrief,
    ProjectStatus,
    ProjectThread,
    ThreadStatus,
    ThreadType,
    VersionStatus,
)
from moodify.storage import (
    StorageConflict,
    StorageCorruption,
    StorageNotFound,
    WorkspaceStore,
)


router = APIRouter(prefix="/workspace/projects", tags=["workspace-projects"])


class WorkspaceProjectCreate(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    project_id: str = Field(min_length=1)
    title: str = Field(min_length=1)
    source_audio_ids: list[str] = Field(min_length=1)
    creative_brief: CreativeBrief | None = None
    commercial_project_id: str | None = None
    privacy_policy: dict[str, Any] = Field(default_factory=dict)


class WorkspaceProjectPatch(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    title: str | None = Field(default=None, min_length=1)
    status: ProjectStatus | None = None
    creative_brief: CreativeBrief | None = None
    active_version_id: str | None = None
    approved_version_id: str | None = None
    delivered_version_id: str | None = None
    commercial_project_id: str | None = None
    privacy_policy: dict[str, Any] | None = None

    @model_validator(mode="after")
    def patch_must_change_something(self) -> "WorkspaceProjectPatch":
        if not self.model_fields_set:
            raise ValueError("PATCH body must contain at least one field")
        return self


class CreativeBriefPatch(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    goal: str | None = Field(default=None, min_length=1)
    preserve: list[str] | None = None
    avoid: list[str] | None = None
    platform: str | None = Field(default=None, min_length=1)
    reference: list[str] | None = None

    @model_validator(mode="after")
    def patch_must_contain_non_null_fields(self) -> "CreativeBriefPatch":
        if not self.model_fields_set:
            raise ValueError("PATCH body must contain at least one field")
        if any(getattr(self, field) is None for field in self.model_fields_set):
            raise ValueError("brief fields cannot be null")
        return self


class AudioVersionCreate(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    version_id: str = Field(min_length=1)
    parent_version_id: str | None = None
    branch: str = Field(default="main", min_length=1)
    name: str = Field(min_length=1)
    purpose: str = Field(min_length=1)
    audio_path: str = Field(min_length=1)
    audio_sha256: str
    treatment_plan_id: str | None = None
    treatment_variant_id: str | None = None
    treatment_record_id: str | None = None
    created_by: str = Field(min_length=1)


class AudioVersionBranch(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    version_id: str = Field(min_length=1)
    branch: str = Field(min_length=1)
    name: str = Field(min_length=1)
    purpose: str = Field(min_length=1)
    audio_path: str = Field(min_length=1)
    audio_sha256: str
    treatment_plan_id: str | None = None
    treatment_variant_id: str | None = None
    treatment_record_id: str | None = None
    created_by: str = Field(min_length=1)


class AudioVersionRollback(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    version_id: str = Field(min_length=1)
    branch: str = Field(default="main", min_length=1)
    name: str = Field(min_length=1)
    purpose: str = Field(min_length=1)
    created_by: str = Field(min_length=1)


class ApprovalRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    decision_id: str = Field(min_length=1)
    version_id: str = Field(min_length=1)
    outcome: ApprovalOutcome
    reason: str = Field(min_length=1)
    operator: str = Field(min_length=1)
    actor_type: ApprovalActorType = ApprovalActorType.HUMAN
    return_to_thread: ThreadType | None = None
    supersedes_decision_id: str | None = None


def _store() -> WorkspaceStore:
    root = Path(os.environ.get("MOODIFY_WORKSPACE_ROOT", "data/workspace_v2"))
    return WorkspaceStore(root)


def _storage_error(exc: Exception) -> HTTPException:
    if isinstance(exc, StorageNotFound):
        return HTTPException(status_code=404, detail="workspace project not found")
    if isinstance(exc, StorageConflict):
        return HTTPException(status_code=409, detail=str(exc))
    if isinstance(exc, StorageCorruption):
        return HTTPException(status_code=500, detail="workspace data is corrupt")
    if isinstance(exc, ValidationError):
        return HTTPException(
            status_code=422,
            detail=exc.errors(
                include_context=False,
                include_url=False,
                include_input=False,
            ),
        )
    if isinstance(exc, ValueError):
        return HTTPException(status_code=400, detail=str(exc))
    return HTTPException(status_code=500, detail="workspace storage failure")


@router.post("", response_model=AudioProject, status_code=201)
def create_workspace_project(request: WorkspaceProjectCreate) -> AudioProject:
    now = datetime.now(timezone.utc)
    project = AudioProject(
        **request.model_dump(),
        created_at=now,
        updated_at=now,
    )
    try:
        _store().create_project(project)
        return project
    except Exception as exc:
        raise _storage_error(exc) from exc


@router.get("/ui", response_class=HTMLResponse)
def workspace_ui() -> HTMLResponse:
    """Serve the workspace v2 UI.

    This static route must be registered before ``/{project_id}``, otherwise
    FastAPI interprets ``ui`` as a project identifier.
    """
    ui_path = Path(__file__).parent / "workspace_ui.html"
    return HTMLResponse(content=ui_path.read_text(encoding="utf-8"))


@router.get("/{project_id}", response_model=AudioProject)
def get_workspace_project(project_id: str) -> AudioProject:
    try:
        return _store().get_project(project_id)
    except Exception as exc:
        raise _storage_error(exc) from exc


@router.patch("/{project_id}", response_model=AudioProject)
def patch_workspace_project(
    project_id: str, request: WorkspaceProjectPatch
) -> AudioProject:
    try:
        current = _store().get_project(project_id)
        payload = current.model_dump()
        payload.update(request.model_dump(exclude_unset=True))
        payload["project_id"] = project_id
        payload["updated_at"] = datetime.now(timezone.utc)
        updated = AudioProject.model_validate(payload)
        _store().update_project(updated)
        return updated
    except Exception as exc:
        raise _storage_error(exc) from exc


@router.post("/{project_id}/brief", response_model=CreativeBrief, status_code=201)
def create_creative_brief(
    project_id: str, request: CreativeBrief
) -> CreativeBrief:
    try:
        current = _store().get_project(project_id)
        if current.creative_brief is not None:
            raise StorageConflict(
                f"creative brief already exists for project: {project_id}"
            )
        payload = current.model_dump()
        payload["creative_brief"] = request.model_dump()
        payload["updated_at"] = datetime.now(timezone.utc)
        updated = AudioProject.model_validate(payload)
        _store().update_project(updated)
        return updated.creative_brief
    except Exception as exc:
        raise _storage_error(exc) from exc


@router.patch("/{project_id}/brief", response_model=CreativeBrief)
def patch_creative_brief(
    project_id: str, request: CreativeBriefPatch
) -> CreativeBrief:
    try:
        current = _store().get_project(project_id)
        if current.creative_brief is None:
            raise StorageConflict(
                f"creative brief does not exist for project: {project_id}"
            )
        brief_payload = current.creative_brief.model_dump()
        brief_payload.update(request.model_dump(exclude_unset=True))
        updated_brief = CreativeBrief.model_validate(brief_payload)
        project_payload = current.model_dump()
        project_payload["creative_brief"] = updated_brief.model_dump()
        project_payload["updated_at"] = datetime.now(timezone.utc)
        updated = AudioProject.model_validate(project_payload)
        _store().update_project(updated)
        return updated.creative_brief
    except Exception as exc:
        raise _storage_error(exc) from exc


@router.get("/{project_id}/threads", response_model=list[ProjectThread])
def list_project_threads(project_id: str) -> list[ProjectThread]:
    try:
        return _store().list_threads(project_id)
    except Exception as exc:
        raise _storage_error(exc) from exc


def _activate_version(store: WorkspaceStore, project: AudioProject, version: AudioVersion) -> None:
    payload = project.model_dump()
    payload["active_version_id"] = version.version_id
    payload["updated_at"] = datetime.now(timezone.utc)
    store.update_project(AudioProject.model_validate(payload))


@router.post("/{project_id}/versions", response_model=AudioVersion, status_code=201)
def create_audio_version(
    project_id: str, request: AudioVersionCreate
) -> AudioVersion:
    try:
        store = _store()
        project = store.get_project(project_id)
        now = datetime.now(timezone.utc)
        version = AudioVersion(
            **request.model_dump(),
            project_id=project_id,
            created_at=now,
            updated_at=now,
        )
        store.create_version_checked(version)
        _activate_version(store, project, version)
        return version
    except Exception as exc:
        raise _storage_error(exc) from exc


@router.get("/{project_id}/versions", response_model=list[AudioVersion])
def list_audio_versions(project_id: str) -> list[AudioVersion]:
    try:
        return _store().list_versions(project_id)
    except Exception as exc:
        raise _storage_error(exc) from exc


@router.get(
    "/{project_id}/versions/{version_id}", response_model=AudioVersion
)
def get_audio_version(project_id: str, version_id: str) -> AudioVersion:
    try:
        return _store().get_version(project_id, version_id)
    except Exception as exc:
        raise _storage_error(exc) from exc


@router.get("/{project_id}/versions/{version_id}/audio")
def stream_audio_version(project_id: str, version_id: str) -> FileResponse:
    """Serve immutable version audio for the Workspace A/B player."""
    try:
        store = _store()
        version = store.get_version(project_id, version_id)
        project_dir = store._project_dir(project_id)
        audio_path = (project_dir / version.audio_path).resolve()
        if project_dir not in audio_path.parents or not audio_path.is_file():
            raise StorageNotFound(
                f"version audio file not found: {version.audio_path}"
            )
        media_types = {
            ".wav": "audio/wav",
            ".flac": "audio/flac",
            ".aif": "audio/aiff",
            ".aiff": "audio/aiff",
        }
        return FileResponse(
            audio_path,
            media_type=media_types.get(audio_path.suffix.casefold(), "application/octet-stream"),
            filename=audio_path.name,
        )
    except Exception as exc:
        raise _storage_error(exc) from exc


@router.post(
    "/{project_id}/versions/{parent_version_id}/branch",
    response_model=AudioVersion,
    status_code=201,
)
def branch_audio_version(
    project_id: str,
    parent_version_id: str,
    request: AudioVersionBranch,
) -> AudioVersion:
    payload = request.model_dump()
    payload["parent_version_id"] = parent_version_id
    try:
        store = _store()
        project = store.get_project(project_id)
        store.get_version(project_id, parent_version_id)
        now = datetime.now(timezone.utc)
        version = AudioVersion(
            **payload,
            project_id=project_id,
            created_at=now,
            updated_at=now,
        )
        store.create_version_checked(version)
        _activate_version(store, project, version)
        return version
    except Exception as exc:
        raise _storage_error(exc) from exc


@router.post(
    "/{project_id}/versions/{target_version_id}/rollback",
    response_model=AudioVersion,
    status_code=201,
)
def rollback_audio_version(
    project_id: str,
    target_version_id: str,
    request: AudioVersionRollback,
) -> AudioVersion:
    try:
        store = _store()
        project = store.get_project(project_id)
        target = store.get_version(project_id, target_version_id)
        parent_id = project.active_version_id or target_version_id
        if project.active_version_id is not None:
            store.get_version(project_id, project.active_version_id)
        now = datetime.now(timezone.utc)
        version = AudioVersion(
            version_id=request.version_id,
            project_id=project_id,
            parent_version_id=parent_id,
            branch=request.branch,
            name=request.name,
            purpose=request.purpose,
            audio_path=target.audio_path,
            audio_sha256=target.audio_sha256,
            treatment_plan_id=target.treatment_plan_id,
            treatment_variant_id=target.treatment_variant_id,
            treatment_record_id=target.treatment_record_id,
            created_by=request.created_by,
            created_at=now,
            updated_at=now,
        )
        store.create_version_checked(version)
        _activate_version(store, project, version)
        return version
    except Exception as exc:
        raise _storage_error(exc) from exc


def _judge_passed_for_version(
    store: WorkspaceStore, project_id: str, version_id: str
) -> bool:
    return any(
        thread.thread_type is ThreadType.JUDGE
        and thread.status is ThreadStatus.PASSED
        and thread.outputs.get("version_id") == version_id
        for thread in store.list_threads(project_id)
    )


@router.post(
    "/{project_id}/approve",
    response_model=ApprovalDecision,
    status_code=201,
)
def approve_audio_version(
    project_id: str, request: ApprovalRequest
) -> ApprovalDecision:
    try:
        store = _store()
        project = store.get_project(project_id)
        version = store.get_version(project_id, request.version_id)
        existing = store.list_approvals(project_id)
        if any(
            decision.decision_id == request.decision_id
            for decision in existing
        ):
            raise StorageConflict(
                f"approval already exists: {request.decision_id}"
            )
        if request.supersedes_decision_id is not None:
            superseded = next(
                (
                    decision
                    for decision in existing
                    if decision.decision_id == request.supersedes_decision_id
                ),
                None,
            )
            if superseded is None or superseded.version_id != request.version_id:
                raise StorageConflict(
                    "superseded decision must exist for the same version"
                )
        if request.outcome is ApprovalOutcome.APPROVED and not (
            _judge_passed_for_version(store, project_id, request.version_id)
        ):
            raise StorageConflict(
                "version cannot be approved before its Judge thread passes"
            )
        now = datetime.now(timezone.utc)
        decision = ApprovalDecision(
            **request.model_dump(),
            project_id=project_id,
            decided_at=now,
        )
        reviewing = version
        if version.status is VersionStatus.DRAFT:
            reviewing = version.transition_to(VersionStatus.REVIEWING, at=now)
        target_status = (
            VersionStatus.APPROVED
            if request.outcome is ApprovalOutcome.APPROVED
            else VersionStatus.REJECTED
        )
        updated_version = reviewing.transition_to(
            target_status,
            at=now,
            approval=decision,
        )
        project_payload = project.model_dump()
        project_payload["active_version_id"] = version.version_id
        project_payload["updated_at"] = now
        if request.outcome is ApprovalOutcome.APPROVED:
            project_payload["approved_version_id"] = version.version_id
            project_payload["status"] = ProjectStatus.APPROVED
        updated_project = AudioProject.model_validate(project_payload)
        store.append_approval(decision)
        store.update_version(updated_version)
        store.update_project(updated_project)
        return decision
    except Exception as exc:
        raise _storage_error(exc) from exc


@router.get("/{project_id}/versions/{version_id_a}/compare/{version_id_b}")
def compare_audio_versions(
    project_id: str,
    version_id_a: str,
    version_id_b: str,
) -> dict:
    """Compare two audio versions across all dimensions."""
    try:
        from moodify.services.version_compare import VersionCompareService
        service = VersionCompareService(_store())
        return service.compare(project_id, version_id_a, version_id_b)
    except Exception as exc:
        raise _storage_error(exc) from exc


@router.get("/{project_id}/versions/compare/list")
def list_comparable_versions(
    project_id: str,
    reference_version_id: str | None = None,
) -> list[dict]:
    """List versions available for comparison."""
    try:
        from moodify.services.version_compare import VersionCompareService
        service = VersionCompareService(_store())
        return service.list_comparable_versions(
            project_id, reference_version_id=reference_version_id
        )
    except Exception as exc:
        raise _storage_error(exc) from exc
