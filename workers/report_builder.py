"""report_builder.py — Moodify Night Worker 报告生成系统.

生成:
  - CSV: 音频指标表 + 参数扫描结果表
  - JSON: 最佳 preset 配置
  - Markdown: 汇总报告 + 最佳 preset 报告 + 错误报告 + 吞吐量报告

用法:
    from workers.report_builder import ReportBuilder

    rb = ReportBuilder("runs/night_auto")
    rb.build_all(metrics_list, sweep_results, best_presets, errors, timings)
"""

from __future__ import annotations

import csv
import json
import os
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


class ReportBuilder:
    """生成所有 Night Worker 输出报告。"""

    def __init__(self, run_dir: str):
        self._run_dir = Path(run_dir)
        self._reports_dir = self._run_dir / "reports"
        self._metrics_dir = self._run_dir / "output" / "metrics"
        self._configs_dir = self._run_dir / "configs"
        for d in [self._reports_dir, self._metrics_dir, self._configs_dir]:
            d.mkdir(parents=True, exist_ok=True)

        self._run_start: str = ""
        self._run_end: str = ""

    # ── 公共 API ────────────────────────────────────

    def build_all(self,
                  metrics_list: list[dict],
                  sweep_results: list[dict],
                  best_presets: list[dict],
                  errors: list[dict],
                  timings: dict,
                  resource_snapshot: dict,
                  config: dict,
                  ) -> dict[str, str]:
        """生成所有报告。返回 {report_name: file_path}。"""
        self._run_start = timings.get("start", "")
        self._run_end = timings.get("end", "")

        paths = {}

        # CSV
        paths["audio_metrics_csv"] = self._write_audio_metrics_csv(metrics_list)
        paths["sweep_results_csv"] = self._write_sweep_results_csv(sweep_results)

        # JSON
        paths["best_presets_json"] = self._write_best_presets_json(best_presets)

        # Markdown
        paths["night_summary"] = self._write_night_summary_md(
            metrics_list, sweep_results, best_presets, errors,
            timings, resource_snapshot, config,
        )
        paths["best_presets_md"] = self._write_best_presets_md(best_presets, sweep_results)
        paths["error_report"] = self._write_error_report_md(errors)
        paths["throughput_report"] = self._write_throughput_report_md(
            sweep_results, timings, resource_snapshot,
        )

        return paths

    # ── CSV ─────────────────────────────────────────

    def _write_audio_metrics_csv(self, metrics_list: list[dict]) -> str:
        path = self._metrics_dir / "audio_metrics.csv"
        if not metrics_list:
            with open(path, "w", newline="") as f:
                f.write("# No metrics collected\n")
            return str(path)

        headers = [
            "file", "duration_s", "sr", "ch",
            "rms_total", "rms_sub", "rms_bass", "rms_low_mid", "rms_mid",
            "rms_presence", "rms_air",
            "peak_db", "crest_factor", "dynamic_range_db", "correlation_lr",
            "health",
        ]
        with open(path, "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(headers)
            for m in metrics_list:
                spec = m.get("spectrum", {})
                dyn = m.get("dynamics", {})
                st = m.get("stereo", {})
                w.writerow([
                    m.get("file_path", ""),
                    m.get("duration_s", ""),
                    m.get("sample_rate", ""),
                    m.get("channels", ""),
                    m.get("rms_total", ""),
                    spec.get("sub_bass", ""),
                    spec.get("bass", ""),
                    spec.get("low_mid", ""),
                    spec.get("mid", ""),
                    spec.get("presence", ""),
                    spec.get("air", ""),
                    dyn.get("peak_db", ""),
                    dyn.get("crest_factor", ""),
                    dyn.get("dynamic_range_db", ""),
                    st.get("correlation_lr", ""),
                    m.get("overall_health", ""),
                ])
        return str(path)

    def _write_sweep_results_csv(self, sweep_results: list[dict]) -> str:
        path = self._metrics_dir / "parameter_sweep_results.csv"
        if not sweep_results:
            with open(path, "w", newline="") as f:
                f.write("# No sweep results\n")
            return str(path)

        param_keys = sorted(
            set().union(*(r.get("params", {}).keys() for r in sweep_results))
        )
        headers = [
            "file", "category", "version_key",
            *[f"param_{k}" for k in param_keys],
            "health_before", "health_after", "score",
        ]
        with open(path, "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(headers)
            for r in sweep_results:
                params = r.get("params", {})
                w.writerow([
                    r.get("file", ""),
                    r.get("category", ""),
                    r.get("version_key", ""),
                    *[params.get(k, "") for k in param_keys],
                    r.get("health_before", ""),
                    r.get("health_after", ""),
                    r.get("score", ""),
                ])
        return str(path)

    # ── JSON ────────────────────────────────────────

    def _write_best_presets_json(self, best_presets: list[dict]) -> str:
        path = self._configs_dir / "best_presets.json"
        payload = {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "count": len(best_presets),
            "presets": best_presets,
        }
        with open(path, "w", encoding="utf-8") as f:
            json.dump(payload, f, ensure_ascii=False, indent=2)
        return str(path)

    # ── Markdown: 主汇总 ────────────────────────────

    def _write_night_summary_md(self,
                                 metrics_list: list[dict],
                                 sweep_results: list[dict],
                                 best_presets: list[dict],
                                 errors: list[dict],
                                 timings: dict,
                                 resource_snapshot: dict,
                                 config: dict,
                                 ) -> str:
        path = self._reports_dir / "night_summary.md"

        num_audio = len(metrics_list)
        num_versions = len(sweep_results)
        num_errors = len(errors)

        # 塑料感风险最高的音频: sub_bass 最低 + bass 最低
        plastic_risk = sorted(
            metrics_list,
            key=lambda m: (
                m.get("spectrum", {}).get("sub_bass", 0) +
                m.get("spectrum", {}).get("bass", 0)
            ),
        )[:5]

        # 最佳 preset
        top_presets = sorted(best_presets, key=lambda p: p.get("score", 0), reverse=True)[:5]

        # 过度处理风险参数 (crest_factor 降低最多的前 5)
        overprocessed = sorted(
            sweep_results,
            key=lambda r: r.get("crest_drop", 0),
        )[:5]

        # 吞吐量
        total_elapsed = timings.get("total_elapsed_s", 1)
        throughput_per_audio = total_elapsed / max(num_audio, 1)
        est_per_night = int(3600 * 12 / max(throughput_per_audio, 1))

        lines = [
            f"# Moodify Night Worker — 运行汇总",
            f"",
            f"**运行名**: `{config.get('run_name', '?')}`",
            f"**开始时间**: {timings.get('start', '?')}",
            f"**结束时间**: {timings.get('end', '?')}",
            f"**总耗时**: {_format_seconds(timings.get('total_elapsed_s', 0))}",
            f"",
            f"---",
            f"",
            f"## 1. 核心数据",
            f"",
            f"| 指标 | 值 |",
            f"|------|----|",
            f"| 分析音频数 | {num_audio} |",
            f"| 生成处理版本数 | {num_versions} |",
            f"| 错误/失败数 | {num_errors} |",
            f"| 服务器平均每首处理耗时 | {_format_seconds(throughput_per_audio)} |",
            f"| 预计一晚上能处理数量 | {est_per_night} 首 |",
            f"",
            f"---",
            f"",
            f"## 2. 塑料感风险最高的音频",
            f"",
            f"(sub_bass + bass 最低, 可能缺乏温暖感和物理重量感)",
            f"",
            f"| # | 文件 | Health | SubBass | Bass |",
            f"|---|------|--------|---------|------|",
        ]
        for i, m in enumerate(plastic_risk, 1):
            spec = m.get("spectrum", {})
            lines.append(
                f"| {i} | `{m.get('file_path', '?')}` | {m.get('overall_health', '?')} "
                f"| {spec.get('sub_bass', '?')} | {spec.get('bass', '?')} |"
            )

        lines.extend([
            f"",
            f"---",
            f"",
            f"## 3. 最佳 Preset 参数组合",
            f"",
            f"| # | 类别 | 音频 | 分数 |",
            f"|---|------|------|------|",
        ])
        for i, p in enumerate(top_presets, 1):
            lines.append(
                f"| {i} | {p.get('category', '?')} "
                f"| `{p.get('file', '?')}` "
                f"| {p.get('score', 0):.2f} |"
            )

        lines.extend([
            f"",
            f"---",
            f"",
            f"## 4. 过度处理风险参数",
            f"",
            f"(crest_factor 下降最多的版本, 表明可能被过度压缩)",
            f"",
            f"| # | 类别 | 版本 | Crest Δ |",
            f"|---|------|------|---------|",
        ])
        for i, r in enumerate(overprocessed, 1):
            lines.append(
                f"| {i} | {r.get('category', '?')} "
                f"| {r.get('version_key', '?')} "
                f"| {r.get('crest_drop', 0):.1f} |"
            )

        lines.extend([
            f"",
            f"---",
            f"",
            f"## 5. 服务器资源",
            f"",
            f"| 指标 | 值 |",
            f"|------|----|",
            f"| CPU 使用率 | {resource_snapshot.get('cpu_pct', '?')}% |",
            f"| 内存使用 | {resource_snapshot.get('mem_used_gb', '?')} GB |",
            f"| 磁盘剩余 | {resource_snapshot.get('disk_free_gb', '?')} GB |",
            f"| 输出目录大小 | {resource_snapshot.get('output_dir_size_gb', '?')} GB |",
            f"| 并发 Worker | {resource_snapshot.get('current_workers', '?')} |",
            f"",
            f"---",
            f"",
            f"## 6. 下一步建议",
            f"",
            f"1. 查看 `best_presets.md` 了解最优参数组合的详细信息",
            f"2. 查看 `throughput_report.md` 评估服务器处理能力",
            f"3. 将高评分 preset 参数提交到 `moodify-core-package/src/moodify/v01_presets.py`",
            f"4. 如果有过度处理的风险参数组合, 记录到安全模块黑名单",
            f"5. 如果某类参数系统性表现最好, 可升级为默认 preset",
            f"6. 检查 `error_report.md` 修复失败的 job",
            f"",
        ])

        with open(path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))
        return str(path)

    # ── Markdown: 最佳 Preset ───────────────────────

    def _write_best_presets_md(self, best_presets: list[dict],
                                sweep_results: list[dict]) -> str:
        path = self._reports_dir / "best_presets.md"
        lines = [
            f"# 最佳 Preset 参数组合",
            f"",
            f"共 {len(best_presets)} 个候选最优 preset。",
            f"",
        ]

        for i, p in enumerate(sorted(best_presets,
                                      key=lambda x: x.get("score", 0),
                                      reverse=True), 1):
            lines.extend([
                f"## {i}. {p.get('category', '?')} — {p.get('version_key', '?')}",
                f"",
                f"- **文件**: `{p.get('file', '?')}`",
                f"- **分数**: {p.get('score', 0):.4f}",
                f"- **健康前**: {p.get('health_before', '?')}",
                f"- **健康后**: {p.get('health_after', '?')}",
                f"",
                f"### 参数",
                f"",
                f"```json",
                json.dumps(p.get("params", {}), ensure_ascii=False, indent=2),
                f"```",
                f"",
            ])

        with open(path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))
        return str(path)

    # ── Markdown: 错误报告 ──────────────────────────

    def _write_error_report_md(self, errors: list[dict]) -> str:
        path = self._reports_dir / "error_report.md"
        lines = [
            f"# 错误报告",
            f"",
        ]
        if not errors:
            lines.append("✅ 本次运行无错误。")
        else:
            lines.append(f"共 {len(errors)} 个错误。")
            lines.append("")
            for i, e in enumerate(errors, 1):
                lines.extend([
                    f"## {i}. {e.get('type', '?')}: {e.get('key', '?')}",
                    f"",
                    f"```",
                    e.get("error", "(无错误信息)"),
                    f"```",
                    f"",
                ])

        with open(path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))
        return str(path)

    # ── Markdown: 吞吐量报告 ────────────────────────

    def _write_throughput_report_md(self,
                                     sweep_results: list[dict],
                                     timings: dict,
                                     resource_snapshot: dict) -> str:
        path = self._reports_dir / "throughput_report.md"

        total_s = timings.get("total_elapsed_s", 1)
        num_versions = max(len(sweep_results), 1)

        # 估算
        per_version = total_s / num_versions
        per_hour = int(3600 / max(per_version, 1))
        per_night = per_hour * 12

        # 各阶段耗时
        stages = timings.get("stages", {})

        lines = [
            f"# 吞吐量报告",
            f"",
            f"## 总体",
            f"",
            f"| 指标 | 值 |",
            f"|------|----|",
            f"| 总耗时 | {_format_seconds(total_s)} |",
            f"| 生成版本数 | {num_versions} |",
            f"| 每版本平均 | {_format_seconds(per_version)} |",
            f"| 每小时产能 | {per_hour} 版本 |",
            f"| 12小时预估 | {per_night} 版本 |",
            f"",
        ]

        if stages:
            lines.extend([
                f"## 各阶段耗时",
                f"",
                f"| 阶段 | 耗时 |",
                f"|------|------|",
            ])
            for name, s in stages.items():
                lines.append(f"| {name} | {_format_seconds(s)} |")

        lines.extend([
            f"",
            f"## 资源快照",
            f"",
            f"| 指标 | 值 |",
            f"|------|----|",
            f"| CPU | {resource_snapshot.get('cpu_pct', '?')}% |",
            f"| 内存 | {resource_snapshot.get('mem_used_gb', '?')} GB |",
            f"| 磁盘 | {resource_snapshot.get('disk_free_gb', '?')} GB 剩余 |",
            f"| Workers | {resource_snapshot.get('current_workers', '?')} |",
            f"",
        ])

        with open(path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))
        return str(path)


# ── helpers ─────────────────────────────────────────────

def _format_seconds(s: float) -> str:
    if s < 1:
        return f"{s * 1000:.0f}ms"
    if s < 60:
        return f"{s:.1f}s"
    if s < 3600:
        m, sec = divmod(s, 60)
        return f"{int(m)}m {int(sec)}s"
    h, rem = divmod(s, 3600)
    m, _ = divmod(rem, 60)
    return f"{int(h)}h {int(m)}m"
