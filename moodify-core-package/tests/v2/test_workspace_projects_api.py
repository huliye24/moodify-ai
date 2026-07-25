from fastapi import FastAPI
from fastapi.testclient import TestClient
import pytest

from moodify.api.routes.workspace_projects import router


app = FastAPI()
app.include_router(router)


@pytest.fixture()
def client(tmp_path, monkeypatch):
    monkeypatch.setenv("MOODIFY_WORKSPACE_ROOT", str(tmp_path))
    return TestClient(app)


def _payload(project_id="project-001"):
    return {
        "project_id": project_id,
        "title": "验收歌曲",
        "source_audio_ids": ["source-001"],
        "privacy_policy": {"retain_days": 30},
    }


def _brief():
    return {
        "goal": "温暖自然",
        "platform": "streaming",
        "preserve": ["自然动态"],
        "avoid": ["过度压缩"],
        "reference": ["reference-001"],
    }


def test_create_project_returns_201_and_contract(client):
    response = client.post("/workspace/projects", json=_payload())

    assert response.status_code == 201
    body = response.json()
    assert body["project_id"] == "project-001"
    assert body["status"] == "CREATED"
    assert body["schema_version"] == "audio_project.v1"


def test_get_project_returns_persisted_snapshot(client):
    client.post("/workspace/projects", json=_payload())

    response = client.get("/workspace/projects/project-001")

    assert response.status_code == 200
    assert response.json()["title"] == "验收歌曲"


def test_patch_project_updates_allowed_fields(client):
    client.post("/workspace/projects", json=_payload())

    response = client.patch(
        "/workspace/projects/project-001",
        json={"title": "新版标题", "status": "BRIEFING"},
    )

    assert response.status_code == 200
    assert response.json()["title"] == "新版标题"
    assert response.json()["status"] == "BRIEFING"


def test_patch_creative_brief_is_validated(client):
    client.post("/workspace/projects", json=_payload())
    response = client.patch(
        "/workspace/projects/project-001",
        json={
            "creative_brief": {
                "goal": "温暖自然",
                "platform": "streaming",
                "preserve": ["自然动态"],
                "avoid": ["过度压缩"],
            }
        },
    )

    assert response.status_code == 200
    assert response.json()["creative_brief"]["goal"] == "温暖自然"


def test_duplicate_project_returns_409(client):
    assert client.post("/workspace/projects", json=_payload()).status_code == 201
    response = client.post("/workspace/projects", json=_payload())
    assert response.status_code == 409


def test_missing_project_returns_404(client):
    assert client.get("/workspace/projects/missing").status_code == 404
    assert (
        client.patch("/workspace/projects/missing", json={"title": "x"}).status_code
        == 404
    )


def test_create_rejects_unknown_or_invalid_fields(client):
    invalid = {**_payload(), "unknown": True}
    assert client.post("/workspace/projects", json=invalid).status_code == 422

    invalid = {**_payload(), "source_audio_ids": []}
    assert client.post("/workspace/projects", json=invalid).status_code == 422


def test_patch_rejects_empty_body_and_unknown_fields(client):
    client.post("/workspace/projects", json=_payload())
    assert client.patch("/workspace/projects/project-001", json={}).status_code == 422
    assert (
        client.patch(
            "/workspace/projects/project-001", json={"project_id": "changed"}
        ).status_code
        == 422
    )


def test_path_traversal_identifier_returns_400(client):
    response = client.post(
        "/workspace/projects",
        json=_payload("../escape"),
    )
    assert response.status_code == 400


def test_router_exposes_only_new_workspace_contract(client):
    paths = {route.path for route in app.routes}
    assert "/workspace/projects" in paths
    assert "/workspace/projects/{project_id}" in paths
    assert all(not path.startswith("/studio/projects") for path in paths)


def test_create_brief_returns_201_and_persists(client):
    client.post("/workspace/projects", json=_payload())
    response = client.post("/workspace/projects/project-001/brief", json=_brief())

    assert response.status_code == 201
    assert response.json()["schema_version"] == "creative_brief.v1"
    project = client.get("/workspace/projects/project-001").json()
    assert project["creative_brief"]["goal"] == "温暖自然"


def test_create_brief_rejects_duplicate(client):
    client.post("/workspace/projects", json=_payload())
    assert client.post(
        "/workspace/projects/project-001/brief", json=_brief()
    ).status_code == 201
    assert client.post(
        "/workspace/projects/project-001/brief", json=_brief()
    ).status_code == 409


def test_patch_brief_is_partial_and_preserves_omitted_fields(client):
    client.post("/workspace/projects", json=_payload())
    client.post("/workspace/projects/project-001/brief", json=_brief())

    response = client.patch(
        "/workspace/projects/project-001/brief",
        json={"goal": "更宽阔、更自然"},
    )

    assert response.status_code == 200
    assert response.json()["goal"] == "更宽阔、更自然"
    assert response.json()["preserve"] == ["自然动态"]


def test_patch_brief_revalidates_cross_field_rules(client):
    client.post("/workspace/projects", json=_payload())
    client.post("/workspace/projects/project-001/brief", json=_brief())

    response = client.patch(
        "/workspace/projects/project-001/brief",
        json={"avoid": ["自然动态"]},
    )

    assert response.status_code == 422
    persisted = client.get("/workspace/projects/project-001").json()
    assert persisted["creative_brief"]["avoid"] == ["过度压缩"]


def test_patch_brief_requires_existing_brief(client):
    client.post("/workspace/projects", json=_payload())
    response = client.patch(
        "/workspace/projects/project-001/brief", json={"goal": "新目标"}
    )
    assert response.status_code == 409


@pytest.mark.parametrize("method", ["post", "patch"])
def test_brief_api_returns_404_for_missing_project(client, method):
    response = getattr(client, method)(
        "/workspace/projects/missing/brief", json=_brief()
    )
    assert response.status_code == 404


@pytest.mark.parametrize("payload", [{}, {"goal": None}, {"unknown": True}])
def test_patch_brief_rejects_empty_null_and_unknown_fields(client, payload):
    client.post("/workspace/projects", json=_payload())
    client.post("/workspace/projects/project-001/brief", json=_brief())
    response = client.patch("/workspace/projects/project-001/brief", json=payload)
    assert response.status_code == 422
