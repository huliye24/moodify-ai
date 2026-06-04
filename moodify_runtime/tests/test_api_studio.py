"""MHP-043: API tests — Studio Back Office endpoints (/studio/*)."""

import json
import os

from fastapi.testclient import TestClient


def _cfg_path(tmp_path):
    d = {
        "project_root": str(tmp_path),
        "output_root": "outputs",
        "report_dir": "reports",
        "operator_jobs_path": "operator_jobs.jsonl",
        "operator_detail_dir": "operator_details",
        "operator_deliveries_path": "operator_deliveries.jsonl",
        "operator_report_dir": "reports/operator_runs",
        "studio_data_dir": "studio",
        "scheduler_data_dir": "scheduler",
        "calibration_data_dir": "calibration",
        "craft_memory_dir": "craft_memory",
        "data_root": "data",
        "input_dirs": ["input"],
        "registry_path": "registry.jsonl",
        "queue_path": "queue.jsonl",
    }
    p = tmp_path / "runtime_config.json"
    p.write_text(json.dumps(d), encoding="utf-8")
    return str(p)


def _api_client(tmp_path):
    cfg = _cfg_path(tmp_path)
    os.environ["MOODIFY_RUNTIME_CONFIG"] = cfg
    from moodify_runtime.operator_api import app
    return TestClient(app)


# ── Clients ─────────────────────────────────────────────────────────


def test_create_and_list_clients(tmp_path):
    client = _api_client(tmp_path)

    r = client.post("/studio/clients", params={
        "name": "Test Studio", "contact": "test@studio.com", "notes": "priority",
    })
    assert r.status_code == 200
    data = r.json()
    assert data["client_id"].startswith("CLI_")
    assert data["name"] == "Test Studio"

    r = client.get("/studio/clients")
    assert r.status_code == 200
    assert len(r.json()["clients"]) == 1


def test_list_clients_empty(tmp_path):
    client = _api_client(tmp_path)
    r = client.get("/studio/clients")
    assert r.status_code == 200
    assert r.json()["clients"] == []


# ── Projects ────────────────────────────────────────────────────────


def test_create_and_list_projects(tmp_path):
    client = _api_client(tmp_path)

    cr = client.post("/studio/clients", params={"name": "Client A"})
    client_id = cr.json()["client_id"]

    r = client.post("/studio/projects", params={
        "client_id": client_id, "name": "Album Mastering", "description": "12 tracks",
    })
    assert r.status_code == 200
    assert r.json()["project_id"].startswith("PRJ_")

    r = client.get("/studio/projects")
    assert r.status_code == 200
    assert len(r.json()["projects"]) == 1

    r = client.get("/studio/projects", params={"client_id": client_id})
    assert r.status_code == 200
    assert len(r.json()["projects"]) == 1

    r = client.get("/studio/projects", params={"client_id": "OTHER"})
    assert r.status_code == 200
    assert r.json()["projects"] == []


# ── Orders ──────────────────────────────────────────────────────────


def test_create_and_list_orders(tmp_path):
    client = _api_client(tmp_path)

    cr = client.post("/studio/clients", params={"name": "Client O"})
    cid = cr.json()["client_id"]
    pr = client.post("/studio/projects", params={"client_id": cid, "name": "Project O"})
    pid = pr.json()["project_id"]

    r = client.post("/studio/orders", params={
        "project_id": pid, "client_id": cid, "description": "Master 3 tracks",
        "priority": 3,
    })
    assert r.status_code == 200
    data = r.json()
    assert data["order_id"].startswith("ORD_")
    assert data["status"] == "pending"

    r = client.get("/studio/orders")
    assert r.status_code == 200
    assert len(r.json()["orders"]) == 1


def test_order_link_and_context(tmp_path):
    client = _api_client(tmp_path)

    cr = client.post("/studio/clients", params={"name": "Client L"})
    cid = cr.json()["client_id"]
    pr = client.post("/studio/projects", params={"client_id": cid, "name": "Project L"})
    pid = pr.json()["project_id"]
    orr = client.post("/studio/orders", params={"project_id": pid, "client_id": cid, "description": "Link test"})
    oid = orr.json()["order_id"]

    jr = client.post("/operator/jobs", params={"source_audio": "input/s.wav", "processing_depth": "quick_scan"})
    jid = jr.json()["job_id"]

    # Link job
    r = client.post(f"/studio/orders/{oid}/link-job", params={"job_id": jid})
    assert r.status_code == 200
    linked = r.json()
    assert jid in linked["linked_job_ids"]

    # Context
    r = client.get(f"/studio/orders/{oid}/context")
    assert r.status_code == 200
    ctx = r.json()
    assert ctx["order"]["order_id"] == oid
    assert len(ctx["linked_jobs"]) == 1

    # Not found
    r = client.get("/studio/orders/FAKE/context")
    assert r.status_code == 404


# ── Notes ───────────────────────────────────────────────────────────


def test_create_and_list_notes(tmp_path):
    client = _api_client(tmp_path)
    cr = client.post("/studio/clients", params={"name": "Client N"})
    cid = cr.json()["client_id"]

    r = client.post("/studio/notes", params={
        "target_type": "client",
        "target_id": cid,
        "content": "Priority client — handle with care",
        "author": "operator",
    })
    assert r.status_code == 200
    assert r.json()["note_id"].startswith("NOTE_")

    r = client.get("/studio/notes")
    assert r.status_code == 200
    assert len(r.json()["notes"]) == 1

    r = client.get("/studio/notes", params={"target_type": "client", "target_id": cid})
    assert r.status_code == 200
    assert len(r.json()["notes"]) == 1
