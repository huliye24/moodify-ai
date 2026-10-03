"""CLI-first A/B compare for a finishing case (``moodify compare …``).

Covers the machine contract the Studio shell and any agent depend on:
prepare builds a measured, hash-pinned comparison artifact; choose appends a
human decision to an append-only ledger; both refuse — with a stable code and
exit code — instead of reporting a success they did not achieve.
"""

import hashlib
import json
from pathlib import Path

import numpy as np
import pytest
import soundfile as sf

from moodify import ab_compare, release_cli
from moodify.mix_graph.graph import load_graph
from moodify.mix_graph.session import run_session

pytestmark = pytest.mark.v01


# ——— fixtures ————————————————————————————————————————————————————————————


def _write_wav(path: Path, seconds: float = 2.0, freq: float = 440.0,
               amplitude: float = 0.25) -> Path:
    sr = 22050
    t = np.arange(int(sr * seconds)) / sr
    wave = (np.sin(2 * np.pi * freq * t) * amplitude).astype(np.float32)
    sf.write(path, np.column_stack([wave, wave]), sr, subtype="PCM_16")
    return path


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _as_json_object(text: str) -> dict | None:
    """Parse a stream only when it *is* one JSON object; warnings stay text."""
    stripped = text.strip()
    if not (stripped.startswith("{") and stripped.endswith("}")):
        return None
    return json.loads(stripped)


class _CliResult:
    """One CLI invocation: exit code plus both captured streams, parsed once."""

    def __init__(self, code: int, out: str, err: str) -> None:
        self.code = code
        self.out = _as_json_object(out)
        self.err = _as_json_object(err)
        self.raw_out = out
        self.raw_err = err


def _run(capsys, argv) -> _CliResult:
    """Run the CLI with --json and read both streams exactly once.

    Only the *last* stderr line is parsed: decoder warnings from librosa are
    allowed to precede the one machine-readable error object.
    """
    code = release_cli.main(argv)
    captured = capsys.readouterr()
    err_lines = [line for line in captured.err.splitlines() if line.strip()]
    return _CliResult(code, captured.out.strip(),
                      err_lines[-1] if err_lines else "")


@pytest.fixture
def case_root(tmp_path):
    root = tmp_path / "cases"
    root.mkdir()
    return root


@pytest.fixture
def source_wav(tmp_path):
    return _write_wav(tmp_path / "source.wav")


@pytest.fixture
def a_case(case_root, source_wav):
    """A case directory exactly like the shell writes it: case.json carries
    the analyzed source hash, source_path.json records the file."""
    case_dir = case_root / "case_abtest"
    case_dir.mkdir()
    (case_dir / "case.json").write_text(json.dumps({
        "schema_version": "1.0",
        "case_id": "case_abtest",
        "source_id": "sha256:" + _sha256(source_wav),
        "lifecycle_state": "ANALYZED",
    }), encoding="utf-8")
    (case_dir / "source_path.json").write_text(
        json.dumps({"path": str(source_wav)}), encoding="utf-8")
    return case_dir


def _render_b(case_dir: Path, source: Path, preset: str = "clean_master") -> Path:
    """Produce B the way the product does: `finishing new` + render session."""
    finishing = case_dir / "finishing"
    finishing.mkdir(parents=True, exist_ok=True)
    graph_path = finishing / f"{source.stem}__{preset}__graph.json"
    assert release_cli.main(["finishing", "new", "--preset", preset,
                             "--source", str(source), "--out", str(graph_path)]) == 0
    result = run_session(load_graph(graph_path), finishing)
    return Path(result["output"]["path"])


@pytest.fixture
def rendered_case(a_case, source_wav, capsys):
    b_path = _render_b(a_case, source_wav)
    capsys.readouterr()  # drop `finishing new`'s stdout before the case under test
    return a_case, source_wav, b_path


# ——— prepare: happy path ———————————————————————————————————————————————


