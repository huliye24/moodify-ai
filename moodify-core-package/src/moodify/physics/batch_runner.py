"""Moodify 异步实验批处理引擎.

用法:
  python batch_runner.py                      # 运行默认实验套件
  python batch_runner.py --suite quick        # 快速验证 (5 min)
  python batch_runner.py --suite full         # 完整套件 (2-4 hours)
  python batch_runner.py --suite bmatrix      # B矩阵辨识

流程:
  1. 读取 experiment_suites.yaml 获取实验定义
  2. 按依赖顺序执行实验
  3. 每个实验: 运行 → 保存结果 → 记录耗时
  4. 全部完成后: 生成 Markdown 报告 → 写入 output_root/reports/
  5. 自动退出 (不残留进程)

输出结构:
  output_root/
    reports/
      YYYY-MM-DD_HH-MM-SS_report.md    ← 人类可读报告
      YYYY-MM-DD_HH-MM-SS_summary.json ← 机器可读摘要
    experiments/
      {suite_name}/
        {experiment_id}/
          results.json
          raw_data.csv
"""

import os, sys, json, time, argparse, subprocess
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass, field
from typing import Callable

# ── 配置 ──────────────────────────────────────────────

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent.parent
OUTPUT_ROOT = PROJECT_ROOT / "outputs"
REPORT_DIR = OUTPUT_ROOT / "reports"

# 实验套件定义
EXPERIMENT_SUITES = {
    "quick": {
        "description": "快速验证套件 — 验证核心假设, ~5 min",
        "experiments": [
            {"id": "D_diagnosis_noise", "module": "moodify.physics.experiments", "func": "experiment_D", "kwargs": {"n_repeats": 30}},
            {"id": "E_m_factor", "module": "moodify.physics.experiments", "func": "experiment_E"},
            {"id": "K_euclidean_vs_mahalanobis", "module": "moodify.physics.experiments_2", "func": "experiment_K"},
        ],
    },
    "engineering": {
        "description": "工程边界分析 — 参数灵敏度+交互+强度校准, ~25 min",
        "experiments": [
            {"id": "P_param_sensitivity", "module": "moodify.physics.experiments_3_engineering", "func": "experiment_P"},
            {"id": "Q_param_interactions", "module": "moodify.physics.experiments_3_engineering", "func": "experiment_Q"},
            {"id": "R_strength_calibration", "module": "moodify.physics.experiments_3_engineering", "func": "experiment_R"},
        ],
    },
    "bmatrix": {
        "description": "B矩阵辨识 — 单情绪或多情绪, ~10 min/情绪",
        "experiments": [
            {"id": "bmatrix_all", "module": "moodify.physics.b_matrix_parallel", "func": "main_cli",
             "kwargs": {"samples": 200, "workers": 16}},
        ],
    },
    "validation": {
        "description": "全管线验证 — 搜索+DSP+重诊断, ~15 min",
        "experiments": [
            {"id": "A_b_matrix", "module": "moodify.physics.experiments", "func": "experiment_A", "kwargs": {"n_samples": 50}},
            {"id": "B_closed_loop", "module": "moodify.physics.experiments", "func": "experiment_B"},
            {"id": "F_plasticity", "module": "moodify.physics.experiments", "func": "experiment_F"},
        ],
    },
    "full": {
        "description": "完整实验套件 — 所有验证+工程+辨识, ~2-4 hours",
        "experiments": [
            {"id": "00_diagnosis_noise", "module": "moodify.physics.experiments", "func": "experiment_D", "kwargs": {"n_repeats": 50}},
            {"id": "01_m_factor", "module": "moodify.physics.experiments", "func": "experiment_E"},
            {"id": "02_plasticity", "module": "moodify.physics.experiments", "func": "experiment_F"},
            {"id": "03_param_sensitivity", "module": "moodify.physics.experiments_3_engineering", "func": "experiment_P"},
            {"id": "04_param_interactions", "module": "moodify.physics.experiments_3_engineering", "func": "experiment_Q"},
            {"id": "05_strength_calibration", "module": "moodify.physics.experiments_3_engineering", "func": "experiment_R"},
            {"id": "06_euclidean_vs_mahalanobis", "module": "moodify.physics.experiments_2", "func": "experiment_K"},
            {"id": "07_b_matrix", "module": "moodify.physics.b_matrix_parallel", "func": "main_cli",
             "kwargs": {"samples": 500, "workers": 16}},
            {"id": "08_closed_loop", "module": "moodify.physics.experiments", "func": "experiment_B"},
        ],
    },
}


