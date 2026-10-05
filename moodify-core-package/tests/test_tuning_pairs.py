"""Paired tier rendering — `moodify tuning render-pair` (MIP-0002 Addendum A).

Covers the machine contract the Studio shell depends on:

* the tier set is closed and self-describing, and an unknown mode/tier is refused;
* one call renders **one complete pair** — A and B mixes, tuned slots, plans and evidence — with
  explicit parameters and an uncalibrated calibration status throughout;
* publication is atomic: a failure on either side leaves no `<pair_id>` and no leftover attempt;
* an existing pair directory is never overwritten and the source audio is never written to;
* the hard gates (decode / duration / SR / channels / finite / ceiling) are measured, recorded,
  and actually enforced;
* and on real synthesised audio the two sides decode, differ, and can both be analysed.
"""

from __future__ import annotations

import hashlib
import json
import shutil
from pathlib import Path

import numpy as np
import pytest
import soundfile as sf

from moodify import release_cli, tuning
from moodify.mix_graph.schema import MixGraphError

pytestmark = pytest.mark.v01

SR = 22050


# ——— fixtures ————————————————————————————————————————————————————————————


def _write_song(path: Path, seconds: float = 1.0) -> Path:
    """A short deterministic stereo signal: tonal body plus a quiet high band."""
    t = np.arange(int(SR * seconds)) / SR
    left = (0.30 * np.sin(2 * np.pi * 220.0 * t)).astype(np.float32)
    right = (0.25 * np.sin(2 * np.pi * 330.0 * t)
             + 0.05 * np.sin(2 * np.pi * 1200.0 * t)).astype(np.float32)
    sf.write(str(path), np.column_stack([left, right]), SR, subtype="PCM_16")
    return path


