from fastapi import FastAPI
from fastapi.testclient import TestClient
import pytest

from moodify.api.routes.workspace_projects import router


app = FastAPI()
app.include_router(router)
SHA_A = "a" * 64
SHA_B = "b" * 64


@pytest.fixture()
def workspace(tmp_path, monkeypatch):
    monkeypatch.setenv("MOODIFY_WORKSPACE_ROOT", str(tmp_path))
    client = TestClient(app)
    assert client.post(
        "/workspace/projects",
        json={
            "project_id": "project-001",
            "title": "版本接口测试",
            "source_audio_ids": ["source-001"],
        },
    ).status_code == 201
    versions = tmp_path / "projects" / "project-001" / "versions"
    versions.mkdir(parents=True)
    (versions / "root.wav").write_bytes(b"root")
    (versions / "branch.wav").write_bytes(b"branch")
    return client, tmp_path


def _create_payload(version_id="version-001"):
    return {
        "version_id": version_id,
        "branch": "main",
        "name": "Original",
        "purpose": "baseline",
        "audio_path": "versions/root.wav",
        "audio_sha256": SHA_A,
        "created_by": "user",
    }


def _branch_payload(version_id="version-002"):
    return {
        "version_id": version_id,
        "branch": "warm",
        "name": "Warm branch",
        "purpose": "candidate",
        "audio_path": "versions/branch.wav",
        "audio_sha256": SHA_B,
        "created_by": "worker",
    }


def test_create_version_returns_201_and_activates_project(workspace):
    client, _ = workspace
    response = client.post(
        "/workspace/projects/project-001/versions", json=_create_payload()
    )

    assert response.status_code == 201
    assert response.json()["status"] == "DRAFT"
    project = client.get("/workspace/projects/project-001").json()
    assert project["active_version_id"] == "version-001"


def test_version_audio_endpoint_serves_immutable_audio(workspace):
    client, _ = workspace
    assert client.post(
        "/workspace/projects/project-001/versions", json=_create_payload()
    ).status_code == 201
    response = client.get(
        "/workspace/projects/project-001/versions/version-001/audio"
    )
    assert response.status_code == 200
    assert response.content == b"root"
    assert response.headers["content-type"].startswith("audio/wav")


def test_create_version_requires_existing_audio_file(workspace):
    client, _ = workspace
    payload = {**_create_payload(), "audio_path": "versions/missing.wav"}
    assert client.post(
        "/workspace/projects/project-001/versions", json=payload
    ).status_code == 404


def test_create_version_rejects_missing_parent(workspace):
    client, _ = workspace
    payload = {**_create_payload(), "parent_version_id": "missing"}
    assert client.post(
        "/workspace/projects/project-001/versions", json=payload
    ).status_code == 404


def test_list_and_get_versions_return_stable_contract(workspace):
    client, _ = workspace
    client.post(
        "/workspace/projects/project-001/versions", json=_create_payload()
    )
    response = client.get("/workspace/projects/project-001/versions")

    assert response.status_code == 200
    assert [row["version_id"] for row in response.json()] == ["version-001"]
    detail = client.get(
        "/workspace/projects/project-001/versions/version-001"
    )
    assert detail.status_code == 200
    assert detail.json()["schema_version"] == "audio_version.v1"


def test_list_versions_returns_empty_collection(workspace):
    client, _ = workspace
    assert client.get("/workspace/projects/project-001/versions").json() == []


def test_branch_creates_child_without_overwriting_parent(workspace):
    client, _ = workspace
    client.post(
        "/workspace/projects/project-001/versions", json=_create_payload()
    )
    response = client.post(
        "/workspace/projects/project-001/versions/version-001/branch",
        json=_branch_payload(),
    )

    assert response.status_code == 201
    assert response.json()["parent_version_id"] == "version-001"
    parent = client.get(
        "/workspace/projects/project-001/versions/version-001"
    ).json()
    assert parent["audio_path"] == "versions/root.wav"


def test_duplicate_version_is_rejected(workspace):
    client, _ = workspace
    assert client.post(
        "/workspace/projects/project-001/versions", json=_create_payload()
    ).status_code == 201
    assert client.post(
        "/workspace/projects/project-001/versions", json=_create_payload()
    ).status_code == 409


def test_rollback_creates_new_child_with_target_audio(workspace):
    client, _ = workspace
    client.post(
        "/workspace/projects/project-001/versions", json=_create_payload()
    )
    client.post(
        "/workspace/projects/project-001/versions/version-001/branch",
        json=_branch_payload(),
    )

    response = client.post(
        "/workspace/projects/project-001/versions/version-001/rollback",
        json={
            "version_id": "version-003",
            "branch": "main",
            "name": "Rollback to original",
            "purpose": "restore prior sound",
            "created_by": "user",
        },
    )

    assert response.status_code == 201
    body = response.json()
    assert body["version_id"] == "version-003"
    assert body["parent_version_id"] == "version-002"
    assert body["audio_path"] == "versions/root.wav"
    assert client.get(
        "/workspace/projects/project-001/versions/version-002"
    ).status_code == 200


def test_version_inputs_are_strictly_validated(workspace):
    client, _ = workspace
    invalid = {**_create_payload(), "audio_sha256": "bad", "unknown": True}
    assert client.post(
        "/workspace/projects/project-001/versions", json=invalid
    ).status_code == 422


def test_version_routes_return_404_for_missing_resources(workspace):
    client, _ = workspace
    assert client.get("/workspace/projects/missing/versions").status_code == 404
    assert client.get(
        "/workspace/projects/project-001/versions/missing"
    ).status_code == 404
    assert client.post(
        "/workspace/projects/project-001/versions/missing/branch",
        json=_branch_payload(),
    ).status_code == 404


def test_list_detects_a_cycle_in_persisted_version_tree(workspace):
    client, root = workspace
    client.post(
        "/workspace/projects/project-001/versions", json=_create_payload()
    )
    path = root / "projects" / "project-001" / "versions" / "version-001.json"
    payload = path.read_text(encoding="utf-8")
    path.write_text(
        payload.replace('"parent_version_id": null', '"parent_version_id": "version-001"'),
        encoding="utf-8",
    )

    assert client.get("/workspace/projects/project-001/versions").status_code == 500


def test_router_exposes_version_contracts():
    paths = {route.path for route in app.routes}
    assert "/workspace/projects/{project_id}/versions" in paths
    assert "/workspace/projects/{project_id}/versions/{version_id}" in paths
    assert (
        "/workspace/projects/{project_id}/versions/{parent_version_id}/branch"
        in paths
    )
    assert (
        "/workspace/projects/{project_id}/versions/{target_version_id}/rollback"
        in paths
    )
