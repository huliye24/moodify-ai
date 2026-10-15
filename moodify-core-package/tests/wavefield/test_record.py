"""Case layout, append-only decisions, export and reproducibility."""

from __future__ import annotations

import json

import pytest

from moodify.wavefield import record
from moodify.wavefield.models import FieldSpec
from moodify.wavefield.search import POLICY_ID, run_field_search


@pytest.fixture
def searched_case(case_dir, source_wav):
    run_field_search(case_dir, source_path=str(source_wav))
    return case_dir


# ---------------------------------------------------------------------------
# Layout
# ---------------------------------------------------------------------------


def test_the_lane_mounts_inside_the_existing_studio_subtree(case_dir):
    assert record.wavefield_dir(case_dir) == case_dir / "studio" / "wavefield"


def test_layout_matches_the_contract(case_dir, source_wav):
    run_field_search(case_dir, source_path=str(source_wav))
    root = record.wavefield_dir(case_dir)

    assert (root / "session.json").is_file()
    assert (root / "search.json").is_file()
    assert (root / "decisions.jsonl").is_file()
    for candidate_id in ("A", "B", "C"):
        assert (root / "candidates" / f"{candidate_id}.wav").is_file()
        assert (root / "fields" / f"{candidate_id}.json").is_file()
        assert (root / "renders" / f"{candidate_id}.json").is_file()
        assert (root / "hearing" / f"{candidate_id}.json").is_file()
    assert (root / "hearing" / "ORIGINAL.json").is_file()


def test_original_is_a_reference_to_the_source_and_not_duplicated(searched_case, source_wav):
    root = record.wavefield_dir(searched_case)
    original = json.loads((root / "hearing" / "ORIGINAL.json").read_text(encoding="utf-8"))

    assert original["is_reference"] is True
    assert original["provenance"]["source_sha256"] == record.sha256_file(source_wav)
    # no second copy of the original audio exists inside the lane
    lane_wavs = {p.name for p in root.rglob("*.wav")}
    assert lane_wavs == {"A.wav", "B.wav", "C.wav"}
    session = record.read_session(searched_case)
    assert session["source_path"] == str(source_wav)


def test_session_and_search_pin_the_policy_and_the_source(searched_case):
    session = record.read_session(searched_case)
    search = record.read_search(searched_case)
    assert session["policy_id"] == POLICY_ID
    assert session["calibration_status"] == "UNCALIBRATED_ENGINEERING_DEFAULT"
    assert search["policy_id"] == POLICY_ID
    assert [p["candidate_id"] for p in search["probes"]] == ["A", "B", "C"]


def test_fields_are_stored_per_candidate_and_revalidate(searched_case):
    for candidate_id in ("A", "B", "C"):
        spec = record.read_field(searched_case, candidate_id)
        assert isinstance(spec, FieldSpec)
        assert spec.field_id == f"field_{candidate_id}"
    assert record.read_field(searched_case, "Z") is None


def test_candidate_ids_are_guarded(case_dir):
    with pytest.raises(record.WaveFieldRecordError) as excinfo:
        record.candidate_path(case_dir, "../escape")
    assert excinfo.value.code == "BAD_CANDIDATE"


# ---------------------------------------------------------------------------
# Decisions
# ---------------------------------------------------------------------------


def test_only_original_and_the_three_probes_can_be_chosen(searched_case):
    for choice in ("ORIGINAL", "A", "B", "C"):
        record.append_decision(searched_case, kept=choice, role="creator",
                               request_id=f"req-{choice}")
    assert [row["kept"] for row in record.read_decisions(searched_case)] == [
        "ORIGINAL", "A", "B", "C",
    ]

    with pytest.raises(record.WaveFieldRecordError) as kept:
        record.append_decision(searched_case, kept="D", role="creator")
    assert kept.value.code == "BAD_KEPT"

    with pytest.raises(record.WaveFieldRecordError) as role:
        record.append_decision(searched_case, kept="A", role="admin")
    assert role.value.code == "BAD_ROLE"


def test_decisions_are_append_only(searched_case):
    record.append_decision(searched_case, kept="A", role="creator", request_id="r1")
    record.append_decision(searched_case, kept="C", role="listener", request_id="r2")

    rows = record.read_decisions(searched_case)
    assert [row["kept"] for row in rows] == ["A", "C"]
    assert record.decision_for(searched_case)["kept"] == "C"
    assert record.decision_for(searched_case, "r1")["kept"] == "A"

    lines = record.decisions_path(searched_case).read_text(encoding="utf-8").splitlines()
    assert len(lines) == 2, "each decision is exactly one line"
    assert record.decisions_path(searched_case).read_text(encoding="utf-8").endswith("\n")


