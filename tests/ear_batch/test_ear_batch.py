import importlib.util
import json
import argparse
from pathlib import Path


MODULE_PATH = Path(__file__).parents[2] / "ops" / "ear_batch" / "ear_batch.py"
SPEC = importlib.util.spec_from_file_location("ear_batch", MODULE_PATH)
ear_batch = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(ear_batch)


def test_source_files_excludes_v2(tmp_path):
    (tmp_path / "Moodify_Ear_v1.md").write_text("v1", encoding="utf-8")
    v2 = tmp_path / "moodify ear 2.0"
    v2.mkdir()
    (v2 / "chapter.md").write_text("v2", encoding="utf-8")
    assert [path.name for path in ear_batch.source_files(tmp_path)] == ["Moodify_Ear_v1.md"]


def test_refresh_ready_respects_dependencies():
    ledger = {"tasks": [
        {"id": "A", "state": "PASSED", "deps": [], "updated_at": None},
        {"id": "B", "state": "PENDING", "deps": ["A"], "updated_at": None},
        {"id": "C", "state": "PENDING", "deps": ["B"], "updated_at": None},
    ]}
    ear_batch.refresh_ready(ledger)
    assert [item["state"] for item in ledger["tasks"]] == ["PASSED", "READY", "PENDING"]


def test_atomic_json_round_trip(tmp_path):
    target = tmp_path / "ledger.json"
    ear_batch.atomic_json(target, {"text": "听见", "value": 1})
    assert json.loads(target.read_text(encoding="utf-8"))["text"] == "听见"


def test_verify_outputs(tmp_path):
    output = tmp_path / "result.md"
    output.write_text("evidence", encoding="utf-8")
    passed, checks = ear_batch.verify_outputs(tmp_path, {"outputs": ["result.md", "missing.json"]})
    assert not passed
    assert checks[0]["passed"]
    assert not checks[1]["passed"]


def test_rebase_source_requires_matching_hashes(tmp_path):
    old_source = tmp_path / "old"
    new_source = tmp_path / "new"
    run_dir = tmp_path / "run"
    old_source.mkdir()
    new_source.mkdir()
    run_dir.mkdir()
    (old_source / "chapter.md").write_text("same", encoding="utf-8")
    (new_source / "chapter.md").write_text("same", encoding="utf-8")
    ear_batch.atomic_json(run_dir / "SOURCE_SNAPSHOT.json", {
        "source": str(old_source),
        "files": [{"path": "chapter.md", "bytes": 4,
                   "sha256": ear_batch.sha256(old_source / "chapter.md")}],
    })
    ear_batch.atomic_json(run_dir / "TASK_LEDGER.json", {
        "source": str(old_source), "updated_at": None, "tasks": [],
    })
    ear_batch.cmd_rebase_source(argparse.Namespace(run_dir=str(run_dir), new_source=str(new_source)))
    assert ear_batch.read_json(run_dir / "SOURCE_SNAPSHOT.json")["source"] == str(new_source.resolve())
    assert ear_batch.read_json(run_dir / "evidence" / "SOURCE_REBASE.json")["passed"]