def test_prepare_ready_pins_both_sides_and_measures_loudness(rendered_case, capsys):
    case_dir, src, b_path = rendered_case
    res = _run(capsys, ["compare", "prepare", str(case_dir), "--json"])
    art = res.out

    assert res.code == 0
    assert art["status"] == "READY"
    assert art["schema"] == "moodify.ab_compare/0.1"
    assert art["decision_authority"] == "human"
    assert art["machine_verdict"] is None

    assert art["a"]["role"] == "source_before_finishing"
    assert art["a"]["path"] == str(src.resolve())
    assert art["a"]["sha256"] == _sha256(src)
    assert art["a"]["sha256_matches_case"] is True

    assert art["b"]["role"] == "rendered_after_finishing"
    assert art["b"]["path"] == str(b_path)
    assert art["b"]["sha256"] == _sha256(b_path)
    assert art["b"]["selection_rule"] == "newest_mtime"

    loud = art["loudness"]
    assert isinstance(loud["a_integrated_lufs"], float)
    assert isinstance(loud["b_integrated_lufs"], float)
    assert loud["delta_lu"] == pytest.approx(
        loud["b_integrated_lufs"] - loud["a_integrated_lufs"], abs=1e-3)
    # v0.1 measures only: no proxy is produced, so the honest value is NOT_MATCHED
    assert loud["matching_status"] == "NOT_MATCHED"
    assert loud["matched_proxy_available"] is False
    assert loud["threshold_status"] == "NO_CALIBRATED_THRESHOLD"
    assert loud["matching_threshold_lu"] is None

    assert art["geometry"]["sample_rate_match"] is True
    assert art["geometry"]["lengths_equal"] is True
    assert art["reasons"] == []

    assert (case_dir / "compare" / "ab_comparison.json").is_file()


def test_prepare_records_render_provenance_graph_and_evidence(rendered_case, capsys):
    case_dir, _src, b_path = rendered_case
    res = _run(capsys, ["compare", "prepare", str(case_dir), "--json"])
    assert res.code == 0
    art = res.out

    evidence = art["b"]["render_evidence"]
    assert evidence["available"] is True
    assert evidence["schema"] == "moodify.mix_graph.evidence/0.1"
    assert evidence["output_sha256"] == _sha256(b_path)
    assert evidence["output_sha256_matches_file"] is True
    assert evidence["path"].endswith(".evidence.json")

    graph = art["b"]["mix_graph"]
    assert graph["available"] is True
    assert graph["matched_by"] == "graph_digest"
    assert graph["graph_digest_sha256"] == evidence["graph_digest_sha256"]
    assert graph["preset"] == "clean_master"
    assert [n["type"] for n in graph["operator_chain"]]


def test_prepare_is_rerunnable_and_keeps_previous_timestamp(rendered_case, capsys):
    case_dir, _src, _b = rendered_case
    first = _run(capsys, ["compare", "prepare", str(case_dir), "--json"]).out
    second = _run(capsys, ["compare", "prepare", str(case_dir), "--json"]).out
    assert second["prepared_at"] >= first["prepared_at"]
    assert second["previous_prepared_at"] == first["prepared_at"]


def test_prepare_explicit_b_must_be_a_render_inside_the_case(rendered_case, capsys,
                                                             tmp_path):
    case_dir, _src, b_path = rendered_case
    outside = _write_wav(tmp_path / "elsewhere_mixgraph_aaaa.wav")
    res = _run(capsys, ["compare", "prepare", str(case_dir),
                        "--b", str(outside), "--json"])
    assert res.code == 2
    assert res.err["code"] == "B_OUTSIDE_CASE"

    res = _run(capsys, ["compare", "prepare", str(case_dir),
                        "--b", b_path.name, "--json"])
    assert res.code == 0
    assert res.out["b"]["selection_rule"] == "explicit"


