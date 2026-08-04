"""MHP-166: Craft Core Tests — preset metadata, safety gate, experiment runner."""

import tempfile
from pathlib import Path

import pytest

from moodify_runtime.craft_presets import (
    PresetMetadata,
    PresetCategory,
    load_preset_metadata,
    validate_preset_safety,
    SafetyGateResult,
)
from moodify_runtime.craft_probes import (
    detect_over_bright,
    detect_transient_damage,
    detect_stereo_collapse,
    detect_vocal_thinning,
    FailureCase,
    build_failure_case_library,
    query_failure_cases,
)


# ── MHP-162: Preset Metadata ─────────────────────────────────────────


def test_load_preset_metadata_known():
    m = load_preset_metadata("warm_vocal")
    assert m.name == "warm_vocal"
    assert m.category == "warm_reality"
    assert m.adoption_status == "experimental"


def test_load_preset_metadata_unknown():
    m = load_preset_metadata("nonexistent_preset")
    assert m.category == "dynamic_recovery"  # default


def test_preset_metadata_to_dict():
    m = load_preset_metadata("clean_master")
    d = m.to_dict()
    assert d["name"] == "clean_master"
    assert d["category"] == "dynamic_recovery"
    assert "preset_id" in d


# ── MHP-165: Safety Gate ─────────────────────────────────────────────


def test_safety_gate_all_pass():
    r = validate_preset_safety("warm_vocal")
    assert r.passed
    assert len(r.failures) == 0


def test_safety_gate_over_dark_severe():
    r = validate_preset_safety("warm_vocal", over_dark_level="severe")
    assert not r.passed
    assert any("over_dark" in f["gate"] for f in r.failures)


def test_safety_gate_over_bright_severe():
    r = validate_preset_safety("clean_master", over_bright_level="severe")
    assert not r.passed
    assert any("over_bright" in f["gate"] for f in r.failures)


def test_safety_gate_transient_severe():
    r = validate_preset_safety("wide_space", transient_damage_level="severe")
    assert not r.passed


def test_safety_gate_warnings():
    r = validate_preset_safety("warm_vocal", over_dark_level="mild", stereo_collapse_level="severe")
    assert r.passed  # warnings only, no failures
    assert len(r.warnings) >= 1


def test_safety_gate_multiple_failures():
    r = validate_preset_safety("bad_preset", over_dark_level="severe", over_bright_level="severe",
                               transient_damage_level="severe", vocal_thinning_level="severe")
    assert not r.passed
    assert len(r.failures) == 4


# ── MHP-149→152: Probe detectors with synthetic audio ────────────────


def test_overbright_detector_integration():
    import struct, math, wave
    tmp = Path(tempfile.mkdtemp())
    sr = 44100

    def ww(path, freqs, amps):
        with wave.open(str(path), 'wb') as wf:
            wf.setnchannels(1); wf.setsampwidth(2); wf.setframerate(sr)
            n = int(sr * 0.3)
            samples = [int(max(-1, min(1, sum(a * math.sin(2 * math.pi * f * i / sr) for f, a in zip(freqs, amps)))) * 32767) for i in range(n)]
            wf.writeframes(struct.pack('<' + 'h' * n, *samples))

    ww(tmp / 'b.wav', [1000, 2000], [0.5, 0.3])
    ww(tmp / 'a_bright.wav', [1000, 2000, 12000], [0.5, 0.3, 0.6])

    r = detect_over_bright(str(tmp / 'b.wav'), str(tmp / 'a_bright.wav'))
    assert r["delta_db"] > 0  # brighter


def test_failure_case_library_writes_and_queries(tmp_path):
    cases = [
        FailureCase(case_id="FC1", preset="warm_vocal", genre="piano", sample_id="SMP_001", defect_type="over_dark", severity="severe"),
        FailureCase(case_id="FC2", preset="clean_master", genre="electronic", sample_id="SMP_002", defect_type="over_bright", severity="mild"),
    ]
    result = build_failure_case_library(tmp_path, cases)
    assert result["cases_written"] == 2

    # Query by defect_type
    results = query_failure_cases(tmp_path, defect_type="over_dark")
    assert len(results) == 1
    assert results[0]["case_id"] == "FC1"

    # Query by preset
    results = query_failure_cases(tmp_path, preset="clean_master")
    assert len(results) == 1


# ── MHP-163: Preset Experiment Runner ────────────────────────────────


def test_preset_experiment_runner(tmp_path):
    """Smoke test: run_preset_experiment on a real WAV through 2 presets."""
    baseline = Path(__file__).resolve().parents[2] / "moodify-core-package" / "tests" / "baseline" / "test_audio" / "piano.wav"
    if not baseline.exists():
        pytest.skip("baseline wav not available")

    from moodify_runtime.craft_presets import run_preset_experiment
    results = run_preset_experiment(
        str(baseline),
        preset_names=["warm_vocal", "clean_master"],
        genre="piano",
        output_dir=str(tmp_path),
    )
    assert len(results) == 2
    assert results[0]["preset"] == "warm_vocal"
    assert results[1]["preset"] == "clean_master"
    for r in results:
        assert "pseudo_mrs_delta" in r
        assert "safety_gate" in r
        assert "over_dark" in r
        assert "over_bright" in r


def test_ab_comparison_report(tmp_path):
    """Build a markdown report from experiment results."""
    results = [
        {"sample_id": "S1", "preset": "warm_vocal", "pseudo_mrs_delta": 5.0,
         "over_dark": "none", "over_bright": "none", "transient_damage": "none",
         "vocal_thinning": "none", "safety_gate": {"passed": True, "failures": [], "warnings": []}},
        {"sample_id": "S1", "preset": "clean_master", "pseudo_mrs_delta": 2.0,
         "over_dark": "mild", "over_bright": "none", "transient_damage": "none",
         "vocal_thinning": "none", "safety_gate": {"passed": True, "failures": [], "warnings": [{"gate": "over_dark", "level": "mild"}]}},
    ]
    from moodify_runtime.craft_presets import build_ab_comparison_report
    report = build_ab_comparison_report(results, output_path=str(tmp_path / "ab_report.md"))
    assert len(report["preset_ranks"]) == 2
    # warm_vocal should rank higher
    assert report["preset_ranks"][0][0] == "warm_vocal"