@dataclass
class ExperimentResult:
    id: str
    status: str  # "PASS", "FAIL", "ERROR", "SKIP"
    verdict: str = ""
    elapsed_s: float = 0.0
    error_msg: str = ""
    data: dict = field(default_factory=dict)


def run_single_experiment(exp_def: dict, suite_dir: Path) -> ExperimentResult:
    """执行单个实验, 捕获异常, 返回结构化结果."""
    exp_id = exp_def["id"]
    module_name = exp_def["module"]
    func_name = exp_def["func"]
    kwargs = exp_def.get("kwargs", {})

    t0 = time.perf_counter()

    try:
        # 动态导入并执行
        import importlib
        mod = importlib.import_module(module_name)
        func = getattr(mod, func_name)

        # 重定向输出目录
        if hasattr(mod, 'OUTPUT_BASE'):
            mod.OUTPUT_BASE = suite_dir

        result = func(**kwargs) if kwargs else func()

        elapsed = time.perf_counter() - t0
        if isinstance(result, dict):
            verdict = result.get("verdict", "?")
            return ExperimentResult(
                id=exp_id, status="PASS" if "PASS" in str(verdict) or "OK" in str(verdict) else "FAIL",
                verdict=str(verdict), elapsed_s=elapsed, data=result,
            )
        else:
            return ExperimentResult(
                id=exp_id, status="PASS", verdict=str(result)[:100],
                elapsed_s=elapsed,
            )

    except Exception as e:
        import traceback
        elapsed = time.perf_counter() - t0
        return ExperimentResult(
            id=exp_id, status="ERROR", verdict="",
            elapsed_s=elapsed, error_msg=f"{e}\n{traceback.format_exc()[:500]}",
        )


def generate_report(suite_name: str, description: str, results: list[ExperimentResult],
                    total_s: float, output_dir: Path) -> str:
    """生成 Markdown 实验报告."""
    now = datetime.now()
    timestamp = now.strftime("%Y-%m-%d %H:%M:%S")
    report_name = now.strftime("%Y-%m-%d_%H-%M-%S")

    passed = sum(1 for r in results if r.status == "PASS")
    failed = sum(1 for r in results if r.status == "FAIL")
    errors = sum(1 for r in results if r.status == "ERROR")

    lines = [
        f"# Moodify 实验报告",
        f"",
        f"**套件**: {suite_name} — {description}",
        f"**时间**: {timestamp}",
        f"**总耗时**: {total_s:.0f}s ({total_s/60:.1f} min)",
        f"**结果**: {passed} PASS / {failed} FAIL / {errors} ERROR / {len(results)} total",
        f"",
        f"---",
        f"",
        f"## 实验结果",
        f"",
        f"| # | 实验 | 状态 | 判定 | 耗时 |",
        f"|---|------|------|------|------|",
    ]

    for i, r in enumerate(results):
        status_icon = {"PASS": "✅", "FAIL": "❌", "ERROR": "⚠️", "SKIP": "⏭️"}.get(r.status, "?")
        lines.append(f"| {i+1} | {r.id} | {status_icon} {r.status} | {r.verdict[:60]} | {r.elapsed_s:.0f}s |")

    lines += [
        f"",
        f"---",
        f"",
        f"## 详细结果",
        f"",
    ]

    for r in results:
        lines.append(f"### {r.id} — {r.status}")
        lines.append(f"- **耗时**: {r.elapsed_s:.0f}s")
        lines.append(f"- **判定**: {r.verdict}")
        if r.error_msg:
            lines.append(f"- **错误**:")
            lines.append(f"```")
            lines.append(r.error_msg[:500])
            lines.append(f"```")
        if r.data:
            # Show key metrics
            for k, v in r.data.items():
                if k in ("timestamp", "verdict", "h1_accepted", "experiment", "assumption_tested"):
                    lines.append(f"- **{k}**: {v}")
        lines.append("")

    lines += [
        f"---",
        f"",
        f"*报告自动生成 · {timestamp} · Moodify Physics Batch Runner*",
    ]

    report_text = "\n".join(lines)

    # 写入报告
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    report_path = REPORT_DIR / f"{report_name}_report.md"
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(report_text)

    # 写入机器可读摘要
    summary = {
        "timestamp": timestamp,
        "suite": suite_name,
        "total_s": round(total_s, 1),
        "passed": passed, "failed": failed, "errors": errors,
        "results": [
            {"id": r.id, "status": r.status, "verdict": r.verdict, "elapsed_s": round(r.elapsed_s, 1)}
            for r in results
        ],
    }
    summary_path = REPORT_DIR / f"{report_name}_summary.json"
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)

    return report_text