def test_repeating_a_request_id_does_not_write_a_second_decision(searched_case):
    first = record.append_decision(searched_case, kept="B", role="pro", request_id="once")
    second = record.append_decision(searched_case, kept="B", role="pro", request_id="once")

    assert first["created"] is True
    assert second["created"] is False
    assert first["record"] == second["record"]
    assert len(record.read_decisions(searched_case)) == 1


def test_a_torn_line_does_not_invalidate_the_ledger(searched_case):
    record.append_decision(searched_case, kept="A", role="creator", request_id="r1")
    with record.decisions_path(searched_case).open("a", encoding="utf-8") as handle:
        handle.write('{"torn": \n')  # a partial write from an interrupted append
    record.append_decision(searched_case, kept="B", role="creator", request_id="r2")

    rows = record.read_decisions(searched_case)
    assert [row["kept"] for row in rows] == ["A", "B"]


def test_the_ledger_exists_and_is_empty_before_any_decision(searched_case):
    ledger = record.decisions_path(searched_case)
    assert ledger.is_file()
    assert ledger.read_text(encoding="utf-8") == ""
    assert record.read_decisions(searched_case) == []


# ---------------------------------------------------------------------------
# Export
# ---------------------------------------------------------------------------


def test_export_is_blocked_before_a_valid_choice(searched_case):
    with pytest.raises(record.WaveFieldRecordError) as excinfo:
        record.export_chosen(searched_case)
    assert excinfo.value.code == "NOT_CHOSEN"
    assert not (record.export_dir(searched_case) / "manifest.json").exists()


def test_export_refuses_a_choice_that_was_not_recorded(searched_case):
    record.append_decision(searched_case, kept="A", role="creator", request_id="r1")
    with pytest.raises(record.WaveFieldRecordError) as excinfo:
        record.export_chosen(searched_case, kept="C")
    assert excinfo.value.code == "NOT_CHOSEN"


def test_keeping_a_field_exports_the_render_with_hashes_and_the_manifest(searched_case):
    record.append_decision(searched_case, kept="C", role="creator", request_id="r1")
    manifest = record.export_chosen(searched_case)

    export_root = record.export_dir(searched_case)
    assert manifest["export_mode"] == "RENDERED_FIELD"
    assert (export_root / "chosen.wav").is_file()
    assert (export_root / "chosen_field.json").is_file()
    assert (export_root / "manifest.json").is_file()

    assert manifest["chosen_audio"] == str(export_root / "chosen.wav")
    assert manifest["chosen_audio_sha256"] == record.sha256_file(export_root / "chosen.wav")
    candidate_bytes = record.candidate_path(searched_case, "C").read_bytes()
    assert (export_root / "chosen.wav").read_bytes() == candidate_bytes
    assert manifest["chosen_field"]["parameters"]["room_size"] == 0.80
    assert len(manifest["source_sha256"]) == 64
    assert manifest["renderer"] and manifest["engine_version"]
    assert manifest["decided_at"] and manifest["created_at"]
    assert manifest["limitations"], "the manifest must state its own boundaries"


def test_keeping_original_exports_a_reference_not_a_duplicate(searched_case, source_wav):
    record.append_decision(searched_case, kept="ORIGINAL", role="listener", request_id="r1")
    manifest = record.export_chosen(searched_case)

    export_root = record.export_dir(searched_case)
    assert manifest["export_mode"] == "REFERENCE_TO_SOURCE"
    assert manifest["chosen_audio"] is None
    assert not (export_root / "chosen.wav").exists()
    assert manifest["source_path"] == str(source_wav)

    chosen = json.loads((export_root / "chosen_field.json").read_text(encoding="utf-8"))
    assert chosen["field"] is None
    assert chosen["kept"] == "ORIGINAL"


def test_switching_to_original_removes_a_stale_field_export(searched_case):
    record.append_decision(searched_case, kept="A", role="creator", request_id="r1")
    record.export_chosen(searched_case)
    assert (record.export_dir(searched_case) / "chosen.wav").is_file()

    record.append_decision(searched_case, kept="ORIGINAL", role="creator", request_id="r2")
    manifest = record.export_chosen(searched_case)
    assert manifest["export_mode"] == "REFERENCE_TO_SOURCE"
    assert not (record.export_dir(searched_case) / "chosen.wav").exists()


