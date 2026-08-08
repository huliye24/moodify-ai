"""Fail-closed engineering gates for rights and release authority.

Rights state is read from an explicit rights manifest. Treatment feedback is
listening evidence and must never be interpreted as copyright authorization.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


RIGHTS_TERMINAL_STATES = {"ready", "blocked"}
RIGHTS_ALLOWED_STATE = "ready"


def check_rights_cleared(manifest_path: str | Path) -> dict[str, Any]:
    """Validate a structured rights manifest and return a fail-closed status.

    Expected manifest fields are ``schema_version``, ``gate_id``, and an
    ``assets`` list. Each asset requires a unique ``asset_id``, ``source_path``,
    and a status of ``pending``, ``ready``, or ``blocked``. Only ``ready`` is
    authorized. Missing, malformed, empty, duplicated, or unknown data blocks
    the entire gate.
    """
    path = Path(manifest_path)
    base: dict[str, Any] = {
        "manifest_path": str(path),
        "total_assets": 0,
        "ready_count": 0,
        "pending_count": 0,
        "blocked_count": 0,
        "ready_assets": [],
        "pending_assets": [],
        "blocked_assets": [],
        "rights_cleared": False,
        "errors": [],
    }
    if not path.is_file():
        base["errors"].append(f"rights manifest not found: {path}")
        return base

    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        base["errors"].append(f"invalid rights manifest: {exc}")
        return base

    if not isinstance(data, dict):
        base["errors"].append("rights manifest root must be an object")
        return base
    for field in ("schema_version", "gate_id", "assets"):
        if field not in data:
            base["errors"].append(f"missing required field: {field}")
    assets = data.get("assets")
    if not isinstance(assets, list) or not assets:
        base["errors"].append("assets must be a non-empty list")
        return base

    seen: set[str] = set()
    for index, asset in enumerate(assets):
        if not isinstance(asset, dict):
            base["errors"].append(f"assets[{index}] must be an object")
            continue
        asset_id = str(asset.get("asset_id", "")).strip()
        source_path = str(asset.get("source_path", "")).strip()
        status = str(asset.get("status", "")).strip().lower()
        if not asset_id:
            base["errors"].append(f"assets[{index}] missing asset_id")
            continue
        if asset_id in seen:
            base["errors"].append(f"duplicate asset_id: {asset_id}")
            continue
        seen.add(asset_id)
        if not source_path:
            base["errors"].append(f"{asset_id}: missing source_path")
        if status not in {"pending", "ready", "blocked"}:
            base["errors"].append(f"{asset_id}: invalid status {status!r}")
            status = "blocked"
        base[f"{status}_assets"].append(asset_id)

    base["total_assets"] = len(assets)
    base["ready_count"] = len(base["ready_assets"])
    base["pending_count"] = len(base["pending_assets"])
    base["blocked_count"] = len(base["blocked_assets"])
    base["rights_cleared"] = (
        not base["errors"]
        and base["ready_count"] == base["total_assets"]
        and base["total_assets"] > 0
    )
    return base


_MRS_GATE_ACCURACY = 0.091
_MRS_PSEUDO_CORRELATION = 0.19
_MRS_OPEN_AGREEMENT = 0.606

MRS_AUTHORITY_STATEMENT = (
    f"MRS gate accuracy is {_MRS_GATE_ACCURACY:.1%}, "
    f"pseudo-MRS preference correlation is approximately {_MRS_PSEUDO_CORRELATION:.2f}, "
    f"and MRS Open agreement is approximately {_MRS_OPEN_AGREEMENT:.1%}. "
    "MRS is technical evidence and must not serve as the sole professional "
    "sound-quality release authority."
)


def mrs_can_release(
    mrs_score: float | None = None,
    human_approved: bool = False,
) -> tuple[bool, str]:
    """Return whether professional listening approval permits release.

    ``mrs_score`` is retained as traceable technical evidence; it never grants
    authority. This predicate must be called by a release boundary to enforce
    the policy and is not, by itself, proof of integration.
    """
    if not human_approved:
        return False, f"human listening approval required; {MRS_AUTHORITY_STATEMENT}"
    return True, "ok"


def is_rights_pending_audio(manifest_path: str | Path, asset_id: str) -> bool:
    """Fail closed unless ``asset_id`` is explicitly ``ready`` in the manifest."""
    status = check_rights_cleared(manifest_path)
    return asset_id not in status.get("ready_assets", [])


def authorize_audio_source(
    manifest_path: str | Path,
    asset_id: str,
    source_path: str | Path,
) -> tuple[bool, str]:
    """Authorize one exact source path from a valid structured manifest."""
    path = Path(manifest_path)
    status = check_rights_cleared(path)
    if status["errors"]:
        return False, "; ".join(status["errors"])
    if asset_id not in status["ready_assets"]:
        return False, f"asset {asset_id!r} is not explicitly ready"
    data = json.loads(path.read_text(encoding="utf-8"))
    asset = next(item for item in data["assets"] if item["asset_id"] == asset_id)
    expected = str(Path(asset["source_path"]).resolve(strict=False)).casefold()
    actual = str(Path(source_path).resolve(strict=False)).casefold()
    if expected != actual:
        return False, f"source path does not match rights asset {asset_id!r}"
    return True, "ok"
