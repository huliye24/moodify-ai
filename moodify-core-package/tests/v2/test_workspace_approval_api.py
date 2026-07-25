from datetime import datetime, timedelta, timezone

from fastapi import FastAPI
from fastapi.testclient import TestClient
import pytest

from moodify.api.routes.workspace_projects import router
from moodify.domain import (
    ProjectThread,
    ThreadRole,
    ThreadStatus,
    ThreadType,
)
from moodify.storage import WorkspaceStore


app = FastAPI()
app.include_router(router)
BASE_TIME = datetime(2026, 7, 25, 8, 0, tzinfo=timezone.utc)


@pytest.fixture()
def workspace(tmp_path, monkeypatch):
    monkeypatch.setenv("MOODIFY_WORKSPACE_ROOT", str(tmp_path))
    client = TestClient(app)
    client.post(
        "/workspace/projects",
        json={
            "project_id": "project-001",
            "title": "审批测试",
            "source_audio_ids": ["source-001"],
        },
    )
    audio_dir = tmp_path / "projects" / "project-001" / "versions"
    audio_dir.mkdir(parents=True)
    (audio_dir / "candidate.wav").write_bytes(b"candidate")
    response = client.post(
        "/workspace/projects/project-001/versions",
        json={
            "version_id": "version-001",
            "branch": "main",
            "name": "Candidate",
            "purpose": "approval",
            "audio_path": "versions/candidate.wav",
            "audio_sha256": "a" * 64,
            "created_by": "worker",
        },
    )
    assert response.status_code == 201
    return client, WorkspaceStore(tmp_path), tmp_path


def _approval(**overrides):
    payload = {
        "decision_id": "decision-001",
        "version_id": "version-001",
        "outcome": "APPROVED",
        "reason": "Judge 通过且人工试听确认",
        "operator": "producer@example.com",
        "actor_type": "HUMAN",
    }
    payload.update(overrides)
    return payload


def _passed_judge(store, version_id="version-001"):
    store.create_thread(
        ProjectThread(
            thread_id=f"judge-{version_id}",
            project_id="project-001",
            thread_type=ThreadType.JUDGE,
            role=ThreadRole.JUDGE,
            status=ThreadStatus.PASSED,
            outputs={"version_id": version_id, "result": "pass"},
            created_at=BASE_TIME,
            updated_at=BASE_TIME + timedelta(seconds=1),
            started_at=BASE_TIME,
            finished_at=BASE_TIME + timedelta(seconds=1),
        )
    )


def test_approval_requires_passed_judge_for_same_version(workspace):
    client, store, _ = workspace
    response = client.post(
        "/workspace/projects/project-001/approve", json=_approval()
    )

    assert response.status_code == 409
    assert store.list_approvals("project-001") == []
    assert store.get_version("project-001", "version-001").status.value == "DRAFT"


def test_human_approval_updates_version_and_project(workspace):
    client, store, _ = workspace
    _passed_judge(store)
    response = client.post(
        "/workspace/projects/project-001/approve", json=_approval()
    )

    assert response.status_code == 201
    assert response.json()["schema_version"] == "approval_decision.v1"
    version = store.get_version("project-001", "version-001")
    project = store.get_project("project-001")
    assert version.status.value == "APPROVED"
    assert version.approval.decision_id == "decision-001"
    assert project.status.value == "APPROVED"
    assert project.approved_version_id == "version-001"


def test_system_cannot_issue_final_approval(workspace):
    client, store, _ = workspace
    _passed_judge(store)
    response = client.post(
        "/workspace/projects/project-001/approve",
        json=_approval(actor_type="SYSTEM"),
    )
    assert response.status_code == 422
    assert store.list_approvals("project-001") == []


@pytest.mark.parametrize("outcome", ["REJECTED", "RETURNED"])
def test_negative_decisions_do_not_require_judge(workspace, outcome):
    client, store, _ = workspace
    extra = {"return_to_thread": "VOCAL"} if outcome == "RETURNED" else {}
    response = client.post(
        "/workspace/projects/project-001/approve",
        json=_approval(outcome=outcome, **extra),
    )
    assert response.status_code == 201
    assert store.get_version(
        "project-001", "version-001"
    ).status.value == "REJECTED"


def test_returned_decision_requires_return_thread(workspace):
    client, _, _ = workspace
    response = client.post(
        "/workspace/projects/project-001/approve",
        json=_approval(outcome="RETURNED"),
    )
    assert response.status_code == 422


def test_duplicate_decision_is_rejected_without_extra_log_row(workspace):
    client, store, _ = workspace
    _passed_judge(store)
    assert client.post(
        "/workspace/projects/project-001/approve", json=_approval()
    ).status_code == 201
    assert client.post(
        "/workspace/projects/project-001/approve", json=_approval()
    ).status_code == 409
    assert len(store.list_approvals("project-001")) == 1


def test_superseded_decision_must_exist_for_same_version(workspace):
    client, _, _ = workspace
    response = client.post(
        "/workspace/projects/project-001/approve",
        json=_approval(
            outcome="REJECTED",
            supersedes_decision_id="missing-decision",
        ),
    )
    assert response.status_code == 409


def test_missing_project_or_version_returns_404(workspace):
    client, _, _ = workspace
    assert client.post(
        "/workspace/projects/missing/approve", json=_approval()
    ).status_code == 404
    assert client.post(
        "/workspace/projects/project-001/approve",
        json=_approval(version_id="missing"),
    ).status_code == 404


def test_approval_request_rejects_unknown_fields(workspace):
    client, _, _ = workspace
    response = client.post(
        "/workspace/projects/project-001/approve",
        json={**_approval(), "unknown": True},
    )
    assert response.status_code == 422


def test_router_exposes_approval_contract():
    assert "/workspace/projects/{project_id}/approve" in {
        route.path for route in app.routes
    }
