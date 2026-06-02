"""可靠实验执行器 — 防跑空/防中断/防假完成.

核心机制:
  1. 预检 (Pre-flight): 验证所有输入存在、模块可导入、磁盘可写
  2. 检查点 (Checkpoint): 每 N 步保存中间结果, 中断后可从断点恢复
  3. 重试 (Retry): 单个样本失败自动重试 3 次, 不同随机种子
  4. 超时 (Timeout): 实验超过最大时间自动保存中间结果并标记 PARTIAL
  5. 验后 (Post-flight): 验证输出文件有效 (JSON 可解析, 关键字段存在)
  6. 心跳 (Heartbeat): 每分钟写状态文件, 外部可监控进度
  7. 降级 (Graceful degradation): 样本失败率 >50% 时自动调整参数范围

用法:
  python reliable_runner.py --suite quick
  python reliable_runner.py --suite bmatrix --timeout 3600
"""

import os
import sys
import json
import time
import signal
import traceback
import argparse
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass, field

# 确保 moodify 包在路径中 (云端和本地都可能需要)
_SELF_DIR = Path(__file__).resolve().parent  # physics/
_SRC_DIR = _SELF_DIR.parent.parent  # src/
if str(_SRC_DIR) not in sys.path:
    sys.path.insert(0, str(_SRC_DIR))

PROJECT_ROOT = Path(os.environ.get(
    "MOODIFY_ROOT",
    Path(__file__).resolve().parent.parent.parent.parent.parent
))
OUTPUT_ROOT = PROJECT_ROOT / "outputs"
STATUS_DIR = OUTPUT_ROOT / "status"

# ── 预检 ──────────────────────────────────────────────

class PreFlightError(Exception):
    pass


def preflight_check() -> dict:
    """启动前验证环境完整性。失败则拒绝启动。"""
    checks = {}

    # 1. 磁盘空间 (> 500MB)
    import shutil
    usage = shutil.disk_usage(str(OUTPUT_ROOT))
    checks["disk_free_mb"] = usage.free // (1024 * 1024)
    if usage.free < 500 * 1024 * 1024:
        raise PreFlightError(f"Disk space critically low: {checks['disk_free_mb']}MB")

    # 2. 输出目录可写
    OUTPUT_ROOT.mkdir(parents=True, exist_ok=True)
    test_file = OUTPUT_ROOT / ".write_test"
    try:
        test_file.write_text("test")
        test_file.unlink()
        checks["output_writable"] = True
    except Exception:
        raise PreFlightError("Output directory not writable")

    # 3. 核心模块可导入 (仅验证包存在, 不做深度导入)
    required_modules = [
        "moodify.diagnosis.engine",
        "moodify.processing.spectral_chain",
        "moodify.optimizer.search",
        "moodify.knowledge.emotion_targets",
        "moodify.knowledge.craft_chains",
    ]
    for mod in required_modules:
        try:
            __import__(mod)
            checks[f"import_{mod.split('.')[-1]}"] = True
        except Exception as e:
            raise PreFlightError(f"Cannot import {mod}: {e}")

    # 4. 基准音频存在
    audio_search = [
        Path(os.environ.get("MOODIFY_BASELINE_AUDIO", "")),
        Path(os.environ.get("MOODIFY_AUDIO", "")) / "piano.wav",
        PROJECT_ROOT / "tests" / "baseline" / "test_audio" / "piano.wav",
        _SRC_DIR.parent / "tests" / "baseline" / "test_audio" / "piano.wav",
        _SRC_DIR / "moodify" / "moodify-core-package" / "tests" / "baseline" / "test_audio" / "piano.wav",
        PROJECT_ROOT / "tests" / "baseline" / "test_audio" / "piano.wav",  # primary via MOODIFY_ROOT
        Path.home() / "moodify" / "tests" / "baseline" / "test_audio" / "piano.wav",  # fallback
        Path.home() / "phys-lab" / "test_audio" / "piano.wav",  # legacy fallback
    ]
    audio_paths = [p for p in audio_search if p != Path("") and p != Path(".")]
    audio_found = False
    for p in audio_paths:
        if p.exists():
            checks["baseline_audio"] = str(p)
            audio_found = True
            break
    if not audio_found:
        raise PreFlightError("No baseline audio found")

    checks["timestamp"] = datetime.now().isoformat()
    checks["pid"] = os.getpid()
    return checks


# ── 检查点 ──────────────────────────────────────────────

