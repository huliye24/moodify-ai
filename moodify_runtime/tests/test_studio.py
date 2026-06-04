"""Tests for studio — client/project/order CRUD, staff notes."""
import tempfile
from pathlib import Path

import pytest

from moodify_runtime.studio import (
    create_client, list_clients,
    create_project, list_projects, get_project,
    create_order, list_orders, get_order,
    create_staff_note, list_staff_notes,
    _new_studio_id,
)
from moodify_runtime.config import RuntimeConfig


@pytest.fixture
def cfg():
    d = tempfile.mkdtemp()
    c = RuntimeConfig(project_root=Path(d), studio_data_dir=Path(d) / "studio")
    c.studio_data_dir.mkdir(parents=True, exist_ok=True)
    return c


class TestIdGeneration:
    def test_new_studio_ids_unique(self):
        ids = {_new_studio_id("client") for _ in range(50)}
        assert len(ids) == 50

    def test_new_studio_id_non_empty(self):
        assert _new_studio_id("project")
        assert len(_new_studio_id("order")) > 0


class TestClientCRUD:
    def test_create_and_list(self, cfg):
        c = create_client(cfg, "Test Studio", contact="t@t.com", notes="ok")
        assert c["name"] == "Test Studio"
        assert "client_id" in c
        assert any(cl["name"] == "Test Studio" for cl in list_clients(cfg))

    def test_multiple_clients(self, cfg):
        create_client(cfg, "A"); create_client(cfg, "B"); create_client(cfg, "C")
        assert len(list_clients(cfg)) >= 3


class TestProjectCRUD:
    def test_create_and_get(self, cfg):
        client = create_client(cfg, "Owner")
        proj = create_project(cfg, client["client_id"], "Album", "Desc")
        assert proj["name"] == "Album"
        assert "project_id" in proj
        fetched = get_project(cfg, proj["project_id"])
        assert fetched["name"] == "Album"

    def test_list_filtered(self, cfg):
        c1 = create_client(cfg, "C1"); c2 = create_client(cfg, "C2")
        create_project(cfg, c1["client_id"], "P1")
        create_project(cfg, c1["client_id"], "P2")
        create_project(cfg, c2["client_id"], "P3")
        assert len(list_projects(cfg, client_id=c1["client_id"])) == 2

    def test_list_all(self, cfg):
        client = create_client(cfg, "Owner")
        create_project(cfg, client["client_id"], "A")
        create_project(cfg, client["client_id"], "B")
        assert len(list_projects(cfg)) == 2


class TestOrderCRUD:
    def test_create_order(self, cfg):
        client = create_client(cfg, "Ord")
        proj = create_project(cfg, client["client_id"], "Single")
        order = create_order(cfg, proj["project_id"], client["client_id"],
                             "Mastering order")
        assert order["description"] == "Mastering order"
        assert order["status"] == "pending"

    def test_list_filtered(self, cfg):
        client = create_client(cfg, "M")
        proj = create_project(cfg, client["client_id"], "Many")
        create_order(cfg, proj["project_id"], client["client_id"], "O1")
        create_order(cfg, proj["project_id"], client["client_id"], "O2")
        assert len(list_orders(cfg, project_id=proj["project_id"])) == 2

    def test_get_order(self, cfg):
        client = create_client(cfg, "G")
        proj = create_project(cfg, client["client_id"], "Get")
        o = create_order(cfg, proj["project_id"], client["client_id"], "Target")
        assert get_order(cfg, o["order_id"])["description"] == "Target"


class TestStaffNotes:
    def test_create_and_list(self, cfg):
        note = create_staff_note(cfg, "order", "ORD-001",
                                 "Review needed", author="op")
        assert note["content"] == "Review needed"
        notes = list_staff_notes(cfg, target_type="order", target_id="ORD-001")
        assert len(notes) >= 1

    def test_filtered(self, cfg):
        create_staff_note(cfg, "client", "CL-A", "A")
        create_staff_note(cfg, "order", "CL-A", "B")
        assert len(list_staff_notes(cfg, target_type="client")) >= 1
