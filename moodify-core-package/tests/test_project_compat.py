"""Case ↔ Project Model compatibility bridge — read-only guarantees.

Covers the promises a compatibility reader must hold (THINKPAD 002):
recognised layouts are inspected without a single byte changing, recorded
hashes are verified against reality, missing artifacts are problems rather
than empty successes, tampering is loud, unknown layouts and unknown schema
versions are refused rather than guessed, and the normalized output is
deterministic.

The committed fixtures under ``tests/fixtures/case_compat/`` are the tiny
synthetic states; ``examples/golden_case/`` is a real historical case with
real recorded hashes and is exercised directly (read-only).
"""

from __future__ import annotations

import hashlib
import json
import shutil
from pathlib import Path

import pytest

from moodify.project import (
    LAYOUT_CORE_CASE,
    LAYOUT_LEGACY_WSE,
    LAYOUT_PROJECT,
    LAYOUT_STUDIO_CASE,
    STATUS_CORRUPT,
    STATUS_INCOMPLETE,
    STATUS_RECOGNIZED,
    STATUS_UNSUPPORTED,
    create_project,
    detect_layout,
    inspect_case,
)
from moodify.project.compat import _norm_sha  # exercised directly below
from moodify.project.errors import ProjectValidationError

FIXTURES = Path(__file__).parent / "fixtures" / "case_compat"
REPO_ROOT = Path(__file__).resolve().parents[2]
GOLDEN_CASE = REPO_ROOT / "examples" / "golden_case"


# ── helpers ───────────────────────────────────────────────────────────────────

def _copy_fixture(name: str, tmp_path: Path) -> Path:
    target = tmp_path / name
    shutil.copytree(FIXTURES / name, target)
    return target


def _snapshot(root: Path) -> dict[str, str]:
    out = {}
    for path in sorted(root.rglob("*")):
        if path.is_file():
            out[path.relative_to(root).as_posix()] = hashlib.sha256(
                path.read_bytes()).hexdigest()
    return out


