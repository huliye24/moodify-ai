"""Pairwise judge API contract tests."""
from __future__ import annotations

from unittest.mock import patch

from fastapi.testclient import TestClient

from moodify.api.main import app


def _fake_judge(case_id, case_root, candidate_a_path, candidate_b_path, policy):
    return {
        "judgment_id": "jud-api-1",
        "outcome": "A_WINS",
        "confidence_level": "HIGH",
        "winner_margin": 0.65,
        "evidence_coverage": 0.85,
        "top_reasons": ["WINNER_MARGIN=0.650"],
        "analysis_failed": [],
        "judgment_dir": "SHOULD_NOT_LEAK",
    }


def test_judgment_requires_b_candidate() -> None:
    client = TestClient(app)
    response = client.post(
        "/api/v1/pairwise-judgments",
        json={"candidate_a_upload_id": "up-a"},
    )
    assert response.status_code == 400
    assert response.json()["error"]["code"] == "VALIDATION"


def test_judgment_unknown_asset() -> None:
    client = TestClient(app)
    response = client.post(
        "/api/v1/pairwise-judgments",
        json={"candidate_a_upload_id": "up-missing", "candidate_b_upload_id": "up-b"},
    )
    assert response.status_code == 404


def test_judgment_contract_and_no_path_leak() -> None:
    client = TestClient(app)
    with (
        patch("moodify.api.routes.pairwise_judge._resolve_audio",
              return_value=__import__("pathlib").Path("fake.wav")),
        patch("moodify.api.routes.pairwise_judge.run_pairwise_judge",
              side_effect=_fake_judge),
    ):
        response = client.post(
            "/api/v1/pairwise-judgments",
            json={"candidate_a_upload_id": "up-a", "candidate_b_upload_id": "up-b"},
        )
    assert response.status_code == 200
    body = response.json()
    assert body["outcome"] == "A_WINS"
    assert body["confidence_level"] == "HIGH"
    assert "judgment_dir" not in body


def test_human_decision_validation() -> None:
    client = TestClient(app)
    response = client.post(
        "/api/v1/pairwise-judgments/jud-x/human-decision",
        json={"decision": "NONSENSE"},
    )
    assert response.status_code == 400
    assert response.json()["error"]["code"] == "VALIDATION"


def test_human_decision_missing_judgment() -> None:
    client = TestClient(app)
    with patch("moodify.api.routes.pairwise_judge._case_root",
               return_value=__import__("pathlib").Path("missing")):
        response = client.post(
            "/api/v1/pairwise-judgments/jud-missing/human-decision",
            json={"decision": "CHOOSE_A"},
        )
    assert response.status_code == 404
