from pathlib import Path
import math
import struct
import wave

from moodify_runtime.config import RuntimeConfig
from moodify_runtime.registry import register_inputs
from moodify_runtime.queue import plan_queue, load_queue


def make_wav(p: Path):
    p.parent.mkdir(parents=True, exist_ok=True)
    with wave.open(str(p), "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(8000)
        wf.writeframes(struct.pack("<h", 0) * 8000)


def test_registry_queue(tmp_path: Path):
    project = tmp_path
    make_wav(project / "data/night_inputs/a.wav")
    cfg = RuntimeConfig(project_root=project).resolved()
    r = register_inputs(cfg, source="test")
    assert r["added"] == 1
    q = plan_queue(cfg, presets=["warm_vocal"])
    assert q["added"] == 1
    rows = load_queue(cfg)
    assert rows[0]["preset"] == "warm_vocal"
