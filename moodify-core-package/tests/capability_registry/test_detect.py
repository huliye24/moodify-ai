"""Tests for read-only environment detectors."""

from __future__ import annotations

from pathlib import Path

from moodify.capability_registry.detect import (
    DetectionResult,
    detect_all,
    detect_musescore,
    python_version,
)


class TestDetectReadOnly:
    def test_all_detectors_return_shapes(self) -> None:
        results = detect_all()
        assert set(results) >= {
            "musescore", "ffmpeg", "ffprobe", "sox", "rubberband", "audacity",
            "basic_pitch", "moodify_self",
        }
        for result in results.values():
            assert isinstance(result, DetectionResult)
            assert isinstance(result.found, bool)

    def test_found_implies_binary_path(self) -> None:
        for result in detect_all().values():
            if result.found and result.tool != "moodify_self":
                assert result.binary_path is not None

    def test_musescore_negative_knowledge_present(self) -> None:
        result = detect_musescore()
        assert result.known_failure_modes, "negative knowledge must not be empty"
        assert any("single -o" in m or "-o" in m for m in result.known_failure_modes)

    def test_python_version_available(self) -> None:
        assert python_version().startswith("3.")

    def test_detect_is_repeatable(self) -> None:
        r1 = detect_all()
        r2 = detect_all()
        for name in r1:
            assert r1[name].found == r2[name].found
            assert r1[name].binary_path == r2[name].binary_path


class TestRegistryBootstrap:
    def test_bootstrap_registers_all_capabilities(self) -> None:
        from moodify.capability_registry.bootstrap import build_registry

        r = build_registry()
        ids = {c.capability_id for c in r.capabilities}
        assert ids == {
            "media.transcode", "media.probe", "notation.render",
            "audio.time_stretch", "audio.measure_loudness",
            "audio.separate_manifest", "waveform.region_edit",
            "lyric.align", "auditory.ocean_listen",
        }
        assert len(r.capabilities) == len(r.providers)
        assert all(p.capability_id for p in r.providers)

    def test_bootstrap_provider_license_labels(self) -> None:
        from moodify.capability_registry.bootstrap import build_registry

        r = build_registry()
        labels = {p.provider_id: p.license_label for p in r.providers}
        assert "GPLv3 (external process)" in labels["musescore.cli"]
        assert "Apache-2.0 (internal)" in labels["basic_pitch.moodify"]
        assert "GPLv2 (external process)" in labels["rubberband.cli"]

    def test_bootstrap_negative_knowledge_not_empty_for_known_providers(self) -> None:
        from moodify.capability_registry.bootstrap import build_registry

        r = build_registry()
        for p in r.providers:
            if p.status == "active" and p.provider_id in (
                "musescore.cli", "rubberband.cli", "basic_pitch.moodify",
            ):
                assert p.known_failure_modes, f"{p.provider_id} lacks negative knowledge"

    def test_bootstrap_registry_roundtrip(self, tmp_path: Path) -> None:
        from moodify.capability_registry.bootstrap import build_registry, write_registry
        from moodify.capability_registry.model import registry_loads

        r = build_registry()
        path = write_registry(r, tmp_path / "registry.json")
        restored = registry_loads(path.read_text(encoding="utf-8"))
        assert restored == r
