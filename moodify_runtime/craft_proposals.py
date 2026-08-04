"""Proposal namespace for automated writeback containment.

Automated recommendations from data-loop, feed, and seed paths are isolated in a
``proposals/`` subdirectory. They carry status ``proposal`` and must never be
treated as approved Craft knowledge without an explicit, evidence-bearing
promotion step.

Part of DSK-MFY-AUX-HARDENING-002 Batch A.
"""

from __future__ import annotations

import hashlib
import json
import os
import uuid
from pathlib import Path
from typing import Any

from .utils import utc_now_iso

PROPOSAL_STATUSES = {"proposal", "pending", "promoted", "rejected"}
DEFAULT_PROPOSAL_STATUS = "proposal"

# ── Required fields per proposal schema ────────────────────────────
_REQUIRED_FIELDS = {"proposal_id", "status", "source", "created_at"}

# ── Required fields for promotion evidence ─────────────────────────
_PROMOTION_REQUIRED = {
    "rights_evidence",
    "human_reviewer",
    "review_timestamp",
    "source_run_id",
    "regression_evidence",
}


def _proposals_dir(craft_memory_dir: Path) -> Path:
    return craft_memory_dir / "proposals"


def write_automated_proposal(
    craft_memory_dir: Path,
    source: str,
    source_run_id: str,
    entries: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """Write automated recommendations as isolated proposals.

    Each entry becomes a separate proposal file under
    ``<craft_memory_dir>/proposals/`` with ``status: "proposal"``.

    Returns the list of written proposal records.
    """
    proposals_dir = _proposals_dir(craft_memory_dir)
    proposals_dir.mkdir(parents=True, exist_ok=True)
    now = utc_now_iso()
    written: list[dict[str, Any]] = []

    for entry in entries:
        proposal_id = f"PROP_{uuid.uuid4().hex[:12].upper()}"
        proposal = {
            "proposal_id": proposal_id,
            "schema_version": "1.0.0",
            "status": DEFAULT_PROPOSAL_STATUS,
            "source": source,
            "source_run_id": source_run_id,
            "created_at": now,
            "craft_data": entry,
            "promotion_evidence": None,
        }
        path = proposals_dir / f"proposal_{proposal_id}.json"
        path.write_text(
            json.dumps(proposal, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        written.append(proposal)

    return written


def list_proposals(craft_memory_dir: Path, status: str | None = None) -> list[dict[str, Any]]:
    """List proposals, optionally filtered by status."""
    pdir = _proposals_dir(craft_memory_dir)
    if not pdir.is_dir():
        return []
    proposals: list[dict[str, Any]] = []
    for fpath in sorted(pdir.glob("proposal_*.json")):
        try:
            data = json.loads(fpath.read_text(encoding="utf-8"))
            if status is None or data.get("status") == status:
                proposals.append(data)
        except (OSError, json.JSONDecodeError):
            continue
    return proposals


def get_proposal(craft_memory_dir: Path, proposal_id: str) -> dict[str, Any] | None:
    """Read a single proposal by ID."""
    path = _proposals_dir(craft_memory_dir) / f"proposal_{proposal_id}.json"
    if not path.is_file():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None


def promote_proposal_to_craft(
    craft_memory_dir: Path,
    proposal_id: str,
    promotion_evidence: dict[str, Any],
) -> dict[str, Any]:
    """Promote a proposal to an approved Craft record with evidence.

    Required evidence fields:
      - rights_evidence
      - human_reviewer
      - review_timestamp
      - source_run_id
      - regression_evidence

    Fails closed on missing, malformed, mismatched, or replayed evidence.
    Promotion is idempotent: a proposal already promoted returns its existing
    craft record identity without duplication.

    Returns the promotion result containing the new or existing craft record.
    """
    # ── 1. Validate evidence completeness ──────────────────────────
    missing = _PROMOTION_REQUIRED - set(promotion_evidence.keys())
    if missing:
        raise ValueError(
            f"Promotion evidence missing required fields: {sorted(missing)}"
        )

    for key in _PROMOTION_REQUIRED:
        if promotion_evidence.get(key) in (None, ""):
            raise ValueError(
                f"Promotion evidence field '{key}' must not be empty"
            )
    if not isinstance(promotion_evidence["rights_evidence"], dict) or not promotion_evidence["rights_evidence"]:
        raise ValueError("rights_evidence must be a non-empty object")
    if not isinstance(promotion_evidence["regression_evidence"], (dict, list)) or not promotion_evidence["regression_evidence"]:
        raise ValueError("regression_evidence must be a non-empty object or list")
    for key in ("human_reviewer", "review_timestamp", "source_run_id"):
        if not isinstance(promotion_evidence[key], str) or not promotion_evidence[key].strip():
            raise ValueError(f"Promotion evidence field '{key}' must be a non-empty string")

    # ── 2. Load and validate proposal ──────────────────────────────
    proposal = get_proposal(craft_memory_dir, proposal_id)
    if proposal is None:
        raise ValueError(f"Proposal not found: {proposal_id}")

    for field in _REQUIRED_FIELDS:
        if field not in proposal:
            raise ValueError(
                f"Proposal {proposal_id} is malformed: missing field '{field}'"
            )

    if proposal["status"] == "promoted":
        existing_evidence = proposal.get("promotion_evidence") or {}
        return {
            "status": "already_promoted",
            "proposal_id": proposal_id,
            "craft_record_id": existing_evidence.get("craft_record_id", ""),
            "promotion_evidence": existing_evidence,
        }

    # ── 3. Verify source_run_id matches ────────────────────────────
    if promotion_evidence["source_run_id"] != proposal["source_run_id"]:
        raise ValueError(
            f"Promotion source_run_id mismatch: evidence says "
            f"'{promotion_evidence['source_run_id']}' but proposal has "
            f"'{proposal['source_run_id']}'"
        )

    # ── 4. Create approved Craft record ────────────────────────────
    craft_id = "CRFT_" + hashlib.sha256(proposal_id.encode("utf-8")).hexdigest()[:12].upper()
    now = utc_now_iso()

    craft_record = {
        "craft_id": craft_id,
        "schema_version": "1.0.0",
        "adoption_status": "candidate",
        "source": proposal["source"],
        "source_proposal_id": proposal_id,
        "source_run_id": proposal["source_run_id"],
        "created_at": now,
        "updated_at": now,
        "rights_evidence": promotion_evidence["rights_evidence"],
        "human_reviewer": promotion_evidence["human_reviewer"],
        "review_timestamp": promotion_evidence["review_timestamp"],
        "regression_evidence": promotion_evidence["regression_evidence"],
        "craft_data": proposal["craft_data"],
    }

    craft_path = craft_memory_dir / "craft_records.jsonl"
    craft_path.parent.mkdir(parents=True, exist_ok=True)
    from .utils import read_jsonl
    try:
        existing_rows = read_jsonl(craft_path)
    except json.JSONDecodeError as exc:
        # Approved Craft history is authoritative. Promotion must never
        # "repair" a malformed store by treating all existing rows as absent,
        # because that silently destroys valid history around the bad line.
        raise ValueError(
            "Craft store is malformed; promotion stopped without modifying "
            f"history: {exc}"
        ) from exc
    existing = next(
        (row for row in existing_rows if row.get("source_proposal_id") == proposal_id),
        None,
    )
    if existing is None:
        tmp_path = craft_path.with_name(f".{craft_path.name}.{proposal_id}.tmp")
        tmp_path.write_text(
            "".join(
                json.dumps(row, ensure_ascii=False) + "\n"
                for row in [*existing_rows, craft_record]
            ),
            encoding="utf-8",
        )
        os.replace(tmp_path, craft_path)
    else:
        craft_id = existing["craft_id"]

    # ── 5. Update proposal with promotion evidence ─────────────────
    proposal["status"] = "promoted"
    proposal["promotion_evidence"] = {
        "craft_record_id": craft_id,
        "human_reviewer": promotion_evidence["human_reviewer"],
        "review_timestamp": promotion_evidence["review_timestamp"],
        "rights_evidence": promotion_evidence["rights_evidence"],
        "source_run_id": promotion_evidence["source_run_id"],
        "regression_evidence": promotion_evidence["regression_evidence"],
        "promoted_at": now,
    }
    original_path = _proposals_dir(craft_memory_dir) / f"proposal_{proposal_id}.json"
    proposal_tmp = original_path.with_name(f".{original_path.name}.tmp")
    proposal_tmp.write_text(
        json.dumps(proposal, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    os.replace(proposal_tmp, original_path)

    return {
        "status": "promoted",
        "proposal_id": proposal_id,
        "craft_record_id": craft_id,
        "promotion_evidence": proposal["promotion_evidence"],
    }
