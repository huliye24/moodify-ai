from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional


DEFAULT_AUDIO_SUFFIXES = [".wav", ".mp3", ".flac", ".m4a", ".aac", ".ogg"]


@dataclass
class RuntimeConfig:
    project_root: Path = Path(".")
    data_root: Path = Path("data/moodify_runtime")
    input_dirs: List[Path] = field(default_factory=lambda: [Path("data/night_inputs")])
    output_root: Path = Path("outputs/daily_runs")
    registry_path: Path = Path("data/moodify_runtime/input_registry.jsonl")
    queue_path: Path = Path("data/moodify_runtime/run_queue.jsonl")
    craft_memory_dir: Path = Path("data/moodify_runtime/craft_memory")
    report_dir: Path = Path("reports/daily_runs")
    presets: List[str] = field(default_factory=lambda: ["warm_vocal", "clean_master", "wide_space"])
    max_files: int = 30
    recurse: bool = False
    timeout_seconds_per_task: int = 900
    sleep_seconds_between_tasks: float = 2.0
    max_retries_per_task: int = 2
    keep_last_n_runs: int = 10
    min_free_disk_gb: float = 1.0
    python: str = "python3"
    stop_on_first_success_template: bool = True
    audio_suffixes: List[str] = field(default_factory=lambda: list(DEFAULT_AUDIO_SUFFIXES))
    command_templates: List[str] = field(default_factory=lambda: [
        "{python} cli.py process --input {input} --output {output_dir} --preset {preset}",
        "{python} -m moodify.cli process --input {input} --output {output_dir} --preset {preset}",
        "{python} cli.py process {input} --output {output_dir} --preset {preset}",
    ])
    env: Dict[str, str] = field(default_factory=lambda: {
        "PYTHONUNBUFFERED": "1",
        "MOODIFY_DAILY_RUN": "1",
    })
    metric_audio_suffixes: List[str] = field(default_factory=lambda: list(DEFAULT_AUDIO_SUFFIXES))
    allow_missing_outputs: bool = True

    @classmethod
    def from_json(cls, path: Path | str) -> "RuntimeConfig":
        path = Path(path)
        raw = json.loads(path.read_text(encoding="utf-8"))
        return cls.from_dict(raw, config_dir=path.parent)

    @classmethod
    def from_dict(cls, raw: Dict[str, Any], config_dir: Optional[Path] = None) -> "RuntimeConfig":
        cfg = cls()
        for key, value in raw.items():
            if not hasattr(cfg, key):
                continue
            current = getattr(cfg, key)
            if isinstance(current, Path):
                setattr(cfg, key, Path(value))
            elif isinstance(current, list) and key.endswith("_dirs"):
                setattr(cfg, key, [Path(x) for x in value])
            elif key == "input_dirs":
                setattr(cfg, key, [Path(x) for x in value])
            else:
                setattr(cfg, key, value)
        return cfg

    def resolved(self) -> "RuntimeConfig":
        root = self.project_root.resolve()
        clone = RuntimeConfig.from_dict(self.to_dict())
        clone.project_root = root

        def rp(p: Path) -> Path:
            return p if p.is_absolute() else root / p

        clone.data_root = rp(self.data_root)
        clone.input_dirs = [rp(p) for p in self.input_dirs]
        clone.output_root = rp(self.output_root)
        clone.registry_path = rp(self.registry_path)
        clone.queue_path = rp(self.queue_path)
        clone.craft_memory_dir = rp(self.craft_memory_dir)
        clone.report_dir = rp(self.report_dir)
        return clone

    def to_dict(self) -> Dict[str, Any]:
        def conv(v):
            if isinstance(v, Path):
                return str(v)
            if isinstance(v, list):
                return [conv(x) for x in v]
            if isinstance(v, dict):
                return {k: conv(x) for k, x in v.items()}
            return v

        return {k: conv(getattr(self, k)) for k in self.__dataclass_fields__.keys()}


def load_config(path: Optional[str | Path] = None) -> RuntimeConfig:
    if path is None:
        path = os.environ.get("MOODIFY_RUNTIME_CONFIG")
    if path:
        return RuntimeConfig.from_json(Path(path)).resolved()
    return RuntimeConfig().resolved()