def test_prepare_publishes_next_actions_for_an_agent(rendered_case, case_root, capsys):
    """`next_actions` routes an agent; it never carries a verdict."""
    res = _run(capsys, ["compare", "prepare", str(rendered_case[0]), "--json"])
    assert [a["action"] for a in res.out["next_actions"]] == [
        "HUMAN_LISTEN", "RECORD_CHOICE"]
    assert all("reason" in a for a in res.out["next_actions"])

    bare = case_root / "case_actions"
    bare.mkdir()
    (bare / "case.json").write_text(json.dumps({"case_id": "case_actions"}),
                                    encoding="utf-8")
    res = _run(capsys, ["compare", "prepare", str(bare), "--json"])
    assert [a["action"] for a in res.out["next_actions"]] == ["PROVIDE_SOURCE", "RENDER_B"]


# ——— prepare: honest failure states ————————————————————————————————————


def test_prepare_without_render_is_human_required(a_case, capsys):
    res = _run(capsys, ["compare", "prepare", str(a_case), "--json"])
    art = res.out
    assert res.code == 3
    assert art["status"] == "HUMAN_REQUIRED"
    assert art["human_required"] is True
    assert [r["code"] for r in art["reasons"]] == ["B_RENDER_MISSING"]
    assert art["b"] is None
    # the measured A is reported; the *reason* names the real cause
    assert art["loudness"]["unavailable_reason"] == "MISSING_SIDE:B"
    assert art["loudness"]["matching_status"] == "UNAVAILABLE"
    assert art["loudness"]["a_integrated_lufs"] is not None


def test_prepare_without_any_source_is_human_required(a_case, capsys):
    """No source_path.json and no finishing graph: A cannot be resolved."""
    (a_case / "source_path.json").unlink()
    res = _run(capsys, ["compare", "prepare", str(a_case), "--json"])
    assert res.code == 3
    assert res.out["status"] == "HUMAN_REQUIRED"
    assert res.out["a"] is None
    assert res.out["reasons"][0]["code"] == "A_SOURCE_UNRESOLVED"
    assert res.out["loudness"]["unavailable_reason"] == "MISSING_SIDE:A,B"


def test_prepare_falls_back_to_the_graph_source_when_the_record_is_gone(
        rendered_case, capsys):
    """The finishing graph records its own source — a moved source_path.json
    does not silently produce an uncompared pair."""
    case_dir, src, _b = rendered_case
    (case_dir / "source_path.json").unlink()
    res = _run(capsys, ["compare", "prepare", str(case_dir), "--json"])
    assert res.code == 0
    assert res.out["a"]["resolution_rule"] == "finishing_graph"
    assert res.out["a"]["path"] == str(src.resolve())
    assert res.out["a"]["sha256_matches_case"] is True


def test_prepare_refuses_a_source_that_is_not_the_analyzed_file(a_case, tmp_path,
                                                               capsys):
    other = _write_wav(tmp_path / "other.wav", freq=330.0)
    res = _run(capsys, ["compare", "prepare", str(a_case),
                        "--a", str(other), "--json"])
    assert res.code == 2
    assert res.err["code"] == "A_SOURCE_MISMATCH"


def test_prepare_reports_unreadable_b_audio_as_inconclusive(a_case, capsys):
    (a_case / "finishing").mkdir()
    (a_case / "finishing" / "broken_mixgraph_0000.wav").write_bytes(
        b"not a wav at all")
    res = _run(capsys, ["compare", "prepare", str(a_case), "--json"])
    assert res.code == 4
    assert res.out["status"] == "INCONCLUSIVE"
    assert res.out["b"]["measurement_failure"].startswith("AUDIO_UNREADABLE")
    assert res.out["loudness"]["matching_status"] == "UNAVAILABLE"


def test_prepare_reports_b_removed_after_render_as_human_required(a_case, source_wav,
                                                                  capsys):
    b_path = _render_b(a_case, source_wav)
    capsys.readouterr()
    b_path.unlink()
    res = _run(capsys, ["compare", "prepare", str(a_case), "--json"])
    assert res.code == 3
    assert res.out["status"] == "HUMAN_REQUIRED"
    assert "B_RENDER_MISSING" in [r["code"] for r in res.out["reasons"]]