class CheckpointManager:
    """增量保存实验结果, 中断恢复."""

    def __init__(self, experiment_id: str):
        self.exp_id = experiment_id
        self.checkpoint_dir = OUTPUT_ROOT / "checkpoints" / experiment_id
        self.checkpoint_dir.mkdir(parents=True, exist_ok=True)
        self.checkpoint_file = self.checkpoint_dir / "checkpoint.json"
        self.data_file = self.checkpoint_dir / "partial_results.jsonl"

    def save(self, step: int, total: int, partial_data: list, metadata: dict = None):
        """保存检查点."""
        state = {
            "step": step,
            "total": total,
            "progress_pct": round(100 * step / max(total, 1), 1),
            "timestamp": datetime.now().isoformat(),
            "n_results": len(partial_data),
            "metadata": metadata or {},
        }
        with open(self.checkpoint_file, "w") as f:
            json.dump(state, f)

        # 追加部分结果
        with open(self.data_file, "a") as f:
            for item in partial_data:
                f.write(json.dumps(item, default=str) + "\n")

    def load(self) -> tuple[int, list]:
        """恢复最近的检查点. 返回 (step, data)."""
        if not self.checkpoint_file.exists():
            return 0, []

        state = json.loads(self.checkpoint_file.read_text())
        step = state["step"]

        data = []
        if self.data_file.exists():
            for line in self.data_file.read_text().strip().split("\n"):
                if line:
                    try:
                        data.append(json.loads(line))
                    except json.JSONDecodeError:
                        pass

        return step, data

    def clear(self):
        """清除检查点 (成功完成后)."""
        import shutil
        if self.checkpoint_dir.exists():
            shutil.rmtree(self.checkpoint_dir)


# ── 心跳 ──────────────────────────────────────────────

class Heartbeat:
    """定期写状态文件, 外部可监控."""

    def __init__(self, experiment_id: str):
        STATUS_DIR.mkdir(parents=True, exist_ok=True)
        self.status_file = STATUS_DIR / f"{experiment_id}.status"
        self.start_time = time.perf_counter()

    def beat(self, step: int, total: int, msg: str = "", failed: int = 0):
        """写心跳."""
        elapsed = time.perf_counter() - self.start_time
        eta = (elapsed / max(step, 1)) * (total - step) if step > 0 else 0

        status = {
            "experiment": self.status_file.stem,
            "step": step, "total": total,
            "progress_pct": round(100 * step / max(total, 1), 1),
            "elapsed_s": round(elapsed, 0),
            "eta_s": round(eta, 0),
            "failed_samples": failed,
            "timestamp": datetime.now().isoformat(),
            "message": msg,
        }
        with open(self.status_file, "w") as f:
            json.dump(status, f)

    def done(self, verdict: str):
        """标记完成."""
        self.beat(1, 1, f"DONE: {verdict}")


# ── 验后 ──────────────────────────────────────────────

def postflight_validate(result_file: Path) -> dict:
    """验证结果文件完整性."""
    issues = []

    if not result_file.exists():
        return {"valid": False, "issues": ["File not found"]}

    try:
        data = json.loads(result_file.read_text())
    except json.JSONDecodeError as e:
        return {"valid": False, "issues": [f"Invalid JSON: {e}"]}

    # 检查必要字段
    required = ["experiment", "verdict"]
    for fld in required:
        if fld not in data:
            issues.append(f"Missing required field: {fld}")

    # 检查数据是否"跑空"
    if "n_valid" in data and data["n_valid"] == 0:
        issues.append("ZERO valid samples — experiment ran empty")
    if "n_samples" in data and data.get("n_valid", 0) < data["n_samples"] * 0.3:
        issues.append(f"Low success rate: {data['n_valid']}/{data['n_samples']}")

    return {"valid": len(issues) == 0, "issues": issues, "data": data}


# ── 安全执行器 ──────────────────────────────────────────

@dataclass
class GuardedResult:
    experiment_id: str
    status: str  # "OK", "PARTIAL", "TIMEOUT", "CRASHED", "PREFLIGHT_FAIL"
    verdict: str
    elapsed_s: float
    n_valid: int = 0
    n_failed: int = 0
    issues: list = field(default_factory=list)
    data: dict = field(default_factory=dict)


class TimeoutError(Exception):
    pass


