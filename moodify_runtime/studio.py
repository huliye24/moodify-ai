"""MHP-036: Studio Back Office — commercial workflow layer.

Durable objects: StudioClient, StudioProject, Order, ProcessingPackage, StaffNote.
JSONL-backed storage with API endpoints.
"""

from __future__ import annotations

import uuid

from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Any, Dict, List, Optional

from .config import RuntimeConfig
from .utils import append_jsonl, read_jsonl, atomic_write_jsonl, utc_now_iso


# ── Data Models ───────────────────────────────────────────────────


@dataclass(frozen=True)
class StudioClient:
    client_id: str
    name: str
    contact: str = ""
    notes: str = ""
    created_at: str = field(default_factory=utc_now_iso)
    updated_at: str = field(default_factory=utc_now_iso)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class StudioProject:
    project_id: str
    client_id: str
    name: str
    description: str = ""
    status: str = "active"  # active, completed, on_hold
    created_at: str = field(default_factory=utc_now_iso)
    updated_at: str = field(default_factory=utc_now_iso)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class Order:
    order_id: str
    project_id: str
    client_id: str
    description: str = ""
    processing_package: str = "standard"
    deadline: str = ""
    priority: int = 5
    status: str = "pending"  # pending, in_progress, completed, delivered
    created_at: str = field(default_factory=utc_now_iso)
    updated_at: str = field(default_factory=utc_now_iso)
    linked_job_ids: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        return d


@dataclass(frozen=True)
class ProcessingPackage:
    package_id: str
    name: str
    description: str = ""
    processing_depth: str = "standard_process"
    presets: List[str] = field(default_factory=list)
    price_tier: str = ""
    created_at: str = field(default_factory=utc_now_iso)

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        return d


@dataclass(frozen=True)
class StaffNote:
    note_id: str
    target_type: str = ""   # "order", "project", "client"
    target_id: str = ""
    author: str = ""
    content: str = ""
    created_at: str = field(default_factory=utc_now_iso)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


# ── Helpers ────────────────────────────────────────────────────────


def _new_studio_id(prefix: str) -> str:
    return f"{prefix}_{uuid.uuid4().hex[:12].upper()}"


def _studio_path(cfg: RuntimeConfig, entity: str) -> Path:
    cfg = cfg.resolved()
    base = cfg.studio_data_dir
    return base / f"{entity}.jsonl"


def _load_entity(cfg: RuntimeConfig, entity: str) -> List[Dict[str, Any]]:
    return read_jsonl(_studio_path(cfg, entity))


def _save_entity(cfg: RuntimeConfig, entity: str, rows: List[Dict[str, Any]]) -> None:
    atomic_write_jsonl(_studio_path(cfg, entity), rows)


# ── CRUD: Clients ──────────────────────────────────────────────────


def create_client(cfg: RuntimeConfig, name: str, contact: str = "", notes: str = "") -> Dict[str, Any]:
    c = StudioClient(client_id=_new_studio_id("CLI"), name=name, contact=contact, notes=notes)
    append_jsonl(_studio_path(cfg, "clients"), c.to_dict())
    return c.to_dict()


def list_clients(cfg: RuntimeConfig) -> List[Dict[str, Any]]:
    return _load_entity(cfg, "clients")


# ── CRUD: Projects ─────────────────────────────────────────────────


def create_project(cfg: RuntimeConfig, client_id: str, name: str, description: str = "") -> Dict[str, Any]:
    p = StudioProject(project_id=_new_studio_id("PRJ"), client_id=client_id, name=name, description=description)
    append_jsonl(_studio_path(cfg, "projects"), p.to_dict())
    return p.to_dict()


def list_projects(cfg: RuntimeConfig, client_id: Optional[str] = None) -> List[Dict[str, Any]]:
    rows = _load_entity(cfg, "projects")
    if client_id:
        rows = [r for r in rows if r.get("client_id") == client_id]
    return rows


