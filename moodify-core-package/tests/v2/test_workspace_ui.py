"""Workspace v2 UI contract tests for steps 25-29."""

from fastapi import FastAPI
from fastapi.testclient import TestClient

from moodify.api.routes.workspace_projects import router


def _client() -> TestClient:
    app = FastAPI()
    app.include_router(router)
    return TestClient(app)


def test_workspace_ui_is_served_with_three_panel_layout():
    response = _client().get("/workspace/projects/ui")
    assert response.status_code == 200
    html = response.text
    assert 'id="thread-panel"' in html
    assert 'id="tab-brief"' in html
    assert 'id="tab-versions"' in html
    assert 'id="approval-panel"' in html


def test_workspace_ui_loads_real_project_threads_and_versions_apis():
    html = _client().get("/workspace/projects/ui").text
    assert "loadProject()" in html
    assert "loadThreads()" in html
    assert "loadVersions()" in html
    assert "loadApprovals()" in html
    assert "`${API}/${currentProjectId}/threads`" in html
    assert "`${API}/${currentProjectId}/versions`" in html


def test_workspace_ui_supports_version_selection_and_comparison():
    html = _client().get("/workspace/projects/ui").text
    assert "selectVersion(" in html
    assert "pickSlot('A')" in html
    assert "pickSlot('B')" in html
    assert "compareVersions()" in html
    assert "/compare/${selectedVersionB}" in html
    assert "<audio controls" in html
    assert "/versions/${v.version_id}/audio" in html


def test_workspace_ui_exposes_human_approval_actions():
    html = _client().get("/workspace/projects/ui").text
    assert "submitApproval(" in html
    assert "APPROVED" in html
    assert "REJECTED" in html
    assert "RETURNED" in html
    assert "actor_type: 'HUMAN'" in html