def test_export_refuses_when_the_chosen_candidate_is_gone(searched_case):
    record.append_decision(searched_case, kept="B", role="creator", request_id="r1")
    record.candidate_path(searched_case, "B").unlink()
    with pytest.raises(record.WaveFieldRecordError) as excinfo:
        record.export_chosen(searched_case)
    assert excinfo.value.code == "CANDIDATE_MISSING"


# ---------------------------------------------------------------------------
# Reproducibility
# ---------------------------------------------------------------------------


def test_the_chosen_field_can_be_reproduced_byte_for_byte(searched_case):
    record.append_decision(searched_case, kept="B", role="creator", request_id="r1")
    manifest = record.export_chosen(searched_case)

    reproduced = record.reproduce_chosen(searched_case)
    assert reproduced["ok"] is True
    assert reproduced["reproduced_sha256"] == manifest["chosen_audio_sha256"]


def test_reproducing_original_verifies_the_source_hash(searched_case, source_wav):
    record.append_decision(searched_case, kept="ORIGINAL", role="creator", request_id="r1")
    record.export_chosen(searched_case)
    reproduced = record.reproduce_chosen(searched_case)
    assert reproduced["ok"] is True
    assert reproduced["reproduced_sha256"] == record.sha256_file(source_wav)


def test_reproduction_leaves_no_scratch_audio_in_the_lane(searched_case):
    record.append_decision(searched_case, kept="A", role="creator", request_id="r1")
    record.export_chosen(searched_case)
    record.reproduce_chosen(searched_case)

    lane_wavs = sorted(p.name for p in record.wavefield_dir(searched_case).rglob("*.wav"))
    assert lane_wavs == ["A.wav", "B.wav", "C.wav", "chosen.wav"]


def test_reproduce_refuses_before_export(searched_case):
    with pytest.raises(record.WaveFieldRecordError) as excinfo:
        record.reproduce_chosen(searched_case)
    assert excinfo.value.code == "EXPORT_MISSING"


# ---------------------------------------------------------------------------
# Inspection
# ---------------------------------------------------------------------------


def test_inspect_reports_absence_honestly(case_dir):
    state = record.inspect(case_dir)
    assert state["present"] is False
    assert state["blockers"] == ["NO_WAVEFIELD_SESSION"]


def test_inspect_reports_the_next_lock(case_dir, source_wav):
    run_field_search(case_dir, source_path=str(source_wav))

    state = record.inspect(case_dir)
    assert state["present"] is True
    assert state["blockers"] == ["NOT_CHOSEN"]
    assert all(state["candidates"][c]["exists"] for c in "ABC")
    assert all(state["hearing"][c] is not None for c in ("ORIGINAL", "A", "B", "C"))
    assert state["choices"] == ["ORIGINAL", "A", "B", "C"]

    record.append_decision(case_dir, kept="A", role="creator", request_id="r1")
    record.export_chosen(case_dir)
    settled = record.inspect(case_dir)
    assert settled["blockers"] == []
    assert settled["chosen"]["kept"] == "A"
    assert settled["export"]["export_mode"] == "RENDERED_FIELD"


def test_inspect_marks_a_candidate_stale_when_its_bytes_change(searched_case):
    target = record.candidate_path(searched_case, "A")
    data = bytearray(target.read_bytes())
    data[100] ^= 0xFF
    target.write_bytes(bytes(data))

    state = record.inspect(searched_case)
    assert state["candidates"]["A"]["stale"] is True
    assert "A_STALE" in state["warnings"]


def test_candidate_choices_list_original_first(searched_case):
    rows = record.candidate_choices(searched_case)
    assert [row["id"] for row in rows] == ["ORIGINAL", "A", "B", "C"]
    assert all(row["available"] for row in rows)
    assert rows[0]["field"] is None
    assert rows[1]["field"]["field_id"] == "field_A"


def test_summarize_hearing_exposes_measurements_and_the_gate_only(searched_case):
    snapshot = record.read_hearing(searched_case, "B")
    summary = record.summarize_hearing(snapshot)
    assert summary["integrated_lufs"] is not None
    assert summary["technical_status"] in {"SAFE_TO_LISTEN", "BLOCKED"}
    assert isinstance(summary["audition_correction_db"], float)
    assert record.summarize_hearing(None) is None