def get_project(cfg: RuntimeConfig, project_id: str) -> Dict[str, Any]:
    for r in _load_entity(cfg, "projects"):
        if r.get("project_id") == project_id:
            return r
    raise KeyError(f"project not found: {project_id}")


# ── CRUD: Orders ───────────────────────────────────────────────────


def create_order(
    cfg: RuntimeConfig,
    project_id: str,
    client_id: str,
    description: str = "",
    processing_package: str = "standard",
    deadline: str = "",
    priority: int = 5,
) -> Dict[str, Any]:
    o = Order(
        order_id=_new_studio_id("ORD"),
        project_id=project_id,
        client_id=client_id,
        description=description,
        processing_package=processing_package,
        deadline=deadline,
        priority=priority,
    )
    append_jsonl(_studio_path(cfg, "orders"), o.to_dict())
    return o.to_dict()


def list_orders(cfg: RuntimeConfig, project_id: Optional[str] = None) -> List[Dict[str, Any]]:
    rows = _load_entity(cfg, "orders")
    if project_id:
        rows = [r for r in rows if r.get("project_id") == project_id]
    return sorted(rows, key=lambda r: (r.get("priority", 5), r.get("created_at", "")))


def get_order(cfg: RuntimeConfig, order_id: str) -> Dict[str, Any]:
    for r in _load_entity(cfg, "orders"):
        if r.get("order_id") == order_id:
            return r
    raise KeyError(f"order not found: {order_id}")


def link_job_to_order(cfg: RuntimeConfig, order_id: str, job_id: str) -> Dict[str, Any]:
    rows = _load_entity(cfg, "orders")
    for r in rows:
        if r.get("order_id") == order_id:
            linked = r.get("linked_job_ids", [])
            if job_id not in linked:
                linked.append(job_id)
                r["linked_job_ids"] = linked
                r["updated_at"] = utc_now_iso()
                if r["status"] == "pending":
                    r["status"] = "in_progress"
            _save_entity(cfg, "orders", rows)
            return r
    raise KeyError(f"order not found: {order_id}")


# ── Staff Notes ────────────────────────────────────────────────────


def create_staff_note(cfg: RuntimeConfig, target_type: str, target_id: str, content: str, author: str = "operator") -> Dict[str, Any]:
    n = StaffNote(note_id=_new_studio_id("NOTE"), target_type=target_type, target_id=target_id, content=content, author=author)
    append_jsonl(_studio_path(cfg, "staff_notes"), n.to_dict())
    return n.to_dict()


def list_staff_notes(cfg: RuntimeConfig, target_type: Optional[str] = None, target_id: Optional[str] = None) -> List[Dict[str, Any]]:
    rows = _load_entity(cfg, "staff_notes")
    if target_type:
        rows = [r for r in rows if r.get("target_type") == target_type]
    if target_id:
        rows = [r for r in rows if r.get("target_id") == target_id]
    return sorted(rows, key=lambda r: r.get("created_at", ""), reverse=True)


# ── Order/Job Context ──────────────────────────────────────────────


def get_order_context(cfg: RuntimeConfig, order_id: str) -> Dict[str, Any]:
    """Return the full context for an order: client, project, order, linked jobs."""
    order = get_order(cfg, order_id)
    try:
        project = get_project(cfg, order["project_id"])
    except KeyError:
        project = {}
    client = {}
    if order.get("client_id"):
        for c in _load_entity(cfg, "clients"):
            if c.get("client_id") == order["client_id"]:
                client = c
                break
    from .operator_console import get_operator_job

    jobs = []
    for jid in order.get("linked_job_ids", []):
        try:
            jobs.append(get_operator_job(cfg, jid))
        except KeyError:
            pass

    return {
        "order": order,
        "project": project,
        "client": client,
        "linked_jobs": jobs,
        "delivery_status": {
            "total": len(jobs),
            "delivered": len([j for j in jobs if j.get("status") == "delivered"]),
            "in_progress": len([j for j in jobs if j.get("status") not in ("delivered", "failed")]),
            "failed": len([j for j in jobs if j.get("status") == "failed"]),
        },
    }