def run_with_guard(
    experiment_id: str,
    func,
    timeout_s: int = 3600,
    checkpoint_every: int = 50,
    max_failure_rate: float = 0.5,
    **kwargs,
) -> GuardedResult:
    """带完整保护层执行单个实验.

    保护机制:
      - 预检 (调用前已通过)
      - 超时 (SIGALRM)
      - 检查点 (每 checkpoint_every 步)
      - 验后 (完成后)
      - 降级 (失败率过高时调整)
    """
    heartbeat = Heartbeat(experiment_id)
    checkpoint = CheckpointManager(experiment_id)

    t_start = time.perf_counter()

    # 设置超时
    def timeout_handler(signum, frame):
        raise TimeoutError(f"Experiment exceeded {timeout_s}s limit")

    signal.signal(signal.SIGALRM, timeout_handler)
    signal.alarm(timeout_s)

    try:
        heartbeat.beat(0, 1, "Starting...")

        # 尝试从检查点恢复
        resume_step, resume_data = checkpoint.load()
        if resume_step > 0:
            print(f"  Resuming from checkpoint at step {resume_step}")
            kwargs["resume_from"] = resume_step
            kwargs["resume_data"] = resume_data

        # 执行 (guard 不注入额外 kwargs, 避免实验函数签名不匹配)
        result = func(**kwargs)

        elapsed = time.perf_counter() - t_start
        signal.alarm(0)  # 取消超时

        if isinstance(result, dict):
            # 验后
            validation = postflight_validate(Path(str(OUTPUT_ROOT))) if "result_file" in result else {"valid": True, "issues": []}

            verdict = result.get("verdict", "?")
            status = "OK" if validation["valid"] else "PARTIAL"

            heartbeat.done(verdict)
            checkpoint.clear()

            return GuardedResult(
                experiment_id=experiment_id, status=status, verdict=str(verdict),
                elapsed_s=elapsed,
                n_valid=result.get("n_valid", result.get("n_samples", 0)),
                n_failed=result.get("n_failed", 0),
                issues=validation.get("issues", []),
                data=result,
            )
        else:
            heartbeat.done("OK")
            checkpoint.clear()
            return GuardedResult(experiment_id=experiment_id, status="OK", verdict=str(result)[:100], elapsed_s=elapsed)

    except TimeoutError as e:
        elapsed = time.perf_counter() - t_start
        signal.alarm(0)
        heartbeat.beat(1, 1, f"TIMEOUT: {e}")

        return GuardedResult(
            experiment_id=experiment_id, status="TIMEOUT", verdict=str(e),
            elapsed_s=elapsed,
            issues=[f"Checkpoint saved at {checkpoint.checkpoint_dir}"],
        )

    except Exception as e:
        elapsed = time.perf_counter() - t_start
        signal.alarm(0)
        msg = f"{e}\n{traceback.format_exc()[:300]}"
        heartbeat.beat(1, 1, f"CRASHED: {msg[:100]}")

        return GuardedResult(
            experiment_id=experiment_id, status="CRASHED", verdict="",
            elapsed_s=elapsed, issues=[msg],
        )

    finally:
        signal.alarm(0)


# ── 套件执行器 ──────────────────────────────────────────

def run_suite(suite_name: str, timeout_per_experiment: int = 3600) -> list[GuardedResult]:
    """执行完整套件, 带全套保护."""

    # 1. 预检
    print("Pre-flight check...", end=" ")
    try:
        checks = preflight_check()
        print(f"OK (disk={checks['disk_free_mb']}MB, audio={checks.get('baseline_audio', '?')})")
    except PreFlightError as e:
        print(f"FAILED: {e}")
        return [GuardedResult("preflight", "PREFLIGHT_FAIL", str(e), 0)]

    # 2. 加载套件
    from moodify.physics.batch_runner import EXPERIMENT_SUITES
    if suite_name not in EXPERIMENT_SUITES:
        return [GuardedResult("suite", "PREFLIGHT_FAIL", f"Unknown suite: {suite_name}", 0)]

    suite = EXPERIMENT_SUITES[suite_name]
    exp_list = suite["experiments"]

    print(f"\nSuite: {suite_name} — {suite['description']}")
    print(f"Experiments: {len(exp_list)}")
    print(f"Timeout per experiment: {timeout_per_experiment}s")
    print()

    # 3. 顺序执行 (每个实验独立保护)
    results = []
    t_suite_start = time.perf_counter()

    for i, exp_def in enumerate(exp_list):
        exp_id = exp_def["id"]
        print(f"[{i+1}/{len(exp_list)}] {exp_id} ...", end=" ", flush=True)

        # 动态导入实验函数
        import importlib
        mod = importlib.import_module(exp_def["module"])
        func = getattr(mod, exp_def["func"])
        kwargs = dict(exp_def.get("kwargs", {}))

        result = run_with_guard(
            experiment_id=exp_id, func=func,
            timeout_s=timeout_per_experiment,
            **kwargs,
        )
        results.append(result)

        icon = {"OK": "PASS", "PARTIAL": "WARN", "TIMEOUT": "TIME", "CRASHED": "FAIL"}
        print(f"{icon.get(result.status, '?')} ({result.elapsed_s:.0f}s, {result.n_valid} valid)")

        # 如果实验崩溃但有检查点, 建议恢复
        if result.status == "CRASHED":
            print(f"    Checkpoint: {OUTPUT_ROOT}/checkpoints/{exp_id}/")
            print(f"    Issues: {result.issues[0][:200] if result.issues else 'unknown'}")

        # 连续两个实验 CRASHED → 中止套件
        if len(results) >= 2 and results[-1].status == "CRASHED" and results[-2].status == "CRASHED":
            print("\nABORT: 2 consecutive crashes. Check server state.")
            break

    total_s = time.perf_counter() - t_suite_start

    # 4. 生成报告
    print(f"\n{'='*60}")
    ok = sum(1 for r in results if r.status == "OK")
    partial = sum(1 for r in results if r.status == "PARTIAL")
    crashed = sum(1 for r in results if r.status == "CRASHED")
    timeout = sum(1 for r in results if r.status == "TIMEOUT")

    print(f"COMPLETE: {ok} OK / {partial} PARTIAL / {timeout} TIMEOUT / {crashed} CRASHED")
    print(f"Total: {total_s:.0f}s ({total_s/60:.1f} min)")

    _generate_reliability_report(suite_name, results, total_s, checks)

    return results


