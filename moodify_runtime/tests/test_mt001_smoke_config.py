from pathlib import Path

from moodify_runtime.config import load_config
from moodify_runtime.queue import plan_queue
from moodify_runtime.registry import register_inputs
from moodify_runtime.utils import render_template_to_argv


def test_mt001_smoke_config_is_self_contained(tmp_path, monkeypatch):
    repo = Path(__file__).resolve().parents[2]
    cfg = load_config(repo / "configs/mt001_runtime_smoke.json")
    assert cfg.project_root == repo
    assert cfg.input_dirs == [repo / "moodify-core-package/tests/baseline/test_audio"]
    assert cfg.output_root == repo / "outputs/mt001_smoke"
    assert cfg.registry_path == repo / "data/moodify_runtime_mt001/input_registry.jsonl"
    assert cfg.queue_path == repo / "data/moodify_runtime_mt001/run_queue.jsonl"
    assert all("moodify-o3is" not in str(value) for value in cfg.to_dict().values())


def test_mt001_smoke_config_plans_3x3_tasks(tmp_path):
    repo = Path(__file__).resolve().parents[2]
    cfg = load_config(repo / "configs/mt001_runtime_smoke.json")
    cfg.data_root = tmp_path / "data"
    cfg.registry_path = tmp_path / "input_registry.jsonl"
    cfg.queue_path = tmp_path / "run_queue.jsonl"
    result = register_inputs(cfg, source="unit")
    assert result["discovered"] == 3
    planned = plan_queue(cfg, reason="unit")
    assert planned["added"] == 9
    assert {task["preset"] for task in planned["tasks"]} == {"warm_vocal", "clean_master", "wide_space"}


def test_mt001_smoke_command_template_targets_moodify_cli():
    repo = Path(__file__).resolve().parents[2]
    cfg = load_config(repo / "configs/mt001_runtime_smoke.json")
    argv = render_template_to_argv(
        cfg.command_templates[0],
        {
            "python": cfg.python,
            "input": repo / "moodify-core-package/tests/baseline/test_audio/electronic.wav",
            "preset": "clean_master",
            "output_dir": repo / "outputs/mt001_smoke/unit/SMP/clean_master",
        },
    )
    assert argv[:4] == [".venv/bin/python", "-m", "moodify.cli", "process"]
    assert "--output-dir" in argv
