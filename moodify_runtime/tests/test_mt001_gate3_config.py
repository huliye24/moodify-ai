from pathlib import Path

from moodify_runtime.config import load_config
from moodify_runtime.utils import render_template_to_argv


def test_mt001_gate3_config_limits_real_ai_batch():
    repo = Path(__file__).resolve().parents[2]
    cfg = load_config(repo / "configs/mt001_gate3_real_ai_30.json")
    assert cfg.input_dirs == [repo / "data/mt001_real_inputs"]
    assert cfg.max_files == 30
    assert cfg.presets == ["warm_vocal", "clean_master", "wide_space"]
    assert cfg.audio_suffixes == [".mp3", ".flac"]
    assert cfg.output_root == repo / "outputs/mt001_gate3_real_ai"
    assert cfg.registry_path == repo / "data/moodify_runtime_mt001_gate3/input_registry.jsonl"


def test_mt001_gate3_command_template_uses_moodify_cli():
    repo = Path(__file__).resolve().parents[2]
    cfg = load_config(repo / "configs/mt001_gate3_real_ai_30.json")
    argv = render_template_to_argv(
        cfg.command_templates[0],
        {
            "python": cfg.python,
            "input": repo / "data/mt001_real_inputs/example song.mp3",
            "preset": "warm_vocal",
            "output_dir": repo / "outputs/mt001_gate3_real_ai/unit/SMP/warm_vocal",
        },
    )
    assert argv[:4] == [".venv/bin/python", "-m", "moodify.cli", "process"]
    assert "--preset" in argv
    assert "--output-dir" in argv
