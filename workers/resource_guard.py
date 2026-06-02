"""resource_guard.py — Moodify Night Worker 资源保护系统.

监控 CPU / 内存 / 磁盘, 自动降级或紧急停止。

用法:
    from workers.resource_guard import ResourceGuard

    guard = ResourceGuard("configs/server_limits.yaml")
    if not guard.can_start_new_worker():
        print("资源不足, 等待...")
        guard.cooldown()

    guard.assert_disk_safe()  # 磁盘不足时抛异常

工作原理:
  - 每 N 秒采样一次系统资源
  - 超过 throttle 阈值 → 降低并行度
  - 超过 max 阈值 → 拒绝新 worker
  - 低于紧急阈值 → 抛异常停止
"""

from __future__ import annotations

import os
import time
import shutil
import logging
from pathlib import Path
from typing import Any

import yaml

logger = logging.getLogger("night_worker.resource_guard")


class ResourceLimits:
    """解析后的资源限制配置。"""

    def __init__(self, config_path: str):
        raw = _load_yaml(config_path)
        self.cpu_max_pct: float =         float(_nested(raw, "cpu", "max_total_pct", default=80))
        self.cpu_throttle_pct: float =    float(_nested(raw, "cpu", "throttle_at_pct", default=70))
        self.cpu_poll_interval: float =   float(_nested(raw, "cpu", "poll_interval_seconds", default=5))
        self.mem_max_gb: float =          float(_nested(raw, "memory", "max_total_gb", default=6.0))
        self.mem_throttle_gb: float =     float(_nested(raw, "memory", "throttle_at_gb", default=4.5))
        self.mem_per_worker_mb: float =   float(_nested(raw, "memory", "per_worker_estimate_mb", default=800))
        self.disk_min_free_gb: float =    float(_nested(raw, "disk", "min_free_gb", default=10))
        self.disk_warn_free_gb: float =   float(_nested(raw, "disk", "warn_free_gb", default=20))
        self.max_output_gb: float =       float(_nested(raw, "disk", "max_output_size_gb", default=100))
        self.parallel_default: int =      int(_nested(raw, "parallelism", "default_workers", default=2))
        self.parallel_max: int =          int(_nested(raw, "parallelism", "max_workers", default=4))
        self.parallel_min: int =          int(_nested(raw, "parallelism", "min_workers", default=1))
        self.cooldown_seconds: float =    float(_nested(raw, "parallelism", "cooldown_seconds", default=3))
        self.max_audio_processed: int =   int(_nested(raw, "safety", "max_total_audio_processed", default=500))
        self.max_wall_time: float =       float(_nested(raw, "safety", "max_wall_time_seconds", default=43200))
        self.max_versions: int =          int(_nested(raw, "safety", "max_versions_total", default=2000))
        self.emergency_stop_mb: int =     int(_nested(raw, "safety", "emergency_stop_free_mb", default=500))


