"""job_queue.py — Moodify Night Worker 任务队列.

管理批量音频分析/参数扫描/评分任务, 支持:
  - 自动跳过已完成 job (断点续跑)
  - 自动跳过已失败 job
  - 并发控制 (通过 ResourceGuard)
  - 超时和异常捕获

用法:
    from workers.job_queue import JobQueue, AudioAnalysisJob

    queue = JobQueue(checkpoint, guard, max_parallel=2)
    for job in queue.iter_analysis_jobs(audio_files):
        result = job.run()
        queue.mark_done(job, result)
"""

from __future__ import annotations

import logging
import time
import traceback
from dataclasses import dataclass, field
from typing import Callable, Iterator

from workers.checkpoint import CheckpointStore
from workers.resource_guard import ResourceGuard

logger = logging.getLogger("night_worker.job_queue")


@dataclass
class JobResult:
    success: bool
    key: str
    data: dict = field(default_factory=dict)
    error: str = ""
    elapsed_s: float = 0.0


class JobQueue:
    """任务队列 — 编排和追踪 job 执行。"""

    def __init__(self,
                 checkpoint: CheckpointStore,
                 guard: ResourceGuard,
                 max_parallel: int = 2):
        self._ckpt = checkpoint
        self._guard = guard
        self._max_parallel = max_parallel

    # ── 音频分析 jobs ───────────────────────────────

    def iter_analysis_jobs(self,
                           audio_files: list[str],
                           analyzer_fn: Callable[[str], dict],
                           ) -> Iterator[tuple[str, Callable[[], JobResult]]]:
        """逐个产出待分析的音频 job (跳过已完成的)。

        Yields: (file_path, callable_that_runs_job)
        """
        skipped = 0
        for fp in audio_files:
            if self._ckpt.is_analyzed(fp):
                skipped += 1
                continue
            if self._ckpt.is_failed("analyze", fp):
                skipped += 1
                continue
            yield fp, self._make_runner(fp, "analyze", analyzer_fn, fp)
        if skipped:
            logger.info("音频分析: 跳过 %d 已完成/失败的文件", skipped)

    # ── 参数扫描 jobs ───────────────────────────────

    def iter_sweep_jobs(self,
                        audio_files: list[str],
                        versions: list[dict],       # [{category, version_key, params}]
                        processor_fn: Callable[[str, dict], dict],
                        ) -> Iterator[tuple[str, str, Callable[[], JobResult]]]:
        """逐个产出待处理的 (file, version) 组合 (跳过已完成的)。

        Yields: (file_path, version_key, callable_that_runs_job)
        """
        skipped = 0
        for fp in audio_files:
            for ver in versions:
                vk = ver["version_key"]
                if self._ckpt.is_processed(fp, vk):
                    skipped += 1
                    continue
                if self._ckpt.is_failed("sweep", f"{fp}::{vk}"):
                    skipped += 1
                    continue
                yield fp, vk, self._make_runner(
                    f"{fp}::{vk}", "sweep", processor_fn, fp, ver["params"]
                )
        if skipped:
            logger.info("参数扫描: 跳过 %d 已完成/失败的版本", skipped)

    # ── 评分 jobs ───────────────────────────────────

    def iter_score_jobs(self,
                        results: list[dict],
                        scorer_fn: Callable[[dict], dict],
                        ) -> Iterator[dict, Callable[[], JobResult]]:
        """为每个结果运行评分 (已在内存中的结果, 无需检查 checkpoint)。

        Yields: (result, callable_that_runs_job)
        """
        for i, r in enumerate(results):
            key = r.get("version_key", f"result_{i}")
            if self._ckpt.is_failed("score", key):
                continue
            yield r, self._make_runner(key, "score", scorer_fn, r)

    # ── 执行辅助 ────────────────────────────────────

    def _make_runner(self, key: str, job_type: str,
                     fn: Callable, *args) -> Callable[[], JobResult]:
        """包装一个函数为 JobResult-返回的 callable。"""
        def runner() -> JobResult:
            t0 = time.perf_counter()
            try:
                # 资源等待
                while not self._guard.can_start_new_worker():
                    self._guard.cooldown()

                self._guard.current_workers += 1
                data = fn(*args)
                elapsed = time.perf_counter() - t0
                return JobResult(success=True, key=key, data=data, elapsed_s=elapsed)
            except Exception as e:
                elapsed = time.perf_counter() - t0
                tb = traceback.format_exc()
                logger.error("Job [%s] %s 失败: %s", job_type, key, e)
                self._ckpt.record_failure(job_type, key, f"{e}\n{tb}")
                return JobResult(success=False, key=key, error=str(e), elapsed_s=elapsed)
            finally:
                self._guard.current_workers -= 1

        return runner

    def mark_analysis_done(self, file_path: str, result: JobResult):
        if result.success:
            self._ckpt.mark_analyzed(file_path, result.data)
            self._guard.increment_processed(versions=0)
            self._guard.assert_disk_safe()  # no new audio generated yet

    def mark_sweep_done(self, file_path: str, version_key: str, result: JobResult):
        if result.success:
            self._ckpt.mark_processed(file_path, version_key, result.data)
            self._guard.increment_processed(versions=0)
            try:
                self._guard.assert_disk_safe()
            except RuntimeError:
                logger.critical("磁盘紧急停止!")
                raise
            if self._guard.is_disk_low():
                logger.warning("磁盘低于安全线, 停止生成新版本")
                raise ResourceWarning("磁盘不足, 停止生成新音频")
