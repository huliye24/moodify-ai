"""N-track API contract and CLI registration tests."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from unittest.mock import patch

from fastapi.testclient import TestClient

from moodify.api.main import app
from moodify.cli_v2.main import cmd_case_ntrack_rank

FAKE_RANKING = {
    "ranking_case_id": "RK-api-1",
    "mode": "TRACK_STRENGTH",
    "top_k": 3,
    "status": "COMPLETED",
    "eligible_count": 5,
    "failed_count": 0,
    "rejected_ids": [],
    "review_required_ids": [],
    "pairwise_edge_count": 10,
    "ranking_estimate_id": "est-api-1",
    "ranking": [{"candidate_id": f"c{i}", "rank": i, "confidence": "HIGH",
                 "top_k_membership": i <= 3} for i in range(1, 6)],
    "tie_bands": [],
    "ranking_dir": "SHOULD_NOT_LEAK",
}


def test_ranking_requires_two_tracks() -> None:
    client = TestClient(app)
    response = client.post("/api/v1/rankings", json={"track_upload_ids": ["up-a"]})
    assert response.status_code == 400
    assert response.json()["error"]["code"] == "VALIDATION"


def test_ranking_unknown_asset() -> None:
    client = TestClient(app)
    response = client.post(
        "/api/v1/rankings",
        json={"track_upload_ids": ["up-missing", "up-b"]},
    )
    assert response.status_code == 404


def test_ranking_contract_and_no_path_leak() -> None:
    client = TestClient(app)
    with (
        patch("moodify.api.routes.ntrack_ranking._resolve_upload",
              return_value=Path("fake.wav")),
        patch("moodify.api.routes.ntrack_ranking.run_ntrack_ranking",
              return_value=FAKE_RANKING),
    ):
        response = client.post(
            "/api/v1/rankings",
            json={"track_upload_ids": ["up-a", "up-b"], "mode": "TRACK_STRENGTH", "top_k": 3},
        )
    assert response.status_code == 200
    body = response.json()
    assert "ranking_dir" not in body
    assert body["ranking_case_id"] == "RK-api-1"
    assert body["ranking"][0]["rank"] == 1


def test_ranking_get_not_found() -> None:
    client = TestClient(app)
    response = client.get("/api/v1/rankings/RK-missing")
    assert response.status_code == 404


def _project(tmp_path: Path) -> Path:
    project = tmp_path / "project"
    project.mkdir()
    valid = {"schema_version": "1.0.0", "title": "t", "project_id": "p-1",
             "assets": {}, "plans": {}, "runs": {}}
    (project / "project.json").write_text(json.dumps(valid), encoding="utf-8")
    (project / "cases" / "RK-1").mkdir(parents=True)
    return project


def test_ntrack_rank_registered(tmp_path: Path) -> None:
    project = _project(tmp_path)
    tracks = [tmp_path / f"t{i}.wav" for i in range(3)]
    for t in tracks:
        t.write_bytes(b"RIFF-x")
    args = argparse.Namespace(project_dir=str(project), case_id="RK-1",
                              tracks=[str(t) for t in tracks],
                              mode="TRACK_STRENGTH", top_k=None, config=None)
    with patch("moodify.evaluation.ntrack.service.run_ntrack_ranking") as mock:
        mock.return_value = {
            "mode": "TRACK_STRENGTH", "eligible_count": 3, "failed_count": 0,
            "pairwise_edge_count": 3,
            "ranking": [{"candidate_id": f"c{i}", "rank": i} for i in range(1, 4)],
            "tie_bands": [], "ranking_estimate_id": "est-1", "ranking_dir": "x",
        }
        result = cmd_case_ntrack_rank(args)
    assert result["command"] == "case.ntrack-rank"
    assert result["result_status"] == "NTRACK_RANKING_COMPLETED"
    assert result["eligible_count"] == 3
