"""Registry model — strict typed, versioned, deterministic serialization.

Contract: docs/tasks/deepseek/DSK-MFY-CAPABILITY-ACCRETION-017/00_TASK_ORCHESTRATION.md
Every record must be verifiable: unknown fields rejected, canonical JSON
deterministic across runs, sources traceable (negative knowledge).
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Literal

SCHEMA_VERSION = "capability-registry/0.1"

RegistryState = Literal["active", "known_missing", "unsupported"]


@dataclass(frozen=True)
class CapabilityContract:
    capability_id: str
    contract_version: str
    purpose: str
    inputs: tuple[str, ...]
    outputs: tuple[str, ...]
    quality_policy: dict = field(default_factory=dict)
    execution: dict = field(default_factory=dict)
    validation: tuple[str, ...] = ()
    evidence: tuple[str, ...] = ()


@dataclass(frozen=True)
class ProviderRecord:
    provider_id: str
    capability_id: str
    adapter_version: str
    license_class: str  # e.g. "reviewed" | "external_process"
    license_label: str  # e.g. "GPLv3 (external process)"
    status: RegistryState
    version: str | None = None
    binary_path: str | None = None
    detected_at: str = ""
    known_failure_modes: tuple[str, ...] = ()
    health: dict = field(default_factory=dict)
    notes: str = ""


@dataclass(frozen=True)
class CapabilityRegistry:
    schema_version: str
    capabilities: tuple[CapabilityContract, ...] = ()
    providers: tuple[ProviderRecord, ...] = ()
    generated_at: str = ""

    def get_capability(self, capability_id: str) -> CapabilityContract | None:
        return next((c for c in self.capabilities if c.capability_id == capability_id), None)

    def get_provider(self, provider_id: str) -> ProviderRecord | None:
        return next((p for p in self.providers if p.provider_id == provider_id), None)

    def providers_for(self, capability_id: str) -> list[ProviderRecord]:
        return [p for p in self.providers if p.capability_id == capability_id]

    def active_providers(self) -> list[ProviderRecord]:
        return [p for p in self.providers if p.status == "active"]


def _capability_to_dict(c: CapabilityContract) -> dict:
    return {
        "capability_id": c.capability_id,
        "contract_version": c.contract_version,
        "purpose": c.purpose,
        "inputs": list(c.inputs),
        "outputs": list(c.outputs),
        "quality_policy": c.quality_policy,
        "execution": c.execution,
        "validation": list(c.validation),
        "evidence": list(c.evidence),
    }


def _provider_to_dict(p: ProviderRecord) -> dict:
    return {
        "provider_id": p.provider_id,
        "capability_id": p.capability_id,
        "adapter_version": p.adapter_version,
        "license_class": p.license_class,
        "license_label": p.license_label,
        "status": p.status,
        "version": p.version,
        "binary_path": p.binary_path,
        "detected_at": p.detected_at,
        "known_failure_modes": list(p.known_failure_modes),
        "health": p.health,
        "notes": p.notes,
    }


def registry_to_dict(r: CapabilityRegistry) -> dict:
    return {
        "schema_version": r.schema_version,
        "capabilities": [_capability_to_dict(c) for c in r.capabilities],
        "providers": [_provider_to_dict(p) for p in r.providers],
        "generated_at": r.generated_at,
    }


def registry_dumps(r: CapabilityRegistry) -> str:
    """Canonical JSON: sorted keys, compact separators, deterministic."""
    return json.dumps(registry_to_dict(r), ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _reject_unknown(data: dict, allowed: set[str], context: str) -> None:
    unknown = set(data) - allowed
    if unknown:
        raise ValueError(f"unknown field(s) in {context}: {sorted(unknown)}")


def _parse_capability(data: dict) -> CapabilityContract:
    _reject_unknown(
        data,
        {
            "capability_id", "contract_version", "purpose", "inputs", "outputs",
            "quality_policy", "execution", "validation", "evidence",
        },
        "capability",
    )
    return CapabilityContract(
        capability_id=str(data["capability_id"]),
        contract_version=str(data.get("contract_version", "1.0")),
        purpose=str(data.get("purpose", "")),
        inputs=tuple(data.get("inputs", ())),
        outputs=tuple(data.get("outputs", ())),
        quality_policy=dict(data.get("quality_policy", {})),
        execution=dict(data.get("execution", {})),
        validation=tuple(data.get("validation", ())),
        evidence=tuple(data.get("evidence", ())),
    )


def _parse_provider(data: dict) -> ProviderRecord:
    _reject_unknown(
        data,
        {
            "provider_id", "capability_id", "adapter_version", "license_class",
            "license_label", "status", "version", "binary_path", "detected_at",
            "known_failure_modes", "health", "notes",
        },
        "provider",
    )
    status = data.get("status", "active")
    if status not in ("active", "known_missing", "unsupported"):
        raise ValueError(f"invalid provider status: {status}")
    return ProviderRecord(
        provider_id=str(data["provider_id"]),
        capability_id=str(data["capability_id"]),
        adapter_version=str(data.get("adapter_version", "")),
        license_class=str(data.get("license_class", "")),
        license_label=str(data.get("license_label", "")),
        status=status,
        version=data.get("version"),
        binary_path=data.get("binary_path"),
        detected_at=str(data.get("detected_at", "")),
        known_failure_modes=tuple(data.get("known_failure_modes", ())),
        health=dict(data.get("health", {})),
        notes=str(data.get("notes", "")),
    )


def registry_from_dict(data: dict) -> CapabilityRegistry:
    _reject_unknown(data, {"schema_version", "capabilities", "providers", "generated_at"}, "registry")
    if data.get("schema_version") != SCHEMA_VERSION:
        raise ValueError(f"unsupported schema_version: {data.get('schema_version')}")
    return CapabilityRegistry(
        schema_version=str(data["schema_version"]),
        capabilities=tuple(_parse_capability(c) for c in data.get("capabilities", ())),
        providers=tuple(_parse_provider(p) for p in data.get("providers", ())),
        generated_at=str(data.get("generated_at", "")),
    )


def registry_loads(text: str) -> CapabilityRegistry:
    return registry_from_dict(json.loads(text))