def main():
    parser = argparse.ArgumentParser(description="Moodify 异步实验批处理引擎")
    parser.add_argument("--suite", default="quick", choices=list(EXPERIMENT_SUITES.keys()),
                        help="实验套件名称 (默认: quick)")
    parser.add_argument("--output", default=None, help="输出目录 (默认: outputs/)")
    parser.add_argument("--dry-run", action="store_true", help="仅列出实验, 不执行")
    args = parser.parse_args()

    suite = EXPERIMENT_SUITES[args.suite]
    exp_list = suite["experiments"]

    print("=" * 60)
    print(f"Moodify Experiment Batch Runner")
    print(f"Suite: {args.suite} — {suite['description']}")
    print(f"Experiments: {len(exp_list)}")
    print(f"Output: {OUTPUT_ROOT}")
    print("=" * 60)

    if args.dry_run:
        for i, exp in enumerate(exp_list):
            print(f"  [{i+1}] {exp['id']} ({exp['module']}.{exp['func']})")
        return

    # 创建套件输出目录
    suite_dir = OUTPUT_ROOT / "experiments" / args.suite
    suite_dir.mkdir(parents=True, exist_ok=True)

    results = []
    t_start = time.perf_counter()

    for i, exp_def in enumerate(exp_list):
        print(f"\n[{i+1}/{len(exp_list)}] {exp_def['id']} ...", end=" ", flush=True)
        result = run_single_experiment(exp_def, suite_dir)
        results.append(result)
        print(f"{result.status} ({result.elapsed_s:.0f}s)")
        if result.error_msg:
            print(f"  Error: {result.error_msg[:200]}")

    total_s = time.perf_counter() - t_start

    # 生成报告
    print(f"\n{'=' * 60}")
    print(f"Generating report...")
    report_text = generate_report(args.suite, suite["description"], results, total_s, OUTPUT_ROOT)

    # 打印摘要
    passed = sum(1 for r in results if r.status == "PASS")
    failed = sum(1 for r in results if r.status == "FAIL")
    print(f"\n{'=' * 60}")
    print(f"COMPLETE: {passed} PASS / {failed} FAIL / {len(results)} total")
    print(f"Total time: {total_s:.0f}s ({total_s/60:.1f} min)")
    print(f"Report: {REPORT_DIR}")

    # 列出报告文件
    reports = sorted(REPORT_DIR.glob("*_report.md"))
    if reports:
        print(f"\nRecent reports:")
        for r in reports[-5:]:
            print(f"  {r.name}  ({r.stat().st_size} bytes)")

    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
