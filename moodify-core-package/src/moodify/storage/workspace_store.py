"""Crash-safe local JSON/JSONL storage for Workspace v2."""

from __future__ import annotations

import json
import hashlib
import os
from pathlib import Path
import re
import tempfile
import shutil
from typing import TypeVar

from pydantic import BaseModel, ValidationError

from moodify.domain import (
    ApprovalDecision,
    AudioProject,
    AudioVersion,
    ProjectThread,
    ProjectWorkflow,
    ThreadType,
    TreatmentPlan,
)


_SAFE_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*$")
ModelT = TypeVar("ModelT", bound=BaseModel)
_THREAD_WORKFLOW_ORDER = {
    thread_type: position for position, thread_type in enumerate(ThreadType)
}


class StorageNotFound(FileNotFoundError):
    pass


class StorageConflict(RuntimeError):
    pass


class StorageCorruption(RuntimeError):
    pass


class WorkspaceStore:
    """Project-isolated store with atomic snapshots and append-only approvals."""

    def __init__(self, root: Path | str) -> None:
        self.root = Path(root).resolve()
        self.root.mkdir(parents=True, exist_ok=True)

    def create_project(self, project: AudioProject) -> None:
        path = self._project_dir(project.project_id) / "project.json"
        self._create_snapshot(path, project)

    def get_project(self, project_id: str) -> AudioProject:
        return self._read_snapshot(
            self._project_dir(project_id) / "project.json", AudioProject
        )

    def update_project(self, project: AudioProject) -> None:
        path = self._project_dir(project.project_id) / "project.json"
        self._require_exists(path)
        self._atomic_write_json(path, project.model_dump(mode="json"))

    def resolve_source_audio(self, project_id: str, source_audio_id: str) -> Path:
        self.get_project(project_id)
        self._validate_id(source_audio_id)
        source_dir = self._project_dir(project_id) / "sources"
        exact = source_dir / source_audio_id
        candidates = [exact] if exact.is_file() else sorted(
            path
            for path in source_dir.glob(f"{source_audio_id}.*")
            if path.suffix.casefold() in {".wav", ".flac", ".aif", ".aiff"}
        )
        if not candidates:
            raise StorageNotFound(f"source audio not found: {source_audio_id}")
        if len(candidates) > 1:
            raise StorageConflict(
                f"source audio identifier is ambiguous: {source_audio_id}"
            )
        return candidates[0].resolve()

    def diagnostic_output_dir(self, project_id: str, thread_id: str) -> Path:
        self.get_project(project_id)
        self._validate_id(thread_id)
        path = self._project_dir(project_id) / "diagnostics" / thread_id
        path.mkdir(parents=True, exist_ok=True)
        return path

    def processing_output_dir(self, project_id: str, thread_id: str) -> Path:
        self.get_project(project_id)
        self._validate_id(thread_id)
        path = self._project_dir(project_id) / "processing" / thread_id
        path.mkdir(parents=True, exist_ok=True)
        return path

    def stage_version_audio(
        self, project_id: str, version_id: str, source_path: Path
    ) -> tuple[str, str]:
        self.get_project(project_id)
        self._validate_id(version_id)
        source = Path(source_path).resolve()
        if not source.is_file():
            raise StorageNotFound(f"processed audio not found: {source_path}")
        suffix = source.suffix.casefold()
        if suffix not in {".wav", ".flac", ".aif", ".aiff"}:
            raise ValueError("processed audio must use a supported lossless type")
        relative = f"versions/{version_id}{suffix}"
        target = self._project_dir(project_id) / relative
        if target.exists():
            raise StorageConflict(f"version audio already exists: {version_id}")
        target.parent.mkdir(parents=True, exist_ok=True)
        descriptor, temp_name = tempfile.mkstemp(
            prefix=f".{target.name}.", suffix=".tmp", dir=target.parent
        )
        os.close(descriptor)
        temp_path = Path(temp_name)
        try:
            shutil.copyfile(source, temp_path)
            if target.exists():
                raise StorageConflict(
                    f"version audio already exists: {version_id}"
                )
            os.replace(temp_path, target)
        finally:
            if temp_path.exists():
                temp_path.unlink()
        digest = hashlib.sha256(target.read_bytes()).hexdigest()
        return relative, digest

    def create_workflow(self, workflow: ProjectWorkflow) -> None:
        self.get_project(workflow.project_id)
        self._create_snapshot(
            self._project_dir(workflow.project_id) / "workflow.json",
            workflow,
        )

    def get_workflow(self, project_id: str) -> ProjectWorkflow:
        self.get_project(project_id)
        return self._read_snapshot(
            self._project_dir(project_id) / "workflow.json",
            ProjectWorkflow,
        )

    def update_workflow(self, workflow: ProjectWorkflow) -> None:
        current = self.get_workflow(workflow.project_id)
        if workflow.created_at != current.created_at:
            raise StorageConflict("workflow identity is immutable")
        path = self._project_dir(workflow.project_id) / "workflow.json"
        self._atomic_write_json(path, workflow.model_dump(mode="json"))

    def create_thread(self, thread: ProjectThread) -> None:
        self._create_snapshot(
            self._entity_path(thread.project_id, "threads", thread.thread_id),
            thread,
        )

    def get_thread(self, project_id: str, thread_id: str) -> ProjectThread:
        return self._read_snapshot(
            self._entity_path(project_id, "threads", thread_id), ProjectThread
        )

    def update_thread(self, thread: ProjectThread) -> None:
        path = self._entity_path(thread.project_id, "threads", thread.thread_id)
        self._require_exists(path)
        self._atomic_write_json(path, thread.model_dump(mode="json"))

    def list_threads(self, project_id: str) -> list[ProjectThread]:
        self.get_project(project_id)
        threads = [
            self.get_thread(project_id, thread_id)
            for thread_id in self.list_ids(project_id, "threads")
        ]
        return sorted(
            threads,
            key=lambda thread: (
                _THREAD_WORKFLOW_ORDER[thread.thread_type],
                thread.created_at,
                thread.thread_id,
            ),
        )

    def create_plan(self, plan: TreatmentPlan) -> None:
        self._create_snapshot(
            self._entity_path(plan.project_id, "plans", plan.plan_id), plan
        )

    def get_plan(self, project_id: str, plan_id: str) -> TreatmentPlan:
        return self._read_snapshot(
            self._entity_path(project_id, "plans", plan_id), TreatmentPlan
        )

    def create_version(self, version: AudioVersion) -> None:
        self._create_snapshot(
            self._entity_path(
                version.project_id, "versions", version.version_id
            ),
            version,
        )

    def create_version_checked(self, version: AudioVersion) -> None:
        self.get_project(version.project_id)
        audio_path = (
            self._project_dir(version.project_id) / version.audio_path
        ).resolve()
        project_dir = self._project_dir(version.project_id)
        if project_dir not in audio_path.parents or not audio_path.is_file():
            raise StorageNotFound(f"version audio file not found: {version.audio_path}")
        self._validate_version_parent_chain(version)
        self.create_version(version)

    def get_version(self, project_id: str, version_id: str) -> AudioVersion:
        return self._read_snapshot(
            self._entity_path(project_id, "versions", version_id), AudioVersion
        )

    def update_version(self, version: AudioVersion) -> None:
        current = self.get_version(version.project_id, version.version_id)
        immutable_fields = (
            "version_id",
            "project_id",
            "parent_version_id",
            "branch",
            "name",
            "purpose",
            "audio_path",
            "audio_sha256",
            "treatment_plan_id",
            "treatment_variant_id",
            "treatment_record_id",
            "created_by",
            "created_at",
        )
        if any(
            getattr(current, field) != getattr(version, field)
            for field in immutable_fields
        ):
            raise StorageConflict("version audio identity and lineage are immutable")
        path = self._entity_path(
            version.project_id, "versions", version.version_id
        )
        self._atomic_write_json(path, version.model_dump(mode="json"))

    def list_versions(self, project_id: str) -> list[AudioVersion]:
        self.get_project(project_id)
        versions = [
            self.get_version(project_id, version_id)
            for version_id in self.list_ids(project_id, "versions")
        ]
        for version in versions:
            self._validate_version_parent_chain(version, allow_existing=True)
        return sorted(versions, key=lambda version: (version.created_at, version.version_id))

    def append_approval(self, decision: ApprovalDecision) -> None:
        project_dir = self._project_dir(decision.project_id)
        self._require_exists(project_dir / "project.json")
        log_path = project_dir / "approvals.jsonl"
        rows = self._read_jsonl(log_path)
        if any(row.get("decision_id") == decision.decision_id for row in rows):
            raise StorageConflict(
                f"approval already exists: {decision.decision_id}"
            )
        rows.append(decision.model_dump(mode="json"))
        self._atomic_write_jsonl(log_path, rows)

    def list_approvals(self, project_id: str) -> list[ApprovalDecision]:
        path = self._project_dir(project_id) / "approvals.jsonl"
        rows = self._read_jsonl(path)
        try:
            return [ApprovalDecision.model_validate(row) for row in rows]
        except ValidationError as exc:
            raise StorageCorruption(f"invalid approval log: {path}") from exc

    def list_ids(self, project_id: str, collection: str) -> list[str]:
        if collection not in {"threads", "plans", "versions"}:
            raise ValueError("unsupported collection")
        directory = self._project_dir(project_id) / collection
        if not directory.exists():
            return []
        return sorted(path.stem for path in directory.glob("*.json"))

    def _entity_path(
        self, project_id: str, collection: str, entity_id: str
    ) -> Path:
        self._validate_id(entity_id)
        return self._project_dir(project_id) / collection / f"{entity_id}.json"

    def _validate_version_parent_chain(
        self, version: AudioVersion, *, allow_existing: bool = False
    ) -> None:
        seen = {version.version_id}
        parent_id = version.parent_version_id
        while parent_id is not None:
            if parent_id in seen:
                raise StorageConflict("version tree must not contain a cycle")
            seen.add(parent_id)
            parent = self.get_version(version.project_id, parent_id)
            parent_id = parent.parent_version_id
        if not allow_existing and (
            self._entity_path(version.project_id, "versions", version.version_id)
        ).exists():
            raise StorageConflict(f"version already exists: {version.version_id}")

    def _project_dir(self, project_id: str) -> Path:
        self._validate_id(project_id)
        path = (self.root / "projects" / project_id).resolve()
        if self.root not in path.parents:
            raise ValueError("project path escapes workspace root")
        return path

    @staticmethod
    def _validate_id(value: str) -> None:
        if not _SAFE_ID.fullmatch(value):
            raise ValueError("storage identifiers must be portable and path-safe")

    def _create_snapshot(self, path: Path, model: BaseModel) -> None:
        if path.exists():
            raise StorageConflict(f"record already exists: {path.stem}")
        self._atomic_write_json(path, model.model_dump(mode="json"))

    @staticmethod
    def _require_exists(path: Path) -> None:
        if not path.exists():
            raise StorageNotFound(str(path))

    @staticmethod
    def _read_snapshot(path: Path, model_type: type[ModelT]) -> ModelT:
        WorkspaceStore._require_exists(path)
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
            return model_type.model_validate(payload)
        except (OSError, json.JSONDecodeError, ValidationError) as exc:
            raise StorageCorruption(f"invalid snapshot: {path}") from exc

    @staticmethod
    def _read_jsonl(path: Path) -> list[dict]:
        if not path.exists():
            return []
        rows: list[dict] = []
        try:
            for number, line in enumerate(
                path.read_text(encoding="utf-8").splitlines(), start=1
            ):
                if line.strip():
                    rows.append(json.loads(line))
        except (OSError, json.JSONDecodeError) as exc:
            raise StorageCorruption(
                f"invalid JSONL record at {path}:{number}"
            ) from exc
        return rows

    @staticmethod
    def _atomic_write_json(path: Path, payload: dict) -> None:
        content = json.dumps(
            payload, ensure_ascii=False, indent=2, sort_keys=True
        ) + "\n"
        WorkspaceStore._atomic_replace(path, content)

    @staticmethod
    def _atomic_write_jsonl(path: Path, rows: list[dict]) -> None:
        content = "".join(
            json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n"
            for row in rows
        )
        WorkspaceStore._atomic_replace(path, content)

    @staticmethod
    def _atomic_replace(path: Path, content: str) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        descriptor, temp_name = tempfile.mkstemp(
            prefix=f".{path.name}.", suffix=".tmp", dir=path.parent
        )
        temp_path = Path(temp_name)
        try:
            with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
                handle.write(content)
                handle.flush()
                os.fsync(handle.fileno())
            os.replace(temp_path, path)
        finally:
            if temp_path.exists():
                temp_path.unlink()