def test_prepare_geometry_mismatch_is_inconclusive(a_case, capsys):
    """A render whose length differs cannot support a same-position switch."""
    finishing = a_case / "finishing"
    finishing.mkdir(parents=True, exist_ok=True)
    _write_wav(finishing / "short_mixgraph_0000.wav", seconds=1.0)
    res = _run(capsys, ["compare", "prepare", str(a_case), "--json"])
    assert res.code == 4
    assert res.out["status"] == "INCONCLUSIVE"
    assert res.out["geometry"]["lengths_equal"] is False
    assert "PAIR_GEOMETRY_MISMATCH" in [r["code"] for r in res.out["reasons"]]


# ——— prepare: path guards ———————————————————————————————————————————————


def test_prepare_rejects_unknown_case_directory(tmp_path, capsys):
    res = _run(capsys, ["compare", "prepare", str(tmp_path / "missing"), "--json"])
    assert res.code == 2
    assert res.raw_out == ""
    assert res.err["code"] == "CASE_NOT_FOUND"


def test_prepare_rejects_directory_that_is_not_a_case(tmp_path, capsys):
    plain = tmp_path / "plain"
    plain.mkdir()
    res = _run(capsys, ["compare", "prepare", str(plain), "--json"])
    assert res.code == 2
    assert res.err["code"] == "NOT_A_CASE"


def test_prepare_enforces_the_cases_root(a_case, tmp_path, capsys):
    res = _run(capsys, ["compare", "prepare", str(a_case),
                        "--cases-root", str(tmp_path / "other"), "--json"])
    assert res.code == 2
    assert res.err["code"] == "CASE_OUTSIDE_ROOT"


# ——— choose ————————————————————————————————————————————————————————————


def test_choose_records_a_and_b_with_evidence_references(rendered_case, capsys):
    case_dir, src, b_path = rendered_case
    art = _run(capsys, ["compare", "prepare", str(case_dir), "--json"]).out

    res = _run(capsys, ["compare", "choose", str(case_dir), "--keep", "A",
                        "--role", "creator", "--json"])
    assert res.code == 0
    first = res.out
    assert first["status"] == "recorded"
    assert first["keep"] == "A" and first["kept"] == "source"
    assert first["role"] == "creator"
    assert first["count"] == 1
    assert first["loudness_matched"] is False

    res = _run(capsys, ["compare", "choose", str(case_dir), "--keep", "B",
                        "--role", "listener", "--notes", "B 更清晰", "--json"])
    assert res.code == 0
    second = res.out
    assert second["kept"] == "rendered"
    assert second["count"] == 2  # append-only: the first record survives

    ledger = case_dir / "compare" / "ab_choices.jsonl"
    entries = [json.loads(line) for line in
               ledger.read_text(encoding="utf-8").splitlines() if line.strip()]
    assert [e["keep"] for e in entries] == ["A", "B"]
    assert [e["kept"] for e in entries] == ["source", "rendered"]
    assert all(e["reviewer_kind"] == "human" for e in entries)

    entry = entries[1]
    assert entry["schema"] == "moodify.ab_compare.choice/0.1"
    assert entry["choice_id"].startswith("abch_")
    assert entry["notes"] == "B 更清晰"
    assert entry["evidence"]["comparison_path"] == str(
        case_dir / "compare" / "ab_comparison.json")
    assert entry["evidence"]["comparison_sha256"] == _sha256(
        case_dir / "compare" / "ab_comparison.json")
    assert entry["evidence"]["a_sha256"] == _sha256(src)
    assert entry["evidence"]["b_sha256"] == _sha256(b_path)
    assert entry["evidence"]["graph_digest_sha256"] == art["b"]["mix_graph"][
        "graph_digest_sha256"]
    assert entry["evidence"]["preset"] == "clean_master"
    assert entry["evidence"]["render_evidence_path"] == art["b"][
        "render_evidence"]["path"]
    assert entry["loudness"]["matching_status"] == "NOT_MATCHED"


