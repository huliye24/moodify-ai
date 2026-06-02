#!/usr/bin/env python3
"""night_worker.py — Moodify Night Worker 夜间自动计算引擎.

在无人参与、无人确认的情况下, 整晚自动运行 Moodify 重计算任务:

  1. 自动读取任务配置
  2. 自动扫描输入音频
  3. 自动批量分析音频
  4. 自动运行参数扫描
  5. 自动生成处理版本
  6. 自动计算处理前后指标
  7. 自动筛选最优 preset
  8. 自动生成 CSV / JSON / Markdown 报告
  9. 自动写日志
  10. 自动写 checkpoint
  11. 支持断点续跑
  12. 支持失败跳过
  13. 支持资源限制
  14. 支持后台运行
  15. 支持第二天早上直接查看结果

用法:
    python workers/night_worker.py --config configs/night_jobs.yaml

后台运行:
    bash scripts/run_night.sh
"""

from __future__ import annotations

import argparse
import itertools
import json
import logging
import math
import os
import random
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import yaml


# ── 将 moodify-core-package/src 加入路径 ────────────────
_PROJECT_ROOT = Path(__file__).resolve().parent.parent
_MOODIFY_SRC = _PROJECT_ROOT / "moodify-core-package" / "src"
if str(_MOODIFY_SRC) not in sys.path:
    sys.path.insert(0, str(_MOODIFY_SRC))

# 项目内部的 workers 模块
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from workers.checkpoint import CheckpointStore
from workers.resource_guard import ResourceGuard, ResourceLimits
from workers.job_queue import JobQueue
from workers.report_builder import ReportBuilder

logger = logging.getLogger("night_worker")


# ═══════════════════════════════════════════════════════════════
# 主入口
# ═══════════════════════════════════════════════════════════════