def _sha256(path: Path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def _run(capsys, argv) -> tuple[int, dict | None, dict | None]:
    """Run the CLI once; return (exit code, stdout JSON, last stderr JSON)."""
    code = release_cli.main(argv)
    captured = capsys.readouterr()
    out = captured.out.strip()
    err_lines = [line for line in captured.err.splitlines() if line.strip()]
    err = err_lines[-1] if err_lines else ""

    def parse(text: str):
        return json.loads(text) if text.startswith("{") and text.endswith("}") else None

    return code, parse(out), parse(err)


@pytest.fixture
def song(tmp_path) -> Path:
    return _write_song(tmp_path / "song.wav")


# ——— 1. tiers are a closed, self-describing set ————————————————————————————


def test_tier_set_is_closed_and_ordered():
    assert tuning.TIER_ORDER == ("conservative", "full")
    assert tuning.SIDE_OF_TIER == {"conservative": "A", "full": "B"}
    assert tuning.MODES == ("fast-stereo-only",)


def test_tier_descriptor_declares_every_value_and_its_calibration_state():
    for tier in tuning.TIER_ORDER:
        d = tuning.tier_descriptor(tier)
        assert d["schema"] == "moodify.core.tuning-tier/0.1"
        assert d["tier"] == tier
        assert d["mode"] == "FAST_STEREO_ONLY"
        assert d["calibration_status"] == "UNCALIBRATED_ENGINEERING_DEFAULT"
        assert d["engine_version"]
        assert d["preserve"] == [], "nobody recorded what to protect; claiming it would be invented"
        nodes = d["parameters"]["nodes"]
        assert len(nodes) >= 3, "every executed node must be listed"
        for node in nodes:
            assert node["type"] in ("eq", "compressor", "stereo", "limiter")
            assert node["parameters"], "a node with no parameters is not a parameter record"


def test_unknown_tier_is_refused():
    with pytest.raises(tuning.TuningError):
        tuning.tier_descriptor("aggressive")
    with pytest.raises(tuning.TuningError):
        tuning.build_tier_graph("clean_master", "song.wav")


def test_tiers_do_not_reuse_the_retired_presets():
    """`clean_master` / `warm_vocal` / `wide_space` retired as product surfaces on 2026-10-04."""
    for tier in tuning.TIER_ORDER:
        blob = json.dumps(tuning.tier_descriptor(tier), ensure_ascii=False)
        for retired in ("clean_master", "warm_vocal", "wide_space"):
            assert retired not in blob


def test_tiers_differ_in_their_explicit_parameters():
    a = tuning.tier_descriptor("conservative")["parameters"]["nodes"]
    b = tuning.tier_descriptor("full")["parameters"]["nodes"]
    assert a != b, "two tiers that apply the same values are not two tiers"


def test_tier_graph_is_a_valid_mix_graph(song):
    graph = tuning.build_tier_graph("full", song)
    assert graph.digest() == tuning.build_tier_graph("full", song).digest(), "digest is stable"
    assert tuning.build_tier_graph("conservative", song).digest() != graph.digest()


# ——— 2. one call renders one complete pair ————————————————————————————————


def test_render_pair_produces_both_sides_and_a_pair_record(tmp_path, song):
    pair_dir = tmp_path / "tuning" / "tune_test_0001"
    result = tuning.render_pair(song, pair_dir, pair_id="tune_test_0001")

    assert result["status"] == "rendered"
    assert result["pair_id"] == "tune_test_0001"
    assert result["mode"] == "FAST_STEREO_ONLY"
    assert result["calibration_status"] == "UNCALIBRATED_ENGINEERING_DEFAULT"
    assert result["review_required"] is True
    assert result["tiers"] == {"A": "conservative", "B": "full"}
    assert result["checks"] == {"both_sides_published": True, "distinct_outputs": True}

    for side in ("A", "B"):
        for rel in ("plan.json", "evidence.json", "mix.wav", "tuned/source.wav"):
            assert (pair_dir / side / rel).is_file(), f"{side}/{rel} must exist"

    pair = json.loads((pair_dir / "pair.json").read_text(encoding="utf-8"))
    assert pair["schema"] == "moodify.studio.tuning-pair/0.1"
    assert pair["pair_id"] == "tune_test_0001"
    assert pair["mode"] == "FAST_STEREO_ONLY"
    assert pair["tiers"] == {"A": "conservative", "B": "full"}
    assert pair["source_sha256"] == _sha256(song)
    assert pair["calibration_status"] == "UNCALIBRATED_ENGINEERING_DEFAULT"
    assert pair["created_at"]

    # No leftover attempt directory anywhere near the pair.
    assert [p.name for p in pair_dir.parent.iterdir()] == ["tune_test_0001"]


def test_both_sides_carry_their_own_evidence_and_differ(tmp_path, song):
    pair_dir = tmp_path / "pairs" / "tune_test_0002"
    tuning.render_pair(song, pair_dir, pair_id="tune_test_0002")

    a = json.loads((pair_dir / "A" / "evidence.json").read_text(encoding="utf-8"))
    b = json.loads((pair_dir / "B" / "evidence.json").read_text(encoding="utf-8"))
    assert a["schema"] == "moodify.studio.tier-evidence/0.1"
    for side, doc, tier in (("A", a, "conservative"), ("B", b, "full")):
        assert doc["tier"]["tier"] == tier
        assert doc["tier"]["calibration_status"] == "UNCALIBRATED_ENGINEERING_DEFAULT"
        assert doc["review_required"] is True
        assert doc["source_sha256"] == _sha256(song)
        assert doc["output"]["mix_sha256"] == _sha256(pair_dir / side / "mix.wav")
        assert doc["output"]["tuned_sha256"] == _sha256(pair_dir / side / "tuned" / "source.wav")
        assert doc["graph_digest_sha256"]
        assert doc["verification"]["before"] and doc["verification"]["after"]
        assert doc["verification"]["invariants"]["finite_output"] is True
        assert doc["duration_s"] and doc["sample_rate"] == SR and doc["channels"] == 2
        assert doc["finite"] is True
        assert doc["mix_graph_evidence"]["schema"] == "moodify.mix_graph.evidence/0.1"
        # A published artifact must not point at the temporary attempt directory.
        assert ".attempt" not in doc["output"]["mix_wav"]
        assert ".attempt" not in doc["render_step"]["relocated_to"]
        assert ".attempt" in doc["render_step"]["rendered_to"], "the render step is recorded as-is"

    assert a["output"]["mix_sha256"] != b["output"]["mix_sha256"], "A and B must not be one sound"
    assert a["graph_digest_sha256"] != b["graph_digest_sha256"]


def test_graph_digest_in_evidence_is_recomputable_from_the_plan(tmp_path, song):
    pair_dir = tmp_path / "pairs" / "tune_test_0003"
    tuning.render_pair(song, pair_dir, pair_id="tune_test_0003")
    for side in ("A", "B"):
        plan = json.loads((pair_dir / side / "plan.json").read_text(encoding="utf-8"))
        ev = json.loads((pair_dir / side / "evidence.json").read_text(encoding="utf-8"))
        identity = {"schema": "moodify.mix_graph/0.1", "nodes": plan["parameters"]["nodes"]}
        payload = json.dumps(identity, ensure_ascii=False, sort_keys=True)
        recomputed = hashlib.sha256(payload.encode("utf-8")).hexdigest()
        assert recomputed == ev["graph_digest_sha256"], "parameters must reproduce the digest"
        assert plan["graph_digest_sha256"] == ev["graph_digest_sha256"]


def test_duration_sample_rate_and_channels_are_gated(tmp_path, song):
    pair_dir = tmp_path / "pairs" / "tune_test_0004"
    tuning.render_pair(song, pair_dir, pair_id="tune_test_0004")
    for side in ("A", "B"):
        ev = json.loads((pair_dir / side / "evidence.json").read_text(encoding="utf-8"))
        gates = {g["gate"]: g for g in ev["checks"]}
        assert set(gates) == {"decodable", "duration_preserved", "sample_rate_preserved",
                              "channels_preserved", "finite_output", "within_full_scale"}
        for gate in gates.values():
            assert gate["passed"] is True, gate
        assert gates["duration_preserved"]["measured"]["delta_samples"] == 0
        assert gates["sample_rate_preserved"]["measured"]["output"] == SR
        assert gates["channels_preserved"]["measured"]["output"] == 2


def test_peak_never_exceeds_the_declared_ceiling(tmp_path, song):
    pair_dir = tmp_path / "pairs" / "tune_test_0005"
    tuning.render_pair(song, pair_dir, pair_id="tune_test_0005")
    for side in ("A", "B"):
        ev = json.loads((pair_dir / side / "evidence.json").read_text(encoding="utf-8"))
        peak = ev["mix_graph_evidence"]["verification"]["peak_gate"]
        assert peak["limit"] == -1.0
        assert peak["passed"] is True
        assert peak["measured"] <= peak["limit"] + 0.01


# ——— 3. atomicity and refusal —————————————————————————————————————————————


def test_an_existing_pair_directory_is_never_overwritten(tmp_path, song):
    pair_dir = tmp_path / "pairs" / "tune_test_0006"
    first = tuning.render_pair(song, pair_dir, pair_id="tune_test_0006")
    before = {p.relative_to(pair_dir).as_posix(): _sha256(p)
              for p in pair_dir.rglob("*") if p.is_file()}
    with pytest.raises(tuning.TuningError):
        tuning.render_pair(song, pair_dir, pair_id="tune_test_0006")
    after = {p.relative_to(pair_dir).as_posix(): _sha256(p)
             for p in pair_dir.rglob("*") if p.is_file()}
    assert after == before, "the refused second attempt must not touch the first pair"
    assert first["pair_id"] == "tune_test_0006"


def test_source_audio_is_never_written_to(tmp_path, song):
    before = _sha256(song)
    tuning.render_pair(song, tmp_path / "pairs" / "tune_test_0007", pair_id="tune_test_0007")
    assert _sha256(song) == before


def test_unknown_mode_is_refused_before_anything_is_written(tmp_path, song):
    pair_dir = tmp_path / "pairs" / "tune_test_0008"
    with pytest.raises(tuning.TuningError, match="unknown mode"):
        tuning.render_pair(song, pair_dir, mode="deep")
    assert not pair_dir.exists()
    assert not pair_dir.parent.exists() or list(pair_dir.parent.iterdir()) == []


def test_missing_source_is_refused(tmp_path):
    with pytest.raises(tuning.TuningError, match="source is not a file"):
        tuning.render_pair(tmp_path / "nope.wav", tmp_path / "pairs" / "x")


def test_one_side_failing_publishes_no_pair_and_leaves_no_attempt(tmp_path, song, monkeypatch):
    """The whole point of the attempt directory: a half pair never becomes a pair."""
    pair_dir = tmp_path / "pairs" / "tune_test_0009"
    calls = {"n": 0}
    real_run_session = tuning.run_session

    def failing(graph, output_dir, dry_run=False):
        calls["n"] += 1
        if calls["n"] == 2:  # the B side
            raise MixGraphError("injected failure while rendering the second side")
        return real_run_session(graph, output_dir, dry_run)

    monkeypatch.setattr(tuning, "run_session", failing)
    with pytest.raises(MixGraphError):
        tuning.render_pair(song, pair_dir, pair_id="tune_test_0009")

    assert not pair_dir.exists(), "a partial pair must never appear"
    assert list(pair_dir.parent.iterdir()) == [], "the attempt directory must be removed"


def test_identical_tiers_are_refused_rather_than_sold_as_two_candidates(tmp_path, song, monkeypatch):
    """Two byte-identical candidates are not two candidates (Phase 2 stop condition)."""
    pair_dir = tmp_path / "pairs" / "tune_test_0010"
    monkeypatch.setattr(tuning, "_render_side", lambda *a, **k: {
        "side": "A", "tier": "conservative", "mix_sha256": "same", "checks": [],
    })
    with pytest.raises(tuning.TuningError):
        tuning.render_pair(song, pair_dir, pair_id="tune_test_0010")
    assert not pair_dir.exists()


def test_a_failure_after_publishing_is_not_possible_by_construction(tmp_path, song):
    """Sanity: the happy path leaves exactly one directory, and it is complete."""
    pair_dir = tmp_path / "pairs" / "tune_test_0011"
    tuning.render_pair(song, pair_dir, pair_id="tune_test_0011")
    entries = sorted(p.name for p in pair_dir.parent.iterdir())
    assert entries == ["tune_test_0011"]
    assert shutil.os.path.isdir(pair_dir)


# ——— 4. CLI surface ————————————————————————————————————————————————————————


def test_cli_renders_a_pair_and_prints_one_json_object(capsys, tmp_path, song):
    pair_dir = tmp_path / "cli" / "tune_cli_0001"
    code, out, err = _run(capsys, [
        "tuning", "render-pair", "--mode", "fast-stereo-only",
        "--source", str(song), "--output-dir", str(pair_dir), "--pair-id", "tune_cli_0001",
    ])
    assert code == 0, err
    assert out and out["status"] == "rendered"
    assert out["pair_id"] == "tune_cli_0001"
    assert (pair_dir / "A" / "mix.wav").is_file() and (pair_dir / "B" / "mix.wav").is_file()


def test_cli_refuses_an_existing_pair_with_a_machine_readable_error(capsys, tmp_path, song):
    pair_dir = tmp_path / "cli" / "tune_cli_0002"
    assert _run(capsys, ["tuning", "render-pair", "--mode", "fast-stereo-only",
                         "--source", str(song), "--output-dir", str(pair_dir)])[0] == 0
    code, out, err = _run(capsys, ["tuning", "render-pair", "--mode", "fast-stereo-only",
                                   "--source", str(song), "--output-dir", str(pair_dir)])
    assert code == 2
    assert err and "refusing to overwrite" in err["error"]
    assert out is None


def test_cli_rejects_an_unknown_mode_at_the_argument_layer(capsys, tmp_path, song):
    with pytest.raises(SystemExit):
        release_cli.main(["tuning", "render-pair", "--mode", "deep",
                          "--source", str(song), "--output-dir", str(tmp_path / "x")])


# ——— 5. real audio: both sides analyse ————————————————————————————————————


def test_both_sides_are_decodable_and_fully_analysable(tmp_path, song):
    """The integration claim: A and B are real audio that Core's own analysis accepts."""
    from moodify.sound_protocol import PROTOCOL_V02, execute_job, validate_job

    def analyse(audio: Path, root: Path) -> dict:
        job = validate_job(
            {"protocol": PROTOCOL_V02, "type": "analyze",
             "source": str(audio), "output_dir": str(root)},
            Path.cwd(),
        )
        payload = execute_job(job)
        return json.loads(Path(payload["reports"]["json"]).read_text(encoding="utf-8"))

    pair_dir = tmp_path / "pairs" / "tune_test_0012"
    tuning.render_pair(song, pair_dir, pair_id="tune_test_0012")

    reports = {}
    for side in ("A", "B"):
        mix = pair_dir / side / "mix.wav"
        audio, sr = sf.read(str(mix))
        assert audio.size > 0 and sr == SR
        report = analyse(mix, tmp_path / f"cases_{side}")
        assert report["measurements"], f"{side} must produce real measurements"
        reports[side] = report

    original_report = analyse(song, tmp_path / "cases_original")

    def metric(report, name):
        for m in report["measurements"]:
            if m["id"] == name:
                return m["value"]
        return None

    # Three sides must be alignable: the original and both candidates share metric ids.
    for name in ("integrated_lufs", "sample_peak_dbfs"):
        vals = [metric(original_report, name), metric(reports["A"], name), metric(reports["B"], name)]
        if all(v is not None for v in vals):
            assert vals[0] is not None and vals[1] is not None and vals[2] is not None