def test_choose_requires_a_choice_and_role_inside_the_closed_sets(a_case, capsys):
    with pytest.raises(ab_compare.CompareError) as bad_keep:
        ab_compare.record_choice(a_case, keep="C", role="creator")
    assert bad_keep.value.code == "BAD_KEEP"

    with pytest.raises(ab_compare.CompareError) as bad_role:
        ab_compare.record_choice(a_case, keep="A", role="boss")
    assert bad_role.value.code == "BAD_ROLE"

    # the CLI rejects both before doing any work, with argparse's exit 2
    for argv in (["compare", "choose", str(a_case), "--keep", "C", "--role", "creator"],
                 ["compare", "choose", str(a_case), "--keep", "A", "--role", "boss"]):
        with pytest.raises(SystemExit) as refused:
            release_cli.main(argv)
        assert refused.value.code == 2
        capsys.readouterr()


def test_choose_before_prepare_is_refused(a_case, capsys):
    res = _run(capsys, ["compare", "choose", str(a_case), "--keep", "A",
                        "--role", "creator", "--json"])
    assert res.code == 2
    assert res.out is None
    assert res.err["code"] == "COMPARISON_NOT_PREPARED"
    assert not (a_case / "compare" / "ab_choices.jsonl").exists()


def test_choose_is_refused_while_the_artifact_is_not_ready(a_case, capsys):
    _run(capsys, ["compare", "prepare", str(a_case), "--json"])  # no B -> HUMAN_REQUIRED
    res = _run(capsys, ["compare", "choose", str(a_case), "--keep", "A",
                        "--role", "creator", "--json"])
    assert res.code == 3
    assert res.err["status"] == "HUMAN_REQUIRED"
    assert "B_RENDER_MISSING" in [r["code"] for r in res.err["reasons"]]
    assert not (a_case / "compare" / "ab_choices.jsonl").exists()


def test_choose_refuses_a_pair_that_changed_since_prepare(rendered_case, capsys):
    case_dir, _src, b_path = rendered_case
    _run(capsys, ["compare", "prepare", str(case_dir), "--json"])
    b_path.write_bytes(b_path.read_bytes() + b"\x00")  # render replaced on disk

    res = _run(capsys, ["compare", "choose", str(case_dir), "--keep", "B",
                        "--role", "listener", "--json"])
    assert res.code == 2
    assert res.err["code"] == "COMPARISON_STALE"
    assert not (case_dir / "compare" / "ab_choices.jsonl").exists()


def test_choose_refuses_when_a_recorded_file_is_gone(rendered_case, capsys):
    case_dir, _src, b_path = rendered_case
    _run(capsys, ["compare", "prepare", str(case_dir), "--json"])
    b_path.unlink()
    res = _run(capsys, ["compare", "choose", str(case_dir), "--keep", "B",
                        "--role", "listener", "--json"])
    assert res.code == 2
    assert res.err["code"] == "B_FILE_GONE"


def test_choose_request_id_makes_a_retry_idempotent(rendered_case, capsys):
    case_dir, _src, _b = rendered_case
    _run(capsys, ["compare", "prepare", str(case_dir), "--json"])
    argv = ["compare", "choose", str(case_dir), "--keep", "B", "--role", "creator",
            "--request-id", "agent-run-7-call-3", "--json"]

    res = _run(capsys, argv)
    assert res.code == 0 and res.out["count"] == 1

    res = _run(capsys, argv)  # the same request re-sent
    assert res.code == 2
    assert res.err["code"] == "DUPLICATE_REQUEST"
    assert ab_compare._count_choices(case_dir) == 1  # nothing was appended

    res = _run(capsys, ["compare", "choose", str(case_dir), "--keep", "B",
                        "--role", "creator", "--request-id", "agent-run-7-call-4",
                        "--json"])
    assert res.code == 0 and res.out["count"] == 2


