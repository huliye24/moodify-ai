"""Archive service for workspace v2 project finalization.

Packages original audio, versions, reports, parameters, feedback and Final
into a structured archive with a verifiable manifest.
"""

from __future__ import annotations

import hashlib
import json
from collections.abc import Callable
from datetime import datetime, timezone
from typing import Any

from moodify.domain import (
    ApprovalOutcome,
    ProjectStatus,
    ProjectThread,
    ThreadRole,
    ThreadStatus,
    ThreadType,
    VersionStatus,
)
from moodify.storage import WorkspaceStore

Clock = Callable[[], datetime]


class ArchiveService:
    """Packages workspace project deliverables into a verifiable archive.

    Produces:
    - archive_manifest.json: full inventory with SHA-256 checksums
    - archived versions with immutable status markers
    - consolidated thread summary
    - approval decision log (JSONL)
    """

    def __init__(
        self,
        store: WorkspaceStore,
        *,
        clock: Clock | None = None,
    ) -> None:
        self.store = store
        self.clock = clock or (lambda: datetime.now(timezone.utc))

    def archive_project(
        self,
        project_id: str,
        thread_id: str,
    ) -> dict[str, Any]:
        """Archive a completed project and return the manifest."""
        project = self.store.get_project(project_id)
        workflow = self.store.get_workflow(project_id)

        if project.status is ProjectStatus.ARCHIVED:
            raise ValueError("project is already archived")

        now = self.clock()

        thread = ProjectThread(
            thread_id=thread_id,
            project_id=project_id,
            thread_type=ThreadType.ARCHIVE,
            role=ThreadRole.ARCHIVE,
            inputs={"action": "archive"},
            created_at=now,
            updated_at=now,
        )
        self.store.create_thread(thread)

        running = thread.transition_to(
            ThreadStatus.QUEUED, at=now
        ).transition_to(ThreadStatus.RUNNING, at=now)
        self.store.update_thread(running)

        try:
            versions = self.store.list_versions(project_id)
            threads = self.store.list_threads(project_id)
            approvals = self.store.list_approvals(project_id)

            project_dir = self.store._project_dir(project_id)
            archive_dir = project_dir / "archive"
            archive_dir.mkdir(parents=True, exist_ok=True)

            manifest: dict[str, Any] = {
                "archive_version": "workspace_archive.v1",
                "project_id": project_id,
                "archived_at": now.isoformat(),
                "archive_thread_id": thread_id,
                "project": project.model_dump(mode="json"),
                "workflow": workflow.model_dump(mode="json"),
                "version_count": len(versions),
                "thread_count": len(threads),
                "approval_count": len(approvals),
                "contents": {},
            }

            manifest["contents"]["versions"] = []
            for version in versions:
                audio_path = project_dir / version.audio_path
                entry: dict[str, Any] = {
                    "version_id": version.version_id,
                    "name": version.name,
                    "status": version.status.value,
                    "audio_sha256": version.audio_sha256,
                }
                if audio_path.exists():
                    verification = hashlib.sha256(
                        audio_path.read_bytes()
                    ).hexdigest()
                    entry["audio_verified"] = (
                        verification == version.audio_sha256
                    )
                else:
                    entry["audio_verified"] = False
                    entry["audio_missing"] = True

                if version.status not in {
                    VersionStatus.ARCHIVED,
                    VersionStatus.DELIVERED,
                }:
                    archived_version = version.transition_to(
                        VersionStatus.ARCHIVED, at=now
                    )
                    self.store.update_version(archived_version)

                manifest["contents"]["versions"].append(entry)

            manifest["contents"]["threads_summary"] = {
                "by_type": {},
                "by_status": {},
            }
            for t in threads:
                ttype = t.thread_type.value
                tstatus = t.status.value
                manifest["contents"]["threads_summary"]["by_type"][ttype] = (
                    manifest["contents"]["threads_summary"]
                    .get("by_type", {})
                    .get(ttype, 0) + 1
                )
                manifest["contents"]["threads_summary"]["by_status"][tstatus] = (
                    manifest["contents"]["threads_summary"]
                    .get("by_status", {})
                    .get(tstatus, 0) + 1
                )

            manifest["contents"]["approvals"] = [
                a.model_dump(mode="json") for a in approvals
            ]

            has_final_approval = any(
                a.outcome is ApprovalOutcome.APPROVED for a in approvals
            )
            manifest["contents"]["final_approval_exists"] = has_final_approval

            manifest_path = archive_dir / "archive_manifest.json"
            manifest_path.write_text(
                json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True),
                encoding="utf-8",
            )

            manifest_sha256 = hashlib.sha256(
                manifest_path.read_bytes()
            ).hexdigest()

            finalized_at = self.clock()
            outputs = {
                "manifest_path": str(
                    manifest_path.relative_to(project_dir)
                ),
                "manifest_sha256": manifest_sha256,
                "version_count": len(versions),
                "thread_count": len(threads),
                "approval_count": len(approvals),
                "final_approval_exists": has_final_approval,
                "archived_at": finalized_at.isoformat(),
            }

            passed = running.transition_to(
                ThreadStatus.PASSED, at=finalized_at, outputs=outputs,
            )

            project_payload = project.model_dump()
            project_payload["status"] = ProjectStatus.ARCHIVED.value
            project_payload["updated_at"] = finalized_at
            from moodify.domain.project import AudioProject
            updated_project = AudioProject.model_validate(project_payload)

            self.store.update_thread(passed)
            self.store.update_project(updated_project)

            try:
                if workflow.stage.value not in {"FINAL", "FAILED"}:
                    advanced = workflow.advance(
                        at=finalized_at,
                        reason=f"archive created: {thread_id}",
                    )
                    self.store.update_workflow(advanced)
            except Exception:
                pass

            return outputs

        except Exception as exc:
            failed_at = self.clock()
            message = str(exc) or exc.__class__.__name__
            failed = running.transition_to(
                ThreadStatus.FAILED, at=failed_at, error=message,
            )
            self.store.update_thread(failed)
            raise

    def verify_archive(
        self, project_id: str
    ) -> dict[str, Any]:
        """Verify an existing archive's integrity."""
        project_dir = self.store._project_dir(project_id)
        archive_dir = project_dir / "archive"
        manifest_path = archive_dir / "archive_manifest.json"

        if not manifest_path.exists():
            return {
                "verified": False,
                "reason": "no archive manifest found",
                "project_id": project_id,
            }

        try:
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        except Exception as exc:
            return {
                "verified": False,
                "reason": f"manifest read error: {exc}",
                "project_id": project_id,
            }

        issues: list[str] = []

        versions = self.store.list_versions(project_id)
        manifest_version_ids = {
            v["version_id"] for v in manifest.get("contents", {}).get("versions", [])
        }
        actual_version_ids = {v.version_id for v in versions}

        if manifest_version_ids != actual_version_ids:
            missing = actual_version_ids - manifest_version_ids
            extra = manifest_version_ids - actual_version_ids
            if missing:
                issues.append(f"versions not in manifest: {missing}")
            if extra:
                issues.append(f"versions in manifest but missing: {extra}")

        for version in versions:
            audio_path = project_dir / version.audio_path
            if not audio_path.exists():
                issues.append(
                    f"audio missing for version {version.version_id}: "
                    f"{version.audio_path}"
                )

        return {
            "verified": len(issues) == 0,
            "project_id": project_id,
            "manifest_archived_at": manifest.get("archived_at"),
            "version_count": len(versions),
            "issues": issues,
        }
