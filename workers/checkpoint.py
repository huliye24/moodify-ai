"""checkpoint.py — Moodify Night Worker 断点续跑系统.

支持:
  - 已分析/已处理文件追踪 (避免重复工作)
  - 失败 job 记录 (跳过重试)
  - 阶段状态持久化 (可跨进程恢复)
  - 原子写入 (避免并发损坏)

用法:
    from workers.checkpoint import CheckpointStore

    ckpt = CheckpointStore("runs/night_auto/checkpoints")
    if not ckpt.is_analyzed("song_01.wav"):
        metrics = analyze("song_01.wav")
        ckpt.mark_analyzed("song_01.wav")
"""

from __future__ import annotations

import json
import os
import time
import fcntl
from pathlib import Path
from datetime import datetime, timezone


class CheckpointStore:
    """断点续跑存储 — 所有状态以 JSON 文件保存。"""

    def __init__(self, checkpoint_dir: str):
        self._dir = Path(checkpoint_dir)
        self._dir.mkdir(parents=True, exist_ok=True)

        self._analyzed_path = self._dir / "analyzed_files.json"
        self._processed_path = self._dir / "processed_versions.json"
        self._failed_path = self._dir / "failed_jobs.json"
        self._stage_path = self._dir / "stage_status.json"

    # ── 原子读写 ────────────────────────────────────

    @staticmethod
    def _atomic_write(path: Path, data: object) -> None:
        tmp = path.with_suffix(".tmp")
        with open(tmp, "w", encoding="utf-8") as f:
            fcntl.flock(f, fcntl.LOCK_EX)
            json.dump(data, f, ensure_ascii=False, indent=2)
            fcntl.flock(f, fcntl.LOCK_UN)
        os.replace(tmp, path)

    @staticmethod
    def _read_json(path: Path) -> dict | list:
        if not path.exists():
            return {}
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError):
            return {}

    # ── 已分析文件 ──────────────────────────────────

    def is_analyzed(self, file_path: str) -> bool:
        """检查音频文件是否已分析。"""
        data = self._read_json(self._analyzed_path)
        if isinstance(data, dict):
            return file_path in data
        return False

    def mark_analyzed(self, file_path: str, metrics_summary: dict | None = None) -> None:
        """标记文件已分析, 可选存储指标摘要。"""
        data = self._read_json(self._analyzed_path)
        if not isinstance(data, dict):
            data = {}
        data[file_path] = {
            "analyzed_at": datetime.now(timezone.utc).isoformat(),
            "summary": metrics_summary or {},
        }
        self._atomic_write(self._analyzed_path, data)

    def get_analyzed_count(self) -> int:
        data = self._read_json(self._analyzed_path)
        return len(data) if isinstance(data, dict) else 0

    @property
    def analyzed_files(self) -> list[str]:
        """返回已分析文件路径列表。"""
        data = self._read_json(self._analyzed_path)
        if isinstance(data, dict):
            return list(data.keys())
        return []

    # ── 已处理版本 ──────────────────────────────────

    def is_processed(self, file_path: str, version_key: str) -> bool:
        """检查特定版本的音频是否已处理。version_key 如 "warm_reality/042"。"""
        data = self._read_json(self._processed_path)
        if isinstance(data, dict):
            entry = data.get(file_path, {})
            return version_key in entry
        return False

    def mark_processed(self, file_path: str, version_key: str,
                       result_summary: dict | None = None) -> None:
        """标记版本已处理。"""
        data = self._read_json(self._processed_path)
        if not isinstance(data, dict):
            data = {}
        if file_path not in data:
            data[file_path] = {}
        data[file_path][version_key] = {
            "processed_at": datetime.now(timezone.utc).isoformat(),
            "result": result_summary or {},
        }
        self._atomic_write(self._processed_path, data)

    def get_processed_count(self, file_path: str | None = None) -> int:
        """返回已处理版本总数, 或指定文件的版本数。"""
        data = self._read_json(self._processed_path)
        if not isinstance(data, dict):
            return 0
        if file_path:
            return len(data.get(file_path, {}))
        return sum(len(v) for v in data.values())

    # ── 失败记录 ────────────────────────────────────

    def record_failure(self, job_type: str, key: str, error: str) -> None:
        """记录一个失败的 job。"""
        data = self._read_json(self._failed_path)
        if not isinstance(data, dict):
            data = {}
        data[f"{job_type}:{key}"] = {
            "type": job_type,
            "key": key,
            "error": str(error),
            "failed_at": datetime.now(timezone.utc).isoformat(),
        }
        self._atomic_write(self._failed_path, data)

    def is_failed(self, job_type: str, key: str) -> bool:
        data = self._read_json(self._failed_path)
        if isinstance(data, dict):
            return f"{job_type}:{key}" in data
        return False

    def get_failed_jobs(self) -> list[dict]:
        data = self._read_json(self._failed_path)
        if isinstance(data, dict):
            return list(data.values())
        return []

    # ── 阶段状态 ────────────────────────────────────

    def set_stage(self, stage: str, status: str = "completed") -> None:
        """记录阶段完成状态。stage: scan|analyze|sweep|score|report"""
        data = self._read_json(self._stage_path)
        if not isinstance(data, dict):
            data = {}
        data[stage] = {
            "status": status,
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }
        self._atomic_write(self._stage_path, data)

    def is_stage_done(self, stage: str) -> bool:
        data = self._read_json(self._stage_path)
        if isinstance(data, dict):
            return data.get(stage, {}).get("status") == "completed"
        return False

    def get_stage_status(self) -> dict:
        data = self._read_json(self._stage_path)
        return data if isinstance(data, dict) else {}

    # ── 全局元数据 ──────────────────────────────────

    def set_meta(self, key: str, value) -> None:
        """存储全局元数据 (开始时间、运行名等)。"""
        data = self._read_json(self._stage_path)
        if not isinstance(data, dict):
            data = {}
        if "_meta" not in data:
            data["_meta"] = {}
        data["_meta"][key] = value
        self._atomic_write(self._stage_path, data)

    def get_meta(self, key: str, default=None):
        data = self._read_json(self._stage_path)
        if isinstance(data, dict):
            return data.get("_meta", {}).get(key, default)
        return default

    # ── 重置 ────────────────────────────────────────

    def reset_stage(self, stage: str) -> None:
        """重置某个阶段 (删除其完成状态, 不删数据)。"""
        data = self._read_json(self._stage_path)
        if isinstance(data, dict) and stage in data:
            del data[stage]
            self._atomic_write(self._stage_path, data)
