"""22-Process Evidence Manifest.

Per-step traceability for the craft processing chain. Records inputs,
outputs, and deltas for every operation so runs can be audited step by step.
Part of ECHAIN-MOODIFY-MRS-EXTREME-017 / MHP-911.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .craft_processes import CRAFT_REGISTRY, CraftOperation


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class StepEvidence:
    step_index: int
    op_id: str
    op_name: str
    category: str
    risk: str
    metrics_before: dict[str, Any] = field(default_factory=dict)
    metrics_after: dict[str, Any] = field(default_factory=dict)
    delta: dict[str, Any] = field(default_factory=dict)
    params_used: dict[str, Any] = field(default_factory=dict)
    duration_s: float = 0.0
    error: str = ""
    timestamp: str = ""

    def to_dict(self) -> dict[str, Any]:
        d = asdict(self)
        return d

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "StepEvidence":
        valid = {f.name for f in cls.__dataclass_fields__.values()}
        return cls(**{k: v for k, v in d.items() if k in valid})


@dataclass
class CraftManifest:
    manifest_id: str
    run_id: str
    chain_name: str
    total_steps: int
    steps: list[StepEvidence] = field(default_factory=list)
    generated_at: str = ""
    provenance: dict[str, Any] = field(default_factory=dict)

    def summary(self) -> dict[str, Any]:
        categories = {}
        errors = 0
        for s in self.steps:
            cat = s.category or "unknown"
            categories[cat] = categories.get(cat, 0) + 1
            if s.error:
                errors += 1
        return {
            "manifest_id": self.manifest_id,
            "chain_name": self.chain_name,
            "total_steps": self.total_steps,
            "steps_recorded": len(self.steps),
            "errors": errors,
            "categories": categories,
        }

    def to_dict(self) -> dict[str, Any]:
        return {
            "manifest_id": self.manifest_id,
            "run_id": self.run_id,
            "chain_name": self.chain_name,
            "total_steps": self.total_steps,
            "generated_at": self.generated_at,
            "provenance": self.provenance,
            "steps": [s.to_dict() for s in self.steps],
        }

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "CraftManifest":
        steps = [StepEvidence.from_dict(s) for s in d.get("steps", [])]
        return cls(
            manifest_id=d.get("manifest_id", ""),
            run_id=d.get("run_id", ""),
            chain_name=d.get("chain_name", ""),
            total_steps=d.get("total_steps", 0),
            steps=steps,
            generated_at=d.get("generated_at", ""),
            provenance=d.get("provenance", {}),
        )


def create_step_evidence(
    op_id: str,
    step_index: int,
    metrics_before: dict[str, Any] | None = None,
    metrics_after: dict[str, Any] | None = None,
    params_used: dict[str, Any] | None = None,
    duration_s: float = 0.0,
    error: str = "",
) -> StepEvidence:
    op = CRAFT_REGISTRY.get(op_id)
    op_name = op.name if op else op_id
    category = op.category.value if op else "unknown"
    risk = op.risk.value if op else "unknown"

    before = metrics_before or {}
    after = metrics_after or {}
    delta = {}
    for key in set(list(before) + list(after)):
        v_b = before.get(key)
        v_a = after.get(key)
        if isinstance(v_b, (int, float)) and isinstance(v_a, (int, float)):
            delta[key] = round(v_a - v_b, 4)
        elif v_b != v_a:
            delta[key] = f"{v_b}->{v_a}"

    return StepEvidence(
        step_index=step_index,
        op_id=op_id,
        op_name=op_name,
        category=category,
        risk=risk,
        metrics_before=before,
        metrics_after=after,
        delta=delta,
        params_used=params_used or {},
        duration_s=duration_s,
        error=error,
        timestamp=_utc_now_iso(),
    )


def create_manifest(
    manifest_id: str,
    run_id: str,
    chain_name: str,
    steps: list[StepEvidence] | None = None,
) -> CraftManifest:
    steps = steps or []
    return CraftManifest(
        manifest_id=manifest_id,
        run_id=run_id,
        chain_name=chain_name,
        total_steps=len(CRAFT_REGISTRY),
        steps=steps,
        generated_at=_utc_now_iso(),
        provenance={
            "craft_registry_size": len(CRAFT_REGISTRY),
            "op_ids": sorted(CRAFT_REGISTRY.keys()),
        },
    )


def write_manifest(manifest: CraftManifest, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(manifest.to_dict(), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def load_manifest(path: Path) -> CraftManifest:
    d = json.loads(path.read_text(encoding="utf-8"))
    return CraftManifest.from_dict(d)


def can_write_back(manifest: CraftManifest,
                   rights_cleared: bool = False,
                   human_approved: bool = False) -> tuple[bool, str]:
    """Predicate: a manifest may enter the Craft Library only when clean.

    Returns (allowed, reason). A manifest is rejected when any step has an
    error, the run is incomplete, rights are not cleared, or a required
    human approval is missing.
    """
    if not manifest.steps:
        return False, "no step evidence recorded"
    if manifest.total_steps == 0:
        return False, "manifest total_steps is zero"

    for step in manifest.steps:
        if step.error:
            return False, f"step {step.step_index} ({step.op_id}) has error: {step.error}"

    if len(manifest.steps) < manifest.total_steps:
        return False, f"incomplete: {len(manifest.steps)}/{manifest.total_steps} steps recorded"

    if not rights_cleared:
        return False, "rights not cleared for source audio"

    if manifest.provenance.get("requires_human_approval") and not human_approved:
        return False, "human approval required but not provided"

    return True, "ok"


def list_process_categories() -> dict[str, list[str]]:
    cats: dict[str, list[str]] = {}
    for op_id, op in CRAFT_REGISTRY.items():
        cat = op.category.value
        if cat not in cats:
            cats[cat] = []
        cats[cat].append(op_id)
    return cats