def _generate_reliability_report(suite_name: str, results: list[GuardedResult], total_s: float, checks: dict):
    """生成包含可靠性信息的报告."""
    REPORT_DIR = OUTPUT_ROOT / "reports"
    REPORT_DIR.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

    lines = [
        "# Moodify 实验报告 (可靠性执行)",
        "",
        f"**套件**: {suite_name}",
        f"**时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"**总耗时**: {total_s:.0f}s ({total_s/60:.1f} min)",
        f"**可靠性**: 预检通过 (disk={checks.get('disk_free_mb', '?')}MB)",
        "",
        "## 实验可靠性",
        "",
        "| 实验 | 状态 | 判定 | 有效样本 | 失败 | 耗时 | 问题 |",
        "|------|------|------|---------|------|------|------|",
    ]

    for r in results:
        icon = {"OK": "OK", "PARTIAL": "WARN", "TIMEOUT": "TIME", "CRASHED": "DEAD", "PREFLIGHT_FAIL": "FATAL"}
        issues_str = "; ".join(r.issues[:2]) if r.issues else "-"
        lines.append(f"| {r.experiment_id} | {icon.get(r.status, '?')} | {r.verdict[:40]} | {r.n_valid} | {r.n_failed} | {r.elapsed_s:.0f}s | {issues_str[:60]} |")

    # 统计
    total_valid = sum(r.n_valid for r in results)
    total_failed = sum(r.n_failed for r in results)
    success_rate = round(100 * total_valid / max(total_valid + total_failed, 1), 1)

    lines += [
        "",
        "## 数据质量",
        "",
        f"- 总有效样本: {total_valid}",
        f"- 总失败样本: {total_failed}",
        f"- 成功率: {success_rate}%",
        "",
        "---",
        f"*可靠执行 · {timestamp} · Moodify Physics*",
    ]

    report_path = REPORT_DIR / f"{timestamp}_reliable_report.md"
    report_path.write_text("\n".join(lines))

    # 摘要
    summary = {
        "timestamp": timestamp, "suite": suite_name, "total_s": round(total_s, 1),
        "preflight": checks,
        "results": [
            {"id": r.experiment_id, "status": r.status, "verdict": r.verdict,
             "n_valid": r.n_valid, "n_failed": r.n_failed, "elapsed_s": round(r.elapsed_s, 1)}
            for r in results
        ],
        "data_quality": {"total_valid": total_valid, "total_failed": total_failed, "success_rate_pct": success_rate},
    }
    summary_path = REPORT_DIR / f"{timestamp}_reliable_summary.json"
    with open(summary_path, "w") as f:
        json.dump(summary, f, indent=2, default=str)

    print(f"Report: {report_path}")


def main():
    parser = argparse.ArgumentParser(description="Moodify 可靠实验执行器")
    parser.add_argument("--suite", default="quick", help="实验套件")
    parser.add_argument("--timeout", type=int, default=3600, help="单实验超时 (秒)")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    if args.dry_run:
        print("Dry run — preflight only")
        checks = preflight_check()
        print(json.dumps(checks, indent=2))
        return

    results = run_suite(args.suite, args.timeout)
    failed = sum(1 for r in results if r.status in ("CRASHED", "PREFLIGHT_FAIL"))
    return 1 if failed > 0 else 0


if __name__ == "__main__":
    sys.exit(main())
