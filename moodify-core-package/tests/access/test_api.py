"""Open access API contract tests."""

from __future__ import annotations

import os
from pathlib import Path

from fastapi.testclient import TestClient

from moodify.api.main import app


def _client(tmp_path: Path) -> TestClient:
    os.environ["MOODIFY_ACCESS_ROOT"] = str(tmp_path / "access")
    return TestClient(app)


def test_register_open_without_code(tmp_path: Path):
    client = _client(tmp_path)
    response = client.post("/api/v1/auth/register", json={"user_id": "api-u1"})
    assert response.status_code == 200
    body = response.json()
    assert body["registration_mode"] == "OPEN"
    assert body["balance"]["available_cwc"] == 100.0


def test_register_with_referral(tmp_path: Path):
    client = _client(tmp_path)
    client.post("/api/v1/auth/register", json={"user_id": "api-inviter"})
    response = client.post(
        "/api/v1/auth/register",
        json={"user_id": "api-invitee", "referral_code": "api-inviter"},
    )
    assert response.status_code == 200
    assert response.json()["referral"]["state"] == "GRANTED"


def test_register_rejects_extra_fields(tmp_path: Path):
    client = _client(tmp_path)
    response = client.post(
        "/api/v1/auth/register",
        json={"user_id": "u1", "invite_code": "REQUIRED"},  # legacy hard-gate field
    )
    assert response.status_code == 422  # extra="forbid"


def test_balance_and_history(tmp_path: Path):
    client = _client(tmp_path)
    client.post("/api/v1/auth/register", json={"user_id": "api-bal"})
    balance = client.get("/api/v1/cwc/balance", params={"user_id": "api-bal"})
    assert balance.status_code == 200
    assert balance.json()["available_cwc"] == 100.0
    history = client.get("/api/v1/cwc/history", params={"user_id": "api-bal"})
    assert len(history.json()["transactions"]) >= 1


def test_compute_estimate(tmp_path: Path):
    client = _client(tmp_path)
    response = client.post("/api/v1/compute/estimate", json={"operation_type": "pairwise_ab_judge"})
    assert response.status_code == 200
    assert response.json()["estimated_cwc"] == 5.0


def test_compute_estimate_unknown(tmp_path: Path):
    client = _client(tmp_path)
    response = client.post("/api/v1/compute/estimate", json={"operation_type": "nope"})
    assert response.status_code == 400
    assert response.json()["error"]["code"] == "VALIDATION"


def test_compute_admit_flow(tmp_path: Path):
    client = _client(tmp_path)
    client.post("/api/v1/auth/register", json={"user_id": "api-admit"})
    admitted = client.post(
        "/api/v1/compute/admit",
        json={"user_id": "api-admit", "operation_type": "pairwise_ab_judge"},
    )
    assert admitted.status_code == 200
    assert admitted.json()["queue_state"] == "ADMITTED"
    settled = client.post(
        "/api/v1/compute/settle",
        json={"admission_id": admitted.json()["admission_id"], "actual_cwc": 4.0},
    )
    assert settled.json()["queue_state"] == "COMPLETED"


def test_quota_view(tmp_path: Path):
    client = _client(tmp_path)
    client.post("/api/v1/auth/register", json={"user_id": "api-quota"})
    response = client.get("/api/v1/compute/quota", params={"user_id": "api-quota"})
    assert response.status_code == 200
    assert response.json()["concurrency_limit"] == 1
    assert response.json()["available_cwc"] == 100.0