class NightWorker:
    """Moodify Night Worker — 夜间自动计算引擎。"""

    def __init__(self, config_path: str):
        self._config = _load_yaml(config_path)
        self._config_path = Path(config_path)

        self._run_name = self._config.get("run_name", "night_auto")
        self._input_dir = Path(self._config.get("input_dir", "data/raw_audio"))
        self._output_dir = Path(self._config.get("output_dir", "runs/night_auto"))
        self._preset_grid_path = self._config.get("preset_grid", "configs/preset_grid.yaml")
        self._server_limits_path = self._config.get("server_limits", "configs/server_limits.yaml")

        # 解析为绝对路径
        if not self._input_dir.is_absolute():
            self._input_dir = _PROJECT_ROOT / self._input_dir
        if not self._output_dir.is_absolute():
            self._output_dir = _PROJECT_ROOT / self._output_dir
        if not Path(self._preset_grid_path).is_absolute():
            self._preset_grid_path = str(_PROJECT_ROOT / self._preset_grid_path)
        if not Path(self._server_limits_path).is_absolute():
            self._server_limits_path = str(_PROJECT_ROOT / self._server_limits_path)

        # 初始化子系统
        self._limits = ResourceLimits(self._server_limits_path)
        self._guard = ResourceGuard(self._limits, str(self._output_dir))
        self._ckpt = CheckpointStore(str(self._output_dir / "checkpoints"))
        self._queue = JobQueue(self._ckpt, self._guard, max_parallel=self._limits.parallel_default)
        self._reporter = ReportBuilder(str(self._output_dir))

        # 运行时状态
        self._timings: dict[str, float] = {}
        self._stage_times: dict[str, float] = {}
        self._all_metrics: list[dict] = []
        self._all_sweep_results: list[dict] = []
        self._all_errors: list[dict] = []
        self._start_ts: str = ""
        self._end_ts: str = ""

        # 设置 logging
        self._setup_logging()

    # ── 运行 ────────────────────────────────────────

    def run(self) -> int:
        """执行完整的 Night Worker 流程。返回 0=成功, 1=有错误。"""
        self._start_ts = datetime.now(timezone.utc).isoformat()
        self._ckpt.set_meta("run_start", self._start_ts)
        self._ckpt.set_meta("run_name", self._run_name)

        logger.info("=" * 60)
        logger.info("Moodify Night Worker 启动")
        logger.info("  运行名: %s", self._run_name)
        logger.info("  输出目录: %s", self._output_dir)
        logger.info("  输入目录: %s", self._input_dir)
        logger.info("=" * 60)

        t0 = time.perf_counter()
        stages = [
            ("scan",   self._stage_scan),
            ("analyze", self._stage_analyze),
            ("sweep",   self._stage_sweep),
            ("score",   self._stage_score),
            ("bench",   self._stage_bench),
            # report 在 finally 块中单独调用, 不在循环中
        ]

        for name, fn in stages:
            if name not in ("scan", "report") and not self._config.get("jobs", {}).get(
                {"analyze": "batch_audio_analysis",
                 "sweep": "parameter_sweep",
                 "score": "best_preset_selection",
                 "bench": "throughput_benchmark",
                 "report": "final_report"}.get(name, ""), True
            ):
                logger.info("跳过阶段 (配置关闭): %s", name)
                continue

            t1 = time.perf_counter()
            try:
                fn()
            except ResourceWarning as e:
                logger.warning("资源不足, 跳过剩余阶段: %s", e)
                self._stage_times[name] = time.perf_counter() - t1
                break
            except Exception as e:
                logger.exception("阶段 [%s] 致命错误: %s", name, e)
                self._all_errors.append({
                    "type": f"stage:{name}",
                    "key": "fatal",
                    "error": str(e),
                })
            self._stage_times[name] = time.perf_counter() - t1
            self._ckpt.set_stage(name)

        self._end_ts = datetime.now(timezone.utc).isoformat()
        self._ckpt.set_meta("run_end", self._end_ts)
        self._timings["total_elapsed_s"] = time.perf_counter() - t0

        # 最终报告 (即使前面的 report stage 失败也尝试生成)
        if self._config.get("jobs", {}).get("final_report", True):
            try:
                self._stage_report(force=True)
            except Exception as e:
                logger.exception("最终报告生成失败: %s", e)

        # 日志统计
        num_errors = len(self._all_errors)
        num_failed = len(self._ckpt.get_failed_jobs())
        logger.info("=" * 60)
        logger.info("Moodify Night Worker 完成")
        logger.info("  分析音频: %d", len(self._all_metrics))
        logger.info("  处理版本: %d", len(self._all_sweep_results))
        logger.info("  错误: %d (stage) + %d (job)", num_errors, num_failed)
        logger.info("  总耗时: %.1fs", self._timings["total_elapsed_s"])
        logger.info("  报告目录: %s", self._output_dir / "reports")
        logger.info("=" * 60)

        return 1 if (num_errors > 0 or num_failed > 0) else 0

    # ── Stage 1: 扫描 ───────────────────────────────

    def _stage_scan(self):
        """扫描输入音频, 为空则生成测试音频。"""
        logger.info("─" * 40)
        logger.info("Stage 1/6: 扫描输入音频")

        self._input_dir.mkdir(parents=True, exist_ok=True)
        audio_files = _scan_audio(self._input_dir)

        if not audio_files:
            if self._config.get("test_audio", {}).get("generate_if_empty", True):
                count = self._config.get("test_audio", {}).get("count", 5)
                duration = self._config.get("test_audio", {}).get("duration_seconds", 10)
                sr = self._config.get("test_audio", {}).get("sample_rate", 44100)
                logger.info("输入目录为空, 生成 %d 首测试音频 (%ds, %dHz)", count, duration, sr)
                audio_files = _generate_test_audio(self._input_dir, count, duration, sr)
            else:
                logger.error("输入目录无音频且未启用自动生成, 停止")
                return

        logger.info("发现 %d 个音频文件", len(audio_files))
        self._audio_files = audio_files

    # ── Stage 2: 批量分析 ───────────────────────────

    def _stage_analyze(self):
        """批量分析所有音频, 生成指标表。"""
        logger.info("─" * 40)
        logger.info("Stage 2/6: 批量音频分析 (%d files)", len(self._audio_files))

        if self._ckpt.is_stage_done("analyze"):
            # 从 checkpoint 恢复已收集的 metrics
            logger.info("阶段 [analyze] 已完成, 从 checkpoint 恢复")
            self._all_metrics = _restore_metrics_from_checkpoint(
                self._ckpt, self._audio_files
            )
            logger.info("恢复 %d 条指标记录", len(self._all_metrics))
            return

        from moodify.v01_analyzer import analyze

        def _analyze_one(fp: str) -> dict:
            metrics = analyze(fp, str(self._output_dir / "output" / "figures"))
            return metrics.to_dict()

        for fp, runner in self._queue.iter_analysis_jobs(self._audio_files, _analyze_one):
            result = runner()
            self._queue.mark_analysis_done(fp, result)
            if result.success:
                self._all_metrics.append(result.data)
                logger.debug("  分析完成: %s", os.path.basename(fp))
            else:
                self._all_errors.append({
                    "type": "analyze",
                    "key": fp,
                    "error": result.error,
                })

        logger.info("分析完成: %d 成功, %d 失败",
                     len(self._all_metrics),
                     sum(1 for e in self._all_errors if e["type"] == "analyze"))

    # ── Stage 3: 参数扫描 ───────────────────────────

    def _stage_sweep(self):
        """批量运行 preset 参数扫描, 生成处理版本。"""
        logger.info("─" * 40)
        logger.info("Stage 3/6: 参数扫描")

        grid = _load_yaml(self._preset_grid_path)
        categories = grid.get("preset_categories", {})

        # 生成所有 (category, version_key, params) 组合
        all_versions = _build_version_grid(categories,
                                            self._config.get("limits", {}).get(
                                                "max_versions_per_audio", 50))
        logger.info("参数网格: %d 个类别, %d 个版本组合",
                     len(categories), len(all_versions))

        from moodify.v01_pipeline import process_audio
        from moodify.v01_analyzer import analyze

        def _process_one(fp: str, params: dict) -> dict:
            """用自定义 params 处理一个音频文件。"""
            # 使用 MoodifyDSPChain 直接处理, 跳过预设系统
            from moodify.audio_io import load_audio
            from moodify.processing.pedalboard_chain import MoodifyDSPChain
            from moodify.v01_exporter import export

            audio, sr = load_audio(fp, always_2d=False)
            chain = MoodifyDSPChain(params)
            processed = chain.process(audio, sr)

            out_dir = str(self._output_dir / "output" / "processed_audio")
            version_key = _params_to_key(params)
            preset_tag = f"night_{_hash_key(version_key)}"
            output_path = export(processed, sr, fp, preset_tag, out_dir)

            # 处理后分析
            metrics_after = analyze(output_path, str(self._output_dir / "output" / "figures"))
            return {
                "output_path": output_path,
                "metrics_after": metrics_after.to_dict(),
                "params_used": params,
            }

        for fp in self._audio_files:
            for version in all_versions:
                vk = version["version_key"]

                # 检查是否已完成或失败
                if self._ckpt.is_processed(fp, vk) or self._ckpt.is_failed("sweep", f"{fp}::{vk}"):
                    continue

                # 磁盘检查
                if self._guard.is_disk_low():
                    logger.warning("磁盘低于安全线, 停止参数扫描")
                    return

                runner = self._queue._make_runner(
                    f"{fp}::{vk}", "sweep", _process_one, fp, version["params"]
                )
                result = runner()

                if result.success:
                    data = result.data
                    # 构建扫描结果记录
                    record = {
                        "file": fp,
                        "category": version["category"],
                        "version_key": vk,
                        "params": version["params"],
                        "output_path": data.get("output_path", ""),
                        "metrics_after": data.get("metrics_after", {}),
                    }
                    self._all_sweep_results.append(record)
                    self._ckpt.mark_processed(fp, vk, record)
                    self._guard.increment_processed(versions=0)
                else:
                    self._all_errors.append({
                        "type": "sweep",
                        "key": f"{fp}::{vk}",
                        "error": result.error,
                    })

        logger.info("参数扫描完成: %d 版本, %d 失败",
                     len(self._all_sweep_results),
                     sum(1 for e in self._all_errors if e["type"] == "sweep"))

    # ── Stage 4: 评分与筛选 ─────────────────────────

    def _stage_score(self):
        """对所有版本评分, 筛选最优 preset。"""
        logger.info("─" * 40)
        logger.info("Stage 4/6: 评分与最优筛选")

        if not self._all_sweep_results:
            logger.warning("无扫描结果可供评分")
            return

        weights = self._config.get("scoring", {}).get("weights", {})
        scored = []
        for r in self._all_sweep_results:
            score = _score_version(r, weights)
            r["score"] = score
            scored.append(r)

        # 选择 top-N
        top_n = self._config.get("reports", {}).get("top_n_best_presets", 5)

        # 按 category 分别选出最佳
        best_by_category: dict[str, list[dict]] = {}
        for r in scored:
            cat = r.get("category", "unknown")
            best_by_category.setdefault(cat, []).append(r)

        self._best_presets = []
        for cat, results in best_by_category.items():
            results.sort(key=lambda x: x.get("score", 0), reverse=True)
            for r in results[:max(1, top_n // len(best_by_category))]:
                r["rank_in_category"] = results.index(r) + 1
                self._best_presets.append(r)

        # 全局 top-N
        scored.sort(key=lambda x: x.get("score", 0), reverse=True)
        self._global_best = scored[:top_n]

        logger.info("评分完成: %d 个版本, %d 个入选最佳",
                     len(scored), len(self._best_presets))
        logger.info("全局最高分: %.4f (%s)",
                     scored[0].get("score", 0) if scored else 0,
                     scored[0].get("category", "?") if scored else "?")

    # ── Stage 5: 吞吐量基准 ─────────────────────────

    def _stage_bench(self):
        """吞吐量基准测试。"""
        logger.info("─" * 40)
        logger.info("Stage 5/6: 吞吐量基准")

        if not self._all_sweep_results:
            logger.info("无数据, 跳过吞吐量基准")
            return

        # 计算处理耗时统计
        total_time = sum(
            r.get("metrics_after", {}).get("duration_s", 0)
            for r in self._all_sweep_results
        )
        num = len(self._all_sweep_results)
        avg_time = total_time / max(num, 1)

        self._benchmark = {
            "total_versions": num,
            "avg_per_version_s": round(avg_time, 2),
            "estimated_per_hour": int(3600 / max(avg_time, 0.01)),
            "estimated_per_night_12h": int(3600 * 12 / max(avg_time, 0.01)),
        }
        logger.info("吞吐量: %.1fs/版本, %d/h, %d/12h",
                     avg_time,
                     self._benchmark["estimated_per_hour"],
                     self._benchmark["estimated_per_night_12h"])

    # ── Stage 6: 报告 ───────────────────────────────

    def _stage_report(self, force: bool = False):
        """生成所有报告。"""
        logger.info("─" * 40)
        logger.info("Stage 6/6: 生成报告")

        timings = {
            "start": self._start_ts,
            "end": self._end_ts or datetime.now(timezone.utc).isoformat(),
            "total_elapsed_s": self._timings.get("total_elapsed_s", 0),
            "stages": self._stage_times,
        }
        snapshot = self._guard.get_snapshot()

        paths = self._reporter.build_all(
            metrics_list=self._all_metrics,
            sweep_results=self._all_sweep_results,
            best_presets=self._best_presets if hasattr(self, "_best_presets") else [],
            errors=self._all_errors + self._ckpt.get_failed_jobs(),
            timings=timings,
            resource_snapshot=snapshot,
            config=self._config,
        )

        for name, p in paths.items():
            logger.info("  %s → %s", name, p)

        # 写日志文件
        log_path = self._output_dir / "logs" / "night_worker.jsonl"
        log_path.parent.mkdir(parents=True, exist_ok=True)
        with open(log_path, "a", encoding="utf-8") as f:
            f.write(json.dumps({
                "ts": datetime.now(timezone.utc).isoformat(),
                "run_name": self._run_name,
                "analyzed": len(self._all_metrics),
                "versions": len(self._all_sweep_results),
                "errors": len(self._all_errors),
                "elapsed_s": self._timings.get("total_elapsed_s", 0),
            }) + "\n")

    # ── 辅助 ────────────────────────────────────────

    def _setup_logging(self):
        log_dir = self._output_dir / "logs"
        log_dir.mkdir(parents=True, exist_ok=True)
        log_file = log_dir / "night_worker.log"

        fmt = logging.Formatter(
            "%(asctime)s [%(levelname)-7s] %(name)s — %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )

        # 文件 handler
        fh = logging.FileHandler(str(log_file), encoding="utf-8")
        fh.setLevel(logging.DEBUG)
        fh.setFormatter(fmt)
        logger.addHandler(fh)

        # 控制台 handler
        ch = logging.StreamHandler(sys.stdout)
        ch.setLevel(logging.INFO)
        ch.setFormatter(fmt)
        logger.addHandler(ch)

        logger.setLevel(logging.DEBUG)
        logger.propagate = False

        # 同时设置子模块 logger
        for name in ["night_worker.job_queue", "night_worker.resource_guard"]:
            child = logging.getLogger(name)
            child.setLevel(logging.DEBUG)
            child.propagate = True


# ═══════════════════════════════════════════════════════════════
# 辅助函数
# ═══════════════════════════════════════════════════════════════

def _load_yaml(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def _scan_audio(directory: Path) -> list[str]:
    """扫描目录下所有音频文件, 返回绝对路径列表。"""
    exts = {".wav", ".mp3", ".flac", ".aiff", ".aif", ".m4a", ".ogg"}
    files = []
    for ext in exts:
        files.extend(str(p) for p in directory.glob(f"*{ext}"))
        files.extend(str(p) for p in directory.glob(f"*{ext.upper()}"))
    return sorted(files)


def _generate_test_audio(directory: Path, count: int,
                          duration_s: float, sr: int) -> list[str]:
    """生成合成测试音频文件 (多频正弦波混合)。"""
    paths = []
    for i in range(count):
        t = np.linspace(0, duration_s, int(sr * duration_s), endpoint=False)

        # 不同风格的基础信号
        styles = [
            # [sub, bass, mid, presence, air] 各频率相对于基频的倍率
            {"freqs": [55, 110, 440, 2000, 8000], "amps": [0.6, 0.4, 0.5, 0.3, 0.2]},
            {"freqs": [40, 80,  500, 3000, 10000], "amps": [0.8, 0.5, 0.3, 0.2, 0.15]},
            {"freqs": [65, 130, 350, 1500, 6000], "amps": [0.4, 0.3, 0.6, 0.4, 0.3]},
            {"freqs": [50, 100, 600, 2500, 9000], "amps": [0.5, 0.35, 0.4, 0.5, 0.25]},
            {"freqs": [45, 90,  420, 1800, 7000], "amps": [0.7, 0.45, 0.35, 0.25, 0.18]},
        ]
        style = styles[i % len(styles)]

        # 构建多频混合信号 (双声道)
        left = np.zeros_like(t)
        right = np.zeros_like(t)
        for freq, amp in zip(style["freqs"], style["amps"]):
            phase = random.random() * 2 * math.pi
            left += amp * np.sin(2 * math.pi * freq * t + phase)
            right += amp * np.sin(2 * math.pi * freq * t + phase + random.random() * 0.3)

        # 立体声展宽
        stereo = np.column_stack([left, right]) * 0.5
        stereo = stereo.astype(np.float32)

        # 写入 WAV
        import soundfile
        out_path = str(directory / f"night_test_{i + 1:02d}.wav")
        soundfile.write(out_path, stereo, sr, subtype="PCM_16")
        paths.append(out_path)

    return paths


def _build_version_grid(categories: dict, max_per_audio: int) -> list[dict]:
    """展开 preset_grid 为线性版本列表。"""
    versions = []
    for cat_name, cat_cfg in categories.items():
        sweep = cat_cfg.get("sweep_params", {})
        fixed = cat_cfg.get("fixed_params", {})

        # 生成各参数采样值
        axes = {}
        for pname, pcfg in sweep.items():
            lo, hi = pcfg["range"]
            steps = pcfg["steps"]
            if steps <= 1:
                axes[pname] = [lo]
            else:
                axes[pname] = [round(lo + (hi - lo) * i / (steps - 1), 4)
                               for i in range(steps)]

        # 笛卡尔积
        param_names = list(axes.keys())
        if not param_names:
            # 无扫描参数, 只用 fixed_params
            params = dict(fixed)
            versions.append({
                "category": cat_name,
                "version_key": f"{cat_name}/fixed",
                "params": params,
            })
            continue

        for values in itertools.product(*axes.values()):
            params = dict(fixed)
            for pname, val in zip(param_names, values):
                params[pname] = val

            vk = _params_to_key(params, prefix=f"{cat_name}/")
            versions.append({
                "category": cat_name,
                "version_key": vk,
                "params": params,
            })

    # 截断至最大版本数
    if len(versions) > max_per_audio:
        logger.warning("版本组合 %d 超过上限 %d, 随机截断", len(versions), max_per_audio)
        random.shuffle(versions)
        versions = versions[:max_per_audio]

    return versions


def _params_to_key(params: dict, prefix: str = "") -> str:
    """将参数 dict 压缩为一个短 key, 如 "warm_reality/P02_2.5_P05_1.0"."""
    parts = []
    for k in sorted(params.keys()):
        v = params[k]
        if isinstance(v, float):
            parts.append(f"{k}_{v:.2f}".rstrip("0").rstrip("."))
        else:
            parts.append(f"{k}_{v}")
    return prefix + "_".join(parts)[:120]  # 限制长度


def _hash_key(key: str, length: int = 12) -> str:
    """将 version_key 哈希为短唯一标识符, 避免文件名冲突。"""
    import hashlib
    h = hashlib.sha256(key.encode()).hexdigest()[:length]
    return h


def _score_version(result: dict, weights: dict) -> float:
    """对一个处理版本打分 (0-1, 越高越好)。"""
    if not weights:
        weights = {
            "spectrum_balance": 0.25,
            "dynamic_health": 0.20,
            "stereo_stability": 0.15,
            "crest_normalization": 0.10,
            "air_presence": 0.10,
            "bass_warmth": 0.10,
            "transient_retention": 0.10,
        }

    metrics = result.get("metrics_after", {})
    spec = metrics.get("spectrum", {})
    dyn = metrics.get("dynamics", {})
    st = metrics.get("stereo", {})

    subs = {
        # 频谱平衡: sub/bass/mid/presence 不至于极端
        "spectrum_balance": _band_balance_score(spec),
        # 动态健康: crest 在 3-7, dynamic_range 在 3-20
        "dynamic_health": _dynamic_health_score(dyn),
        # 立体声稳定: correlation 在 0.3-0.85
        "stereo_stability": _stereo_score(st),
        # crest 标准化: crest 越接近 4-6 越好
        "crest_normalization": _crest_score(dyn),
        # 空气感: air 不要太低
        "air_presence": _clamp_norm(spec.get("air", -90), -30, -10),
        # 低音温暖: bass 不要太低
        "bass_warmth": _clamp_norm(spec.get("bass", -90), -18, -3),
        # 瞬态保持: (占位, 实际中从 processor fingerprint 获取)
        "transient_retention": 0.5,
    }

    score = sum(weights.get(k, 0) * subs.get(k, 0) for k in subs)
    return round(score, 4)


def _band_balance_score(spec: dict) -> float:
    """检查频带是否没有极端值。"""
    sub = spec.get("sub_bass", -90)
    bass = spec.get("bass", -90)
    presence = spec.get("presence", -90)
    air = spec.get("air", -90)
    # 各频带不能太弱
    s = 1.0
    if sub < -30: s -= 0.2
    if bass < -18: s -= 0.2
    if presence < -18: s -= 0.2
    if air < -30: s -= 0.15
    # 也不能太强
    if sub > -3: s -= 0.15
    if bass > -1: s -= 0.1
    return max(0.0, s)


def _dynamic_health_score(dyn: dict) -> float:
    crest = dyn.get("crest_factor", 3)
    dr = dyn.get("dynamic_range_db", 5)
    s = 1.0
    if crest < 2: s -= 0.3
    if crest > 8: s -= 0.2
    if dr < 3: s -= 0.3
    if dr > 20: s -= 0.1
    if 3 <= crest <= 7 and 5 <= dr <= 18:
        s = min(1.0, s + 0.2)
    return max(0.0, s)


def _stereo_score(st: dict) -> float:
    corr = st.get("correlation_lr", 0.5)
    if 0.3 <= corr <= 0.85:
        return 1.0
    if corr < 0.2:
        return 0.4  # 太宽, mono 兼容风险
    if corr > 0.95:
        return 0.6  # 太窄
    return 0.7


def _crest_score(dyn: dict) -> float:
    crest = dyn.get("crest_factor", 3)
    # 理想区间 4-6
    if 4 <= crest <= 6:
        return 1.0
    dist = min(abs(crest - 4), abs(crest - 6))
    return max(0.0, 1.0 - dist / 6.0)


def _clamp_norm(val: float, lo: float, hi: float) -> float:
    """将值 clamp 到 [lo, hi] 并线性归一化到 [0,1]."""
    v = max(lo, min(hi, val))
    return (v - lo) / max(hi - lo, 0.01)


def _restore_metrics_from_checkpoint(ckpt: CheckpointStore,
                                      audio_files: list[str]) -> list[dict]:
    """从 checkpoint 恢复已分析的 metrics。"""
    metrics = []
    for fp in audio_files:
        data = ckpt._read_json(ckpt._analyzed_path)
        if isinstance(data, dict) and fp in data:
            entry = data[fp]
            summary = entry.get("summary", {})
            if summary:
                summary["file_path"] = fp
                metrics.append(summary)
    return metrics


class ResourceWarning(RuntimeWarning):
    """资源不足警告 — 应停止生成新内容但不终止整个运行。"""
    pass


# ═══════════════════════════════════════════════════════════════
# CLI
# ═══════════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(
        description="Moodify Night Worker — 夜间自动计算引擎",
    )
    parser.add_argument(
        "--config", "-c",
        default="configs/night_jobs.yaml",
        help="任务配置文件路径 (默认 configs/night_jobs.yaml)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="仅扫描和校验配置, 不实际执行",
    )
    parser.add_argument(
        "--reset",
        choices=["analyze", "sweep", "all"],
        help="重置 checkpoint 阶段后重新运行",
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="详细日志输出",
    )
    args = parser.parse_args()

    # 解析配置路径
    config_path = args.config
    if not os.path.isabs(config_path):
        config_path = os.path.join(_PROJECT_ROOT, config_path)

    if not os.path.exists(config_path):
        print(f"错误: 配置文件不存在: {config_path}", file=sys.stderr)
        sys.exit(1)

    worker = NightWorker(config_path)

    # 重置
    if args.reset:
        if args.reset in ("analyze", "all"):
            worker._ckpt.reset_stage("analyze")
            print("已重置: analyze 阶段")
        if args.reset in ("sweep", "all"):
            worker._ckpt.reset_stage("sweep")
            print("已重置: sweep 阶段")
        print("重置完成, 退出")
        return

    # 干跑
    if args.dry_run:
        print(f"配置: {config_path}")
        print(f"运行名: {worker._run_name}")
        print(f"输入目录: {worker._input_dir}")
        print(f"输出目录: {worker._output_dir}")
        audio_files = _scan_audio(worker._input_dir)
        print(f"音频文件: {len(audio_files)}")
        grid = _load_yaml(worker._preset_grid_path)
        cats = grid.get("preset_categories", {})
        versions = _build_version_grid(cats, 50)
        print(f"参数网格: {len(cats)} 类别, {len(versions)} 版本")
        limits = worker._limits
        print(f"并行限制: {limits.parallel_min}-{limits.parallel_max}"
              f" (默认 {limits.parallel_default})")
        print(f"磁盘安全线: {limits.disk_min_free_gb}GB")
        print("干跑完成 (未执行实际任务)")
        return

    # 正式运行
    exit_code = worker.run()
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
