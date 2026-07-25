from datetime import datetime, timedelta, timezone

from fastapi import FastAPI
from fastapi.testclient import TestClient
import pytest

from moodify.api.routes.workspace_projects import router
from moodify.domain import (
    AudioProject,
    ProjectThread,
    ThreadRole,
    ThreadType,
)
from moodify.storage import WorkspaceStore


app = FastAPI()
app.include_router(router)
BASE_TIME = datetime(2026, 7, 25, 8, 0, tzinfo=timezone.utc)


@pytest.fixture()
def workspace(tmp_path, monkeypatch):
    monkeypatch.setenv("MOODIFY_WORKSPACE_ROOT", str(tmp_path))
    store = WorkspaceStore(tmp_path)
    store.create_project(
        AudioProject(
            project_id="project-001",
            title="线程查询测试",
            source_audio_ids=["source-001"],
            created_at=BASE_TIME,
            updated_at=BASE_TIME,
        )
    )
    return TestClient(app), store, tmp_path


def _thread(
    thread_id: str,
    created_offset: int,
    thread_type: ThreadType = ThreadType.DESIGN,
) -> ProjectThread:
    created_at = BASE_TIME + timedelta(seconds=created_offset)
    role = {
        ThreadType.BRIEF: ThreadRole.PRODUCER,
        ThreadType.DIAGNOSIS: ThreadRole.ANALYST,
        ThreadType.DESIGN: ThreadRole.DESIGNER,
    }[thread_type]
    return ProjectThread(
        thread_id=thread_id,
        project_id="project-001",
        thread_type=thread_type,
        role=role,
        created_at=created_at,
        updated_at=created_at,
    )


def test_list_threads_returns_empty_collection(workspace):
    client, _, _ = workspace
    response = client.get("/workspace/projects/project-001/threads")

    assert response.status_code == 200
    assert response.json() == []


def test_list_threads_follows_workflow_then_created_at_and_id(workspace):
    client, store, _ = workspace
    store.create_thread(_thread("design", 0, ThreadType.DESIGN))
    store.create_thread(_thread("brief-b", 1, ThreadType.BRIEF))
    store.create_thread(_thread("diagnosis", 0, ThreadType.DIAGNOSIS))
    store.create_thread(_thread("brief-a", 1, ThreadType.BRIEF))

    response = client.get("/workspace/projects/project-001/threads")

    assert response.status_code == 200
    assert [row["thread_id"] for row in response.json()] == [
        "brief-a",
        "brief-b",
        "diagnosis",
        "design",
    ]


def test_list_threads_returns_full_domain_contract(workspace):
    client, store, _ = workspace
    store.create_thread(_thread("thread-001", 0))

    body = client.get("/workspace/projects/project-001/threads").json()[0]

    assert body["schema_version"] == "project_thread.v1"
    assert body["thread_type"] == "DESIGN"
    assert body["role"] == "DESIGNER"
    assert body["status"] == "PLANNED"


def test_list_threads_returns_404_for_missing_project(workspace):
    client, _, _ = workspace
    assert client.get("/workspace/projects/missing/threads").status_code == 404


def test_list_threads_rejects_unsafe_project_id(workspace):
    client, _, _ = workspace
    assert client.get("/workspace/projects/bad$id/threads").status_code == 400


def test_list_threads_reports_corrupt_snapshot(workspace):
    client, store, root = workspace
    store.create_thread(_thread("thread-001", 0))
    path = root / "projects" / "project-001" / "threads" / "thread-001.json"
    path.write_text("{broken", encoding="utf-8")

    response = client.get("/workspace/projects/project-001/threads")

    assert response.status_code == 500
    assert response.json()["detail"] == "workspace data is corrupt"


def test_router_exposes_thread_collection_contract():
    assert "/workspace/projects/{project_id}/threads" in {
        route.path for route in app.routes
    }
