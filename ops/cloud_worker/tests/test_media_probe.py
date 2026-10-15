"""`media_probe` —— 媒体事实提取。

裁决（2026-10-15）：`media_probe` 允许直接调用 ffprobe；它只出媒体事实，不是 DSP / Judge。
因此本模块可以**在没有 Core 的机器上**跑（W3A 的覆盖面）。

分两层：
- 纯函数层（`summarize`）：喂 canned ffprobe JSON，断言事实提取与 `not_alignable` 的诚实性。
- 真实工具层：用标准库合成一段 WAV，真跑 ffprobe。**没有 ffprobe 就 skip**，不假装通过。
"""

from __future__ import annotations

import shutil
import wave
from pathlib import Path

import pytest

import contract
from adapters import media_probe

CANNED = {
    "format": {"format_name": "wav", "duration": "2.500000", "size": "441044"},
    "streams": [
        {
            "codec_type": "audio",
            "codec_name": "pcm_s16le",
            "sample_rate": "44100",
            "channels": 2,
            "channel_layout": "stereo",
            "bits_per_sample": 16,
        },
        {"codec_type": "video", "codec_name": "png"},  # 封面流：不得被当成音频流
    ],
}


# ------------------------------------------------------------ 纯函数层

def test_summarize_reads_media_facts():
    facts = media_probe.summarize(CANNED)

    assert facts["container"] == "wav"
    assert facts["codec"] == "pcm_s16le"
    assert facts["duration_seconds"] == 2.5
    assert facts["sample_rate"] == 44100
    assert facts["channels"] == 2
    assert facts["channel_layout"] == "stereo"
    assert facts["bit_depth"] == 16
    assert facts["file_size_bytes"] == 441044
    assert facts["audio_stream_count"] == 1
    assert facts["stream_count"] == 2


def test_summarize_picks_the_audio_stream_not_the_first_stream():
    """带封面的文件里第一条流可能不是音频。"""
    assert media_probe.summarize(CANNED)["codec"] == "pcm_s16le"


def test_missing_facts_are_not_alignable_not_guessed():
    """取不到的写 not_alignable，**不补算**。"""
    raw = {"format": {}, "streams": [{"codec_type": "audio", "codec_name": "mp3"}]}
    facts = media_probe.summarize(raw)

    assert facts["duration_seconds"] == contract.NOT_ALIGNABLE
    assert facts["sample_rate"] == contract.NOT_ALIGNABLE
    assert facts["bit_depth"] == contract.NOT_ALIGNABLE
    assert facts["file_size_bytes"] == contract.NOT_ALIGNABLE
    assert facts["codec"] == "mp3"  # 这个有，就照实写


def test_stream_without_audio_is_a_tool_failure():
    from adapters.base import AdapterError

    with pytest.raises(AdapterError) as ei:
        media_probe.summarize({"format": {}, "streams": [{"codec_type": "video"}]})
    assert ei.value.code == "TOOL_FAILED"


def test_adapter_uses_no_core(tmp_path, monkeypatch):
    """不碰 Core：即使 ctx.core 是 None 也必须能跑完（W3A 的核心断言）。"""
    from adapters.base import AdapterContext

    (tmp_path / "out").mkdir()
    (tmp_path / "scratch").mkdir()
    (tmp_path / "in.wav").write_bytes(b"x" * 100)
    job = contract.validate_job(
        {
            "schema_version": contract.JOB_SCHEMA_VERSION,
            "job_id": "11111111-1111-4111-8111-111111111111",
            "request_id": "req-1",
            "job_type": "media_probe",
            "input": {"bucket": "moodify-dataset", "key": "k", "sha256": "a" * 64},
            "output_prefix": "results/11111111-1111-4111-8111-111111111111/",
            "created_at": "2026-10-15T10:00:00Z",
        }
    )
    ctx = AdapterContext(
        job=job,
        work_dir=tmp_path,
        input_path=tmp_path / "in.wav",
        out_dir=tmp_path / "out",
        scratch_dir=tmp_path / "scratch",
        core=None,  # ← 刻意不给 Core
        timeout_seconds=60,
    )
    monkeypatch.setattr(media_probe, "probe_media", lambda path, timeout: CANNED)

    outcome = media_probe.run(ctx)

    assert outcome.status == contract.STATUS_DONE
    assert outcome.core_version == contract.NOT_ALIGNABLE
    assert [a.key_suffix for a in outcome.artifacts] == ["media_probe.json"]


# ------------------------------------------------------------ 真实工具层

def _ffprobe_available() -> bool:
    import os

    exe = os.environ.get("MOODIFY_FFPROBE", "ffprobe")
    return shutil.which(exe) is not None


requires_ffprobe = pytest.mark.skipif(
    not _ffprobe_available(),
    reason="本机没有 ffprobe；真实工具路径在节点（W3）上验，这里不假装通过",
)


def _write_wav(path: Path, seconds: float = 0.5, rate: int = 44100, channels: int = 1) -> None:
    """用标准库合成一段静音 WAV —— 不引入任何依赖。"""
    frames = int(seconds * rate)
    with wave.open(str(path), "wb") as w:
        w.setnchannels(channels)
        w.setsampwidth(2)
        w.setframerate(rate)
        w.writeframes(b"\x00\x00" * frames * channels)


@requires_ffprobe
def test_real_ffprobe_extracts_the_facts_we_synthesized(tmp_path):
    """真实工具路径：合成一段已知参数的 WAV，看 ffprobe 报出来的事实是否对得上。"""
    wav = tmp_path / "tone.wav"
    _write_wav(wav, seconds=0.5, rate=44100, channels=1)

    facts = media_probe.summarize(media_probe.probe_media(wav, timeout=60))

    assert facts["sample_rate"] == 44100
    assert facts["channels"] == 1
    assert facts["codec"].startswith("pcm")
    assert abs(float(facts["duration_seconds"]) - 0.5) < 0.05
    assert facts["file_size_bytes"] > 0