class ResourceGuard:
    """运行时的资源保护闸门。"""

    def __init__(self, limits: ResourceLimits, output_dir: str = "."):
        self.limits = limits
        self._output_dir = Path(output_dir)
        self._current_workers = 0
        self._last_throttle = 0.0
        self._total_audio_processed = 0
        self._total_versions = 0
        self._start_time = time.monotonic()

    # ── 公共 API ────────────────────────────────────

    @property
    def current_workers(self) -> int:
        return self._current_workers

    @current_workers.setter
    def current_workers(self, n: int):
        self._current_workers = max(0, n)

    def increment_processed(self, versions: int = 1):
        self._total_audio_processed += 1
        self._total_versions += versions

    @property
    def total_audio_processed(self) -> int:
        return self._total_audio_processed

    @property
    def total_versions(self) -> int:
        return self._total_versions

    @property
    def elapsed_seconds(self) -> float:
        return time.monotonic() - self._start_time

    def can_start_new_worker(self) -> bool:
        """检查是否允许启动一个新的 worker 进程。"""
        # 硬上限
        if self._current_workers >= self.limits.parallel_max:
            logger.debug("已达并行硬上限 %d", self.limits.parallel_max)
            return False

        # 音频数上限
        if self._total_audio_processed >= self.limits.max_audio_processed:
            logger.warning("已达音频处理上限 %d", self.limits.max_audio_processed)
            return False

        # 版本数上限
        if self._total_versions >= self.limits.max_versions:
            logger.warning("已达版本生成上限 %d", self.limits.max_versions)
            return False

        # 时间上限
        if self.elapsed_seconds >= self.limits.max_wall_time:
            logger.warning("已达运行时间上限 %.1fh", self.limits.max_wall_time / 3600)
            return False

        # CPU 检查
        cpu_pct = self._get_cpu_usage()
        if cpu_pct >= self.limits.cpu_max_pct:
            logger.info("CPU %.1f%% 超过 max %.0f%%, 等待", cpu_pct, self.limits.cpu_max_pct)
            return False

        # 内存检查
        mem_used = self._get_memory_used_gb()
        if mem_used >= self.limits.mem_max_gb:
            logger.info("内存 %.1fGB 超过 max %.1fGB, 等待", mem_used, self.limits.mem_max_gb)
            return False

        return True

    def recommend_parallelism(self) -> int:
        """根据当前资源状况建议并行数。"""
        cpu_pct = self._get_cpu_usage()
        mem_used = self._get_memory_used_gb()

        # CPU 节流
        if cpu_pct >= self.limits.cpu_max_pct:
            rec = self.limits.parallel_min
        elif cpu_pct >= self.limits.cpu_throttle_pct:
            rec = max(self.limits.parallel_min,
                      self.limits.parallel_default - 1)
        else:
            rec = self.limits.parallel_default

        # 内存节流
        if mem_used >= self.limits.mem_max_gb:
            rec = self.limits.parallel_min
        elif mem_used >= self.limits.mem_throttle_gb:
            rec = max(self.limits.parallel_min, rec - 1)

        return min(rec, self.limits.parallel_max)

    def assert_disk_safe(self) -> None:
        """检查磁盘是否安全; 不安全则抛 RuntimeError。"""
        free_gb = self._get_free_disk_gb()
        free_mb = free_gb * 1024

        if free_mb < self.limits.emergency_stop_mb:
            raise RuntimeError(
                f"紧急停止: 磁盘仅剩 {free_mb:.0f}MB, "
                f"低于紧急阈值 {self.limits.emergency_stop_mb}MB"
            )

    def is_disk_low(self) -> bool:
        """磁盘是否低于安全线? (低于此线应停止生成新音频)"""
        return self._get_free_disk_gb() < self.limits.disk_min_free_gb

    def get_disk_status(self) -> dict:
        free_gb = self._get_free_disk_gb()
        return {
            "free_gb": free_gb,
            "warn": free_gb < self.limits.disk_warn_free_gb,
            "stop_new": free_gb < self.limits.disk_min_free_gb,
            "emergency": (free_gb * 1024) < self.limits.emergency_stop_mb,
        }

    def cooldown(self):
        """短暂冷却, 避免资源检查频繁切换。"""
        now = time.monotonic()
        elapsed = now - self._last_throttle
        if elapsed < self.limits.cooldown_seconds:
            time.sleep(self.limits.cooldown_seconds - elapsed)
        self._last_throttle = time.monotonic()

    def get_snapshot(self) -> dict:
        """返回当前资源快照 (供报告使用)。"""
        return {
            "cpu_pct": self._get_cpu_usage(),
            "mem_used_gb": self._get_memory_used_gb(),
            "disk_free_gb": self._get_free_disk_gb(),
            "current_workers": self._current_workers,
            "recommended_workers": self.recommend_parallelism(),
            "audio_processed": self._total_audio_processed,
            "versions_generated": self._total_versions,
            "elapsed_seconds": round(self.elapsed_seconds, 1),
            "output_dir_size_gb": round(self._get_output_dir_size_gb(), 2),
        }

    # ── 系统采样 ────────────────────────────────────

    @staticmethod
    def _get_cpu_usage() -> float:
        """读取 /proc/stat 计算最近一段时间的 CPU 使用率 (0-100)。"""
        try:
            with open("/proc/stat", "r") as f:
                line = f.readline()
            parts = line.split()
            if parts[0] != "cpu":
                return 0.0
            vals = [int(x) for x in parts[1:]]
            total = sum(vals)
            idle = vals[3] + (vals[4] if len(vals) > 4 else 0)  # idle + iowait
            # 简单 ratio (非精确但足够)
            if total == 0:
                return 0.0
            return round(100.0 * (1.0 - idle / total), 1)
        except Exception:
            return 0.0

    @staticmethod
    def _get_memory_used_gb() -> float:
        """从 /proc/meminfo 读取已用内存 (GB)。"""
        try:
            meminfo = {}
            with open("/proc/meminfo", "r") as f:
                for line in f:
                    if ":" in line:
                        k, v = line.split(":", 1)
                        meminfo[k.strip()] = v.strip().split()[0]
            total = int(meminfo.get("MemTotal", 0))
            available = int(meminfo.get("MemAvailable", 0))
            if total == 0:
                return 0.0
            used_kb = total - available
            return round(used_kb / (1024 * 1024), 2)
        except Exception:
            return 0.0

    @staticmethod
    def _get_free_disk_gb() -> float:
        """返回当前工作目录所在分区的剩余空间 (GB)。"""
        try:
            stat = os.statvfs(".")
            free_bytes = stat.f_frsize * stat.f_bavail
            return round(free_bytes / (1024 ** 3), 2)
        except Exception:
            return 999.0  # 无法获取时乐观处理

    def _get_output_dir_size_gb(self) -> float:
        """返回输出目录总大小 (GB)。"""
        try:
            total = 0
            for dirpath, _dirnames, filenames in os.walk(self._output_dir):
                for f in filenames:
                    fp = os.path.join(dirpath, f)
                    try:
                        total += os.path.getsize(fp)
                    except OSError:
                        pass
            return round(total / (1024 ** 3), 2)
        except Exception:
            return 0.0


# ── helpers ─────────────────────────────────────────────

def _load_yaml(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def _nested(d: dict, *keys: str, default: Any = None) -> Any:
    """从嵌套字典中安全取值.

    用法: _nested(d, "cpu", "max_total_pct", default=80)
    """
    for k in keys:
        if isinstance(d, dict):
            d = d.get(k)
        else:
            return default
    return d if d is not None else default
