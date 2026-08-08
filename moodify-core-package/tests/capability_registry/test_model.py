"""Tests for capability registry model and deterministic serialization."""

from __future__ import annotations

import pytest

from moodify.capability_registry.model import (
    SCHEMA_VERSION,
    CapabilityContract,
    CapabilityRegistry,
    ProviderRecord,
    registry_dumps,
    registry_from_dict,
    registry_loads,
)


def sample_registry() -> CapabilityRegistry:
    return CapabilityRegistry(
        schema_version=SCHEMA_VERSION,
        capabilities=(
            CapabilityContract(
                capability_id="notation.render",
                contract_version="1.0",
                purpose="Render score",
                inputs=("musicxml",),
                outputs=("pdf", "svg"),
                quality_policy={"page_count_nonzero": True},
                execution={"network_access": False},
                validation=("output_exists",),
                evidence=("provider_version", "command_manifest"),
            ),
        ),
        providers=(
            ProviderRecord(
                provider_id="musescore.cli",
                capability_id="notation.render",
                adapter_version="0.0",
                license_class="external_process",
                license_label="GPLv3 (external process)",
                status="active",
                version="4.5.1",
                binary_path="C:/MuseScore.exe",
                detected_at="2026-08-02T00:00:00Z",
                known_failure_modes=("single -o only",),
            ),
        ),
        generated_at="2026-08-02T00:00:00Z",
    )


class TestRegistryModel:
    def test_get_capability(self) -> None:
        r = sample_registry()
        assert r.get_capability("notation.render") is not None
        assert r.get_capability("nope") is None

    def test_get_provider(self) -> None:
        r = sample_registry()
        assert r.get_provider("musescore.cli") is not None
        assert r.get_provider("nope") is None

    def test_providers_for(self) -> None:
        r = sample_registry()
        assert len(r.providers_for("notation.render")) == 1
        assert r.providers_for("nope") == []

    def test_active_providers_filters(self) -> None:
        r = CapabilityRegistry(
            schema_version=SCHEMA_VERSION,
            providers=(
                ProviderRecord(
                    provider_id="a", capability_id="x", adapter_version="0",
                    license_class="c", license_label="l", status="active",
                ),
                ProviderRecord(
                    provider_id="b", capability_id="x", adapter_version="0",
                    license_class="c", license_label="l", status="known_missing",
                ),
            ),
        )
        assert [p.provider_id for p in r.active_providers()] == ["a"]


class TestSerialization:
    def test_roundtrip_preserves_content(self) -> None:
        r = sample_registry()
        restored = registry_loads(registry_dumps(r))
        assert restored == r

    def test_double_run_same_bytes(self) -> None:
        r = sample_registry()
        assert registry_dumps(r) == registry_dumps(r)

    def test_deterministic_key_order(self) -> None:
        r = sample_registry()
        text = registry_dumps(r)
        assert text.count('"capability_id"') == 2  # capability + provider
        assert '"schema_version"' in text

    def test_no_timestamps_variability(self) -> None:
        r1 = sample_registry()
        r2 = sample_registry()
        assert registry_dumps(r1) == registry_dumps(r2)

    def test_unknown_capability_field_rejected(self) -> None:
        with pytest.raises(ValueError, match="bogus"):
            registry_from_dict(
                {
                    "schema_version": SCHEMA_VERSION,
                    "capabilities": [{"capability_id": "x", "bogus": 1}],
                    "providers": [],
                    "generated_at": "",
                }
            )

    def test_unknown_top_level_key_rejected(self) -> None:
        with pytest.raises(ValueError, match="surprise"):
            registry_from_dict(
                {
                    "schema_version": SCHEMA_VERSION,
                    "capabilities": [],
                    "providers": [],
                    "generated_at": "",
                    "surprise": 1,
                }
            )

    def test_unsupported_schema_version_rejected(self) -> None:
        with pytest.raises(ValueError, match="schema_version"):
            registry_from_dict(
                {
                    "schema_version": "capability-registry/9.9",
                    "capabilities": [],
                    "providers": [],
                    "generated_at": "",
                }
            )

    def test_invalid_provider_status_rejected(self) -> None:
        with pytest.raises(ValueError, match="status"):
            registry_from_dict(
                {
                    "schema_version": SCHEMA_VERSION,
                    "capabilities": [],
                    "providers": [
                        {
                            "provider_id": "a",
                            "capability_id": "x",
                            "adapter_version": "0",
                            "license_class": "c",
                            "license_label": "l",
                            "status": "bogus",
                        }
                    ],
                    "generated_at": "",
                }
            )