def test_choose_rejects_an_empty_request_id(rendered_case, capsys):
    case_dir, _src, _b = rendered_case
    _run(capsys, ["compare", "prepare", str(case_dir), "--json"])
    res = _run(capsys, ["compare", "choose", str(case_dir), "--keep", "A",
                        "--role", "creator", "--request-id", "   ", "--json"])
    assert res.code == 2
    assert res.err["code"] == "BAD_REQUEST_ID"


# ——— show ——————————————————————————————————————————————————————————————


def test_show_returns_artifact_freshness_and_ledger_count(rendered_case, capsys):
    case_dir, _src, _b = rendered_case
    _run(capsys, ["compare", "prepare", str(case_dir), "--json"])
    _run(capsys, ["compare", "choose", str(case_dir), "--keep", "A",
                  "--role", "pro", "--json"])

    res = _run(capsys, ["compare", "show", str(case_dir), "--json"])
    assert res.code == 0
    assert res.out["status"] == "READY"
    assert res.out["freshness"]["a_matches_artifact"] is True
    assert res.out["freshness"]["b_matches_artifact"] is True
    assert res.out["freshness"]["choice_count"] == 1
    assert res.out["freshness"]["artifact_sha256"] == _sha256(
        case_dir / "compare" / "ab_comparison.json")


def test_show_before_prepare_is_refused(a_case, capsys):
    res = _run(capsys, ["compare", "show", str(a_case), "--json"])
    assert res.code == 2
    assert res.err["code"] == "COMPARISON_NOT_PREPARED"


def test_show_flags_a_pair_changed_after_prepare(rendered_case, capsys):
    case_dir, _src, b_path = rendered_case
    _run(capsys, ["compare", "prepare", str(case_dir), "--json"])
    b_path.write_bytes(b_path.read_bytes() + b"\x00")
    res = _run(capsys, ["compare", "show", str(case_dir), "--json"])
    assert res.code == 0  # reading is still possible — the staleness is the fact
    assert res.out["freshness"]["b_matches_artifact"] is False
    assert res.out["freshness"]["a_matches_artifact"] is True


# ——— machine interface ——————————————————————————————————————————————————


@pytest.mark.parametrize("argv_tail", [["prepare"], ["show"]])
def test_stdout_is_exactly_one_json_object_with_or_without_the_flag(
        rendered_case, capsys, argv_tail):
    case_dir, _src, _b = rendered_case
    release_cli.main(["compare", "prepare", str(case_dir), "--json"])
    capsys.readouterr()
    code = release_cli.main(["compare", *argv_tail, str(case_dir)])
    captured = capsys.readouterr()
    assert code in (0, 3, 4)
    json.loads(captured.out)  # single parseable JSON document on stdout
    assert captured.out.strip().count("\n") == 0  # not a stream of objects
    assert captured.err.strip()  # the human digest stays on stderr


def test_choose_stdout_is_one_json_object_with_human_digest_on_stderr(rendered_case,
                                                                      capsys):
    case_dir, _src, _b = rendered_case
    release_cli.main(["compare", "prepare", str(case_dir)])
    capsys.readouterr()
    code = release_cli.main(["compare", "choose", str(case_dir), "--keep", "B",
                            "--role", "creator"])
    captured = capsys.readouterr()
    assert code == 0
    payload = json.loads(captured.out)
    assert payload["status"] == "recorded"
    assert "已记录" in captured.err


def test_prepare_exit_codes_match_the_reported_status(rendered_case, case_root,
                                                      source_wav, capsys):
    """0 READY · 2 refused · 3 HUMAN_REQUIRED."""
    bare = case_root / "case_norender"
    bare.mkdir()
    (bare / "case.json").write_text(json.dumps({"case_id": "case_norender"}),
                                    encoding="utf-8")

    assert release_cli.main(["compare", "prepare", str(rendered_case[0])]) == 0
    capsys.readouterr()
    assert release_cli.main(["compare", "prepare", str(bare)]) == 3
    capsys.readouterr()
    assert release_cli.main(["compare", "prepare", str(case_root / "nope")]) == 2
    capsys.readouterr()