def _read(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _write(path: Path, payload: dict) -> None:
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def _problem_codes(inspection) -> set[str]:
    return {p.code for p in inspection.problems}


def _all_logical_paths(inspection) -> list[str]:
    paths = [a.logical_path for refs in inspection.sections.values() for a in refs]
    if inspection.source is not None and inspection.source.logical_path:
        paths.append(inspection.source.logical_path)
    return paths


# ── A. layout detection ───────────────────────────────────────────────────────

def test_detect_layout_project(tmp_path):
    src = tmp_path / "song.m4a"
    src.write_bytes(b"fixture-bytes")
    manifest = create_project(src, tmp_path / "projects")
    root = tmp_path / "projects" / manifest.project_id
    assert detect_layout(root) == LAYOUT_PROJECT


def test_detect_layout_core_case():
    assert detect_layout(FIXTURES / "core_case_analyzed") == LAYOUT_CORE_CASE


def test_detect_layout_studio_case():
    assert detect_layout(FIXTURES / "studio_case") == LAYOUT_STUDIO_CASE


def test_detect_layout_legacy_wse():
    assert detect_layout(FIXTURES / "legacy_source_only") == LAYOUT_LEGACY_WSE


def test_detect_layout_unknown_is_none(tmp_path):
    (tmp_path / "random.txt").write_text("not a case", encoding="utf-8")
    assert detect_layout(tmp_path) is None


def test_inspect_rejects_non_directory(tmp_path):
    with pytest.raises(ProjectValidationError):
        inspect_case(tmp_path / "does-not-exist")


# ── B. recognized layouts ─────────────────────────────────────────────────────

def test_project_layout_is_recognized_and_source_verified(tmp_path):
    src = tmp_path / "song.m4a"
    src.write_bytes(b"fixture-bytes")
    manifest = create_project(src, tmp_path / "projects")
    root = tmp_path / "projects" / manifest.project_id

    inspection = inspect_case(root)
    assert inspection.status == STATUS_RECOGNIZED
    assert inspection.layout == LAYOUT_PROJECT
    assert inspection.case_id == manifest.project_id
    assert inspection.source is not None
    assert inspection.source.origin == "project_copy"
    assert inspection.source.verified is True
    assert inspection.source.recorded_sha256 == manifest.source.content_hash
    assert not inspection.problems


def test_core_case_fixture_is_recognized(tmp_path):
    inspection = inspect_case(FIXTURES / "core_case_analyzed")
    assert inspection.status == STATUS_RECOGNIZED
    assert inspection.layout == LAYOUT_CORE_CASE
    assert inspection.case_id == "case_11111111111111111111111111111111"
    # record-only source: the digest is preserved, nothing is invented
    assert inspection.source is not None
    assert inspection.source.origin == "case_record"
    assert inspection.source.verified is None
    refs = {a.logical_path: a for a in inspection.sections["analysis"]}
    assert refs["report.json"].exists is True
    assert refs["scan/metrics.json"].verified is True  # recorded hash matches
    assert refs["scan/metrics.json"].recorded_sha256.startswith("sha256:")


def test_studio_fixture_normalizes_every_vocabulary_section():
    inspection = inspect_case(FIXTURES / "studio_case")
    assert inspection.status == STATUS_RECOGNIZED
    assert inspection.layout == LAYOUT_STUDIO_CASE
    assert inspection.case_id == "case_22222222222222222222222222222222"

    refs = {name: {a.logical_path for a in section}
            for name, section in inspection.sections.items() if section}
    assert "stems/vocals.m4a" in refs["stems"]
    assert "stems/manifest.json" in refs["stems"]
    assert "midi/lead.mid" in refs["transcription"]
    assert "score/lead.musicxml" in refs["score"]
    assert "studio/diagnosis.json" in refs["session"]
    assert "studio/selection.json" in refs["session"]
    assert "studio/plans/context_plan.json" in refs["session"]
    # human decisions and derived records are surfaced as unknowns, not re-derived
    assert any("finish_mode.json" in u for u in inspection.unknowns)
    assert any("selection.json" in u for u in inspection.unknowns)
    assert any("pipeline.json" in u for u in inspection.unknowns)
    assert any("ab_choices.jsonl records 1" in u for u in inspection.unknowns)
    # the separator's own grade boundary travels with the data
    assert any("grade boundary" in u for u in inspection.unknowns)
    assert any(a.logical_path.endswith("render.m4a") for a in inspection.sections["renders"])
    assert any(a.logical_path.endswith("ab_comparison.json")
               for a in inspection.sections["verification"])


# ── C. source-only / incomplete states ────────────────────────────────────────

def test_source_only_layout_is_recognized_without_records(tmp_path):
    inspection = inspect_case(FIXTURES / "legacy_source_only")
    assert inspection.status == STATUS_RECOGNIZED
    assert inspection.layout == LAYOUT_LEGACY_WSE
    assert inspection.source is not None
    assert inspection.source.origin == "in_case"
    assert inspection.source.verified is None  # nothing recorded to verify against
    assert inspection.sections["analysis"] == ()


def test_active_case_without_report_is_incomplete():
    inspection = inspect_case(FIXTURES / "core_case_active")
    assert inspection.status == STATUS_INCOMPLETE
    assert "ANALYSIS_NOT_COMPLETED" in _problem_codes(inspection)


def test_case_record_without_either_file_is_unsupported(tmp_path):
    (tmp_path / "50_something").mkdir()
    inspection = inspect_case(tmp_path)
    assert inspection.status == STATUS_UNSUPPORTED
    assert "UNSUPPORTED_LAYOUT" in _problem_codes(inspection)


# ── D. missing and tampered artifacts ─────────────────────────────────────────

def test_missing_project_source_is_corrupt(tmp_path):
    src = tmp_path / "song.m4a"
    src.write_bytes(b"fixture-bytes")
    manifest = create_project(src, tmp_path / "projects")
    root = tmp_path / "projects" / manifest.project_id
    (root / manifest.source.logical_path).unlink()

    inspection = inspect_case(root)
    assert inspection.status == STATUS_CORRUPT
    assert "PROJECT_SOURCE_UNVERIFIED" in _problem_codes(inspection)


def test_tampered_project_source_is_corrupt(tmp_path):
    src = tmp_path / "song.m4a"
    src.write_bytes(b"fixture-bytes")
    manifest = create_project(src, tmp_path / "projects")
    root = tmp_path / "projects" / manifest.project_id
    copy = root / manifest.source.logical_path
    copy.write_bytes(copy.read_bytes() + b"x")

    inspection = inspect_case(root)
    assert inspection.status == STATUS_CORRUPT
    assert "PROJECT_SOURCE_UNVERIFIED" in _problem_codes(inspection)


def test_tampered_scan_artifact_is_corrupt(tmp_path):
    root = _copy_fixture("core_case_analyzed", tmp_path)
    metrics = root / "scan" / "metrics.json"
    metrics.write_bytes(metrics.read_bytes() + b"x")

    inspection = inspect_case(root)
    assert inspection.status == STATUS_CORRUPT
    assert "ARTIFACT_TAMPERED" in _problem_codes(inspection)
    tampered = [a for a in inspection.sections["analysis"]
                if a.logical_path == "scan/metrics.json"][0]
    assert tampered.verified is False


def test_missing_recorded_artifact_is_incomplete_not_corrupt(tmp_path):
    root = _copy_fixture("core_case_analyzed", tmp_path)
    (root / "scan" / "metrics.json").unlink()

    inspection = inspect_case(root)
    assert inspection.status == STATUS_INCOMPLETE
    assert "ARTIFACT_MISSING" in _problem_codes(inspection)
    missing = [a for a in inspection.sections["analysis"]
               if a.logical_path == "scan/metrics.json"][0]
    assert missing.exists is False


def test_missing_optional_artifact_does_not_invalidate(tmp_path):
    root = _copy_fixture("core_case_analyzed", tmp_path)
    (root / "measurements.json").unlink()  # optional: report.json still identifies

    inspection = inspect_case(root)
    assert inspection.status == STATUS_RECOGNIZED


def test_studio_reader_verifies_external_source_when_path_resolves(tmp_path):
    root = _copy_fixture("studio_case", tmp_path)
    source = tmp_path / "source.m4a"
    source.write_bytes(b"the real source")
    digest = hashlib.sha256(source.read_bytes()).hexdigest()
    _write(root / "source_path.json", {"path": str(source)})

    # recorded digest in the fixtures is 2222…22 — a mismatch must be loud
    incomplete = inspect_case(root)
    assert incomplete.status == STATUS_CORRUPT
    assert "SOURCE_HASH_MISMATCH" in _problem_codes(incomplete)

    # point every source-digest record at the true digest → verified, recognized
    case = _read(root / "case.json")
    case["source_id"] = f"sha256:{digest}"
    _write(root / "case.json", case)
    report = _read(root / "report.json")
    report["source"]["sha256"] = f"sha256:{digest}"
    _write(root / "report.json", report)
    stems = _read(root / "stems" / "manifest.json")
    stems["source_sha256"] = digest  # bare hex, like the real manifest
    _write(root / "stems" / "manifest.json", stems)

    verified = inspect_case(root)
    assert verified.source is not None
    assert verified.source.verified is True
    assert verified.status == STATUS_RECOGNIZED


def test_stale_source_path_is_unknown_not_fatal(tmp_path):
    root = _copy_fixture("studio_case", tmp_path)
    _write(root / "source_path.json", {"path": str(tmp_path / "gone.m4a")})

    inspection = inspect_case(root)
    assert inspection.status == STATUS_RECOGNIZED
    assert inspection.source is not None and inspection.source.verified is None
    assert any("no longer exists" in u for u in inspection.unknowns)


# ── E. partial deep path / extra files ────────────────────────────────────────

def test_partial_deep_artifacts_are_reported_as_absent_not_guessed(tmp_path):
    root = _copy_fixture("studio_case", tmp_path)
    shutil.rmtree(root / "stems")
    shutil.rmtree(root / "midi")
    shutil.rmtree(root / "score")

    inspection = inspect_case(root)
    assert inspection.status == STATUS_RECOGNIZED
    assert inspection.sections["stems"] == ()
    assert inspection.sections["transcription"] == ()
    assert inspection.sections["score"] == ()
    # renders/selection remain visible — a partial deep path is not a broken case
    assert any(a.logical_path.endswith("render.m4a") for a in inspection.sections["renders"])


def test_extra_unknown_files_do_not_invalidate(tmp_path):
    root = _copy_fixture("core_case_analyzed", tmp_path)
    (root / "notes.txt").write_text("human scratch", encoding="utf-8")
    (root / "scratch" ).mkdir()
    (root / "scratch" / "later.json").write_text("{}", encoding="utf-8")

    inspection = inspect_case(root)
    assert inspection.status == STATUS_RECOGNIZED
    assert inspection.ignored_file_count == 2
    assert "notes.txt" in inspection.ignored_files


# ── F. traversal ──────────────────────────────────────────────────────────────

def test_recorded_artifact_path_cannot_escape_the_case(tmp_path):
    root = _copy_fixture("core_case_analyzed", tmp_path)
    outside = tmp_path / "outside.m4a"
    outside.write_bytes(b"do not touch")
    outside_before = outside.read_bytes()

    manifest = _read(root / "scan" / "scan_manifest.json")
    manifest["artifacts"]["sneaky"] = {
        "path": "..\\..\\..\\outside.m4a",
        "sha256": hashlib.sha256(outside_before).hexdigest(),
    }
    _write(root / "scan" / "scan_manifest.json", manifest)

    inspection = inspect_case(root)
    # the recorded path is reduced to a basename: nothing outside is read or hashed
    assert outside.read_bytes() == outside_before
    for logical in _all_logical_paths(inspection):
        assert ".." not in logical.split("/")
        assert not Path(logical).is_absolute()
    assert "ARTIFACT_MISSING" in _problem_codes(inspection)  # scan/sneaky.m4a absent


# ── G. read-only and deterministic ────────────────────────────────────────────

def test_repeated_reads_do_not_change_any_byte(tmp_path):
    root = _copy_fixture("studio_case", tmp_path)
    before = _snapshot(root)
    inspect_case(root)
    inspect_case(root)
    assert _snapshot(root) == before


def test_repeated_reads_do_not_change_the_legacy_golden_case():
    before = _snapshot(GOLDEN_CASE)
    inspect_case(GOLDEN_CASE)
    assert _snapshot(GOLDEN_CASE) == before


def test_normalized_output_is_deterministic():
    first = json.dumps(inspect_case(FIXTURES / "studio_case").to_dict(), sort_keys=True)
    second = json.dumps(inspect_case(FIXTURES / "studio_case").to_dict(), sort_keys=True)
    third = json.dumps(inspect_case(FIXTURES / "studio_case").to_dict(), sort_keys=True)
    assert first == second == third


def test_reader_does_not_modify_the_project_manifest(tmp_path):
    src = tmp_path / "song.m4a"
    src.write_bytes(b"fixture-bytes")
    manifest = create_project(src, tmp_path / "projects")
    root = tmp_path / "projects" / manifest.project_id
    manifest_bytes = (root / "project.json").read_bytes()

    inspection = inspect_case(root)
    assert inspection.status == STATUS_RECOGNIZED
    assert (root / "project.json").read_bytes() == manifest_bytes


# ── H. unknowns stay unknown, conflicts are loud ──────────────────────────────

def test_unknown_case_schema_version_is_flagged_not_accepted(tmp_path):
    root = _copy_fixture("core_case_analyzed", tmp_path)
    case = _read(root / "case.json")
    case["schema_version"] = "2.0"
    _write(root / "case.json", case)

    inspection = inspect_case(root)
    assert inspection.status == STATUS_RECOGNIZED  # loud, but not corrupt
    assert any("schema_version '2.0'" in u for u in inspection.unknowns)


def test_unknown_studio_schema_is_flagged_not_interpreted(tmp_path):
    root = _copy_fixture("studio_case", tmp_path)
    diagnosis = _read(root / "studio" / "diagnosis.json")
    diagnosis["schema"] = "moodify.studio.diagnosis/0.9"
    _write(root / "studio" / "diagnosis.json", diagnosis)

    inspection = inspect_case(root)
    assert any("diagnosis/0.9" in u for u in inspection.unknowns)


def test_conflicting_source_digests_are_corrupt(tmp_path):
    root = _copy_fixture("core_case_analyzed", tmp_path)
    report = _read(root / "report.json")
    report["source"]["sha256"] = "sha256:" + "9" * 64
    _write(root / "report.json", report)

    inspection = inspect_case(root)
    assert inspection.status == STATUS_CORRUPT
    assert "SOURCE_HASH_CONFLICT" in _problem_codes(inspection)


def test_conflicting_case_ids_are_corrupt(tmp_path):
    root = _copy_fixture("core_case_analyzed", tmp_path)
    report = _read(root / "report.json")
    report["case"]["case_id"] = "case_" + "9" * 32
    _write(root / "report.json", report)

    inspection = inspect_case(root)
    assert inspection.status == STATUS_CORRUPT
    assert "CASE_ID_CONFLICT" in _problem_codes(inspection)


def test_norm_sha_normalizes_both_recorded_formats():
    bare = "a" * 64
    prefixed = "sha256:" + "A" * 64
    assert _norm_sha(bare) == "sha256:" + bare
    assert _norm_sha(prefixed) == "sha256:" + "a" * 64
    assert _norm_sha("not-a-digest") is None
    assert _norm_sha(None) is None


# ── I. the real historical golden case ────────────────────────────────────────

def test_golden_case_source_and_candidates_verify():
    inspection = inspect_case(GOLDEN_CASE)
    assert inspection.layout == LAYOUT_LEGACY_WSE
    assert inspection.case_id == "case_00000000000000000000000000000001"
    assert inspection.source is not None
    assert inspection.source.verified is True  # e8e61fea… recorded in 3 places

    candidates = [a for a in inspection.sections["renders"]
                  if a.kind == "renders.candidate_audio"]
    assert len(candidates) == 3
    assert all(a.verified is True for a in candidates)


def test_golden_case_reports_its_missing_recorded_spectra():
    """8 spectra PNGs are recorded but absent on disk (historic .gitignore loss).

    The reader must report them rather than silently succeed — "missing" is not
    "fine". This is the honest state of the repository's own golden case.
    """
    inspection = inspect_case(GOLDEN_CASE)
    assert inspection.status == STATUS_INCOMPLETE
    missing = [a for a in inspection.sections["analysis"]
               if not a.exists and a.kind == "analysis.scan_artifact"]
    assert len(missing) == 8
    assert {a.code for a in inspection.problems} == {"ARTIFACT_MISSING"}


def test_golden_case_tamper_is_detected(tmp_path):
    root = tmp_path / "golden"
    shutil.copytree(GOLDEN_CASE, root)
    candidate = root / "03_candidates" / "candidate_A.wav"
    candidate.write_bytes(candidate.read_bytes() + b"x")

    inspection = inspect_case(root)
    assert inspection.status == STATUS_CORRUPT
    assert "ARTIFACT_TAMPERED" in _problem_codes(inspection)


# ── J. CLI ────────────────────────────────────────────────────────────────────

def test_cli_inspect_legacy_prints_one_json_object(capsys):
    from moodify.release_cli import main

    rc = main(["project", "inspect-legacy", str(FIXTURES / "core_case_analyzed"),
               "--json"])
    captured = capsys.readouterr()
    assert rc == 0
    payload = json.loads(captured.out)
    assert payload["status"] == STATUS_RECOGNIZED
    assert payload["case_id"] == "case_11111111111111111111111111111111"
    assert captured.err == ""  # --json suppresses the human digest


def test_cli_inspect_legacy_exit_codes(capsys, tmp_path):
    from moodify.release_cli import main

    rc = main(["project", "inspect-legacy", str(FIXTURES / "core_case_active")])
    captured = capsys.readouterr()
    assert rc == 0  # incomplete is an answer
    assert "INCOMPLETE" in captured.err
    json.loads(captured.out)

    rc = main(["project", "inspect-legacy", str(tmp_path)])
    captured = capsys.readouterr()
    assert rc == 2  # unsupported is a refusal
    assert json.loads(captured.out)["status"] == STATUS_UNSUPPORTED

    rc = main(["project", "inspect-legacy", str(tmp_path / "missing")])
    captured = capsys.readouterr()
    assert rc == 2
    assert json.loads(captured.err)["status"] == "error"
