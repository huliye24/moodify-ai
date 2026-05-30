"""批量 AI 评测 — 驱动数据飞轮

对音乐资产目录执行全量评测：
- 穷举所有情绪目标
- 三评委分别评分
- 自动写入 CalibrationState（触发 D 值更新）

用法:
    moodify evaluate-run --assets "path/to/assets" --output-dir outputs
    moodify evaluate-status  # 查看当前 D 值和统计
"""

from __future__ import annotations

import json
import logging
import time
from dataclasses import dataclass
from pathlib import Path
from datetime import datetime

import numpy as np

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════════
#  RunConfig
# ═══════════════════════════════════════════════════════════════

@dataclass
class RunConfig:
    """一次批量评测的配置."""
    assets_dir: str          # 音乐资产目录
    output_dir: str         # 输出目录
    emotions: list[str]      # 要评测的情绪列表
    top_k: int              # 每个情绪取 top_k 个处理版本
    dry_run: bool           # True=只打印计划，不执行
    force: bool             # True=重新评测已有记录
    min_d_advance: float    # 期望的 D 值最低增幅

    @classmethod
    def from_args(cls, args) -> "RunConfig":
        emotions = getattr(args, "emotions", "").split(",") if getattr(args, "emotions", None) else [
            "GA", "SE", "UD", "LW", "HL", "DR", "WL", "CN"
        ]
        return cls(
            assets_dir=str(args.assets_dir),
            output_dir=str(getattr(args, "output_dir", "outputs")),
            emotions=emotions,
            top_k=int(getattr(args, "top_k", 3)),
            dry_run=bool(getattr(args, "dry_run", False)),
            force=bool(getattr(args, "force", False)),
            min_d_advance=float(getattr(args, "min_d_advance", 0.05)),
        )


# ═══════════════════════════════════════════════════════════════
#  BatchRunner
# ═══════════════════════════════════════════════════════════════

@dataclass
class EvaluationRunResult:
    """一次批量运行的结果."""
    run_id: str
    started_at: str
    finished_at: str | None
    total_tracks: int
    total_evaluations: int
    completed: int
    failed: int
    d_before: float
    d_after: float
    delta_d: float
    results: list[dict]


class BatchEvaluator:
    """批量 AI 评测器 — 对资产目录穷举情绪处理 + AI 评测 + 反馈写入."""

    def __init__(self, config: RunConfig):
        self.config = config
        self.results: list[dict] = []

    def discover_assets(self) -> list[Path]:
        """发现目录下所有音频文件."""
        extensions = {".wav", ".mp3", ".flac", ".aiff", ".aif", ".m4a", ".ogg"}
        assets_dir = Path(self.config.assets_dir)
        if not assets_dir.exists():
            return []

        audio_files = []
        # 递归扫描
        for ext in extensions:
            audio_files.extend(assets_dir.rglob(f"*{ext}"))
            audio_files.extend(assets_dir.rglob(f"*{ext.upper()}"))

        # 过滤掉明显是处理输出的文件（包含关键词）
        filtered = []
        for f in audio_files:
            name_lower = f.stem.lower()
            skip_keywords = ["wavefield", "enrichment", "processed", "output", "_v1", "_v2", "_v3"]
            if not any(kw in name_lower for kw in skip_keywords):
                filtered.append(f)

        return sorted(set(filtered))

    def run(self) -> EvaluationRunResult:
        """执行批量评测."""
        run_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        started_at = datetime.now().isoformat()

        # 读取 D 值
        d_before = self._load_d_value()
        logger.info(f"[{run_id}] Starting batch evaluation. D_before={d_before:.3f}")

        assets = self.discover_assets()
        logger.info(f"Discovered {len(assets)} audio assets")

        if self.config.dry_run:
            self._print_plan(assets)
            return EvaluationRunResult(
                run_id=run_id, started_at=started_at, finished_at=None,
                total_tracks=len(assets),
                total_evaluations=len(assets) * len(self.config.emotions) * self.config.top_k,
                completed=0, failed=0,
                d_before=d_before, d_after=d_before, delta_d=0.0,
                results=[],
            )

        completed = 0
        failed = 0
        t_start = time.perf_counter()

        for asset_path in assets:
            for emotion in self.config.emotions:
                try:
                    result = self._evaluate_single(asset_path, emotion)
                    if result:
                        self.results.append(result)
                        completed += 1
                    else:
                        failed += 1
                except Exception as e:
                    logger.warning(f"Failed: {asset_path.name} × {emotion}: {e}")
                    failed += 1

            # 每首歌后打印进度
            logger.info(
                f"[{asset_path.name}] {emotion} done "
                f"({completed}/{len(assets) * len(self.config.emotions)})"
            )

        d_after = self._load_d_value()
        elapsed = time.perf_counter() - t_start

        logger.info(
            f"[{run_id}] Batch complete: {completed} ok, {failed} failed, "
            f"D: {d_before:.3f} → {d_after:.3f} ({d_after-d_before:+.3f}), "
            f"{elapsed:.0f}s"
        )

        return EvaluationRunResult(
            run_id=run_id,
            started_at=started_at,
            finished_at=datetime.now().isoformat(),
            total_tracks=len(assets),
            total_evaluations=len(assets) * len(self.config.emotions),
            completed=completed,
            failed=failed,
            d_before=d_before,
            d_after=d_after,
            delta_d=d_after - d_before,
            results=self.results,
        )

    def _evaluate_single(self, audio_path: Path, emotion: str) -> dict | None:
        """对单首曲子执行完整评测流程."""
        from moodify.orchestration.workflow_engine import WorkflowOrchestrator
        from moodify.evaluation.judges import EvaluatorOrchestrator
        from moodify.knowledge.emotion_targets import EMOTION_TARGETS_V2, KEY_TO_CODE

        # 解析情绪
        emotion_code = KEY_TO_CODE.get(emotion, emotion)
        emotion_info = EMOTION_TARGETS_V2.get(emotion_code, EMOTION_TARGETS_V2.get("GA", {}))
        emotion_name = emotion_info.get("name_cn", emotion_code)
        emotion_desc = emotion_info.get("primary", "")

        # 运行处理管道
        orch = WorkflowOrchestrator()
        result = orch.process(
            input_path=str(audio_path),
            emotion_target=emotion,
            platform="spotify",
            output_dir=self.config.output_dir,
        )

        if not result.success or not result.output_path:
            logger.warning(f"Process failed: {audio_path.name} × {emotion}")
            return None

        # 诊断原始和处理后的音频
        from moodify.diagnosis.engine import DiagnosisEngine
        engine = DiagnosisEngine()

        ws_before = engine.diagnose_quick(str(audio_path))
        ws_after = engine.diagnose_quick(result.output_path)

        # 提取 5D 向量
        from moodify.orchestration.state_transfer import StateTransferEngine
        ws_raw_proc = StateTransferEngine.diagnostic_to_process(ws_before)
        ws_proc_proc = StateTransferEngine.diagnostic_to_process(ws_after)
        ws_before_5d = ws_raw_proc.to_array()
        ws_after_5d = ws_proc_proc.to_array()

        # 运行 AI 评测
        evaluator = EvaluatorOrchestrator()
        assessment = evaluator.evaluate(
            raw_audio_path=str(audio_path),
            processed_audio_path=result.output_path,
            raw_ws=ws_before.to_dict(),
            processed_ws=ws_after.to_dict(),
            emotion_code=emotion_code,
            emotion_name=emotion_name,
            emotion_desc=emotion_desc,
            params_applied=result.best_params or {},
            proxy_score=max(result.scores[0] if result.scores else 0, 0),
            strength_vector=result.best_strength or {},
            ws_before_5d=ws_before_5d,
            ws_after_5d=ws_after_5d,
            storage_dir=self.config.output_dir,
        )

        return {
            "run_id": datetime.now().isoformat(),
            "asset": str(audio_path),
            "emotion": emotion,
            "emotion_code": emotion_code,
            "output_path": result.output_path,
            "proxy_score": assessment.proxy_score,
            "real_eds_equivalent": assessment.real_eds_equivalent,
            "final_score": assessment.final_score,
            "consensus_confidence": assessment.consensus_confidence,
            "judge_a": assessment.judge_a_score,
            "judge_b": assessment.judge_b_score,
            "judge_c": assessment.judge_c_score,
            "whs_before": result.whs_before,
            "whs_after": result.whs_after,
            "eds": result.eds,
        }

    def _load_d_value(self) -> float:
        try:
            from moodify.calibration.online import CalibrationState
            state = CalibrationState.load(self.config.output_dir)
            return state.d_value()
        except Exception:
            return 0.05

    def _print_plan(self, assets: list[Path]) -> None:
        print(f"\n=== Batch Evaluation Plan ===")
        print(f"  Assets dir: {self.config.assets_dir}")
        print(f"  Tracks: {len(assets)}")
        print(f"  Emotions: {self.config.emotions}")
        print(f"  Total evaluations: {len(assets) * len(self.config.emotions)}")
        print(f"  Output dir: {self.config.output_dir}\n")

        for asset in assets:
            print(f"  - {asset.name}")
            for emotion in self.config.emotions:
                print(f"      └─ {emotion}")


# ═══════════════════════════════════════════════════════════════
#  CLI 命令
# ═══════════════════════════════════════════════════════════════

def cmd_evaluate_run(args) -> int:
    """批量 AI 评测命令."""
    from moodify.calibration.online import CalibrationState
    from moodify.evaluation.batch import BatchEvaluator, RunConfig

    config = RunConfig.from_args(args)

    # 显示 D 值前
    try:
        state = CalibrationState.load(config.output_dir)
        print(f"D before: {state.d_value():.3f} (n={state.total_n})")
    except Exception:
        print("D before: 0.050 (no calibration data)")

    print(f"\nRunning batch evaluation...")
    print(f"  Assets: {config.assets_dir}")
    print(f"  Emotions: {config.emotions}")
    print(f"  Dry run: {config.dry_run}\n")

    evaluator = BatchEvaluator(config)
    run_result = evaluator.run()

    # 结果报告
    print(f"\n=== Batch Run Report ===")
    print(f"  Run ID: {run_result.run_id}")
    print(f"  Completed: {run_result.completed}/{run_result.total_evaluations}")
    print(f"  Failed: {run_result.failed}")
    print(f"  D: {run_result.d_before:.3f} → {run_result.d_after:.3f} ({run_result.delta_d:+.3f})")

    if run_result.results:
        avg_score = np.mean([r["final_score"] for r in run_result.results])
        avg_proxy_error = np.mean([abs(r["proxy_score"] - r["real_eds_equivalent"]) for r in run_result.results])
        print(f"  Avg AI score: {avg_score:.1f}")
        print(f"  Avg proxy error: {avg_proxy_error:.1f}")

    # 保存评测报告
    report_path = Path(config.output_dir) / f"evaluation_report_{run_result.run_id}.json"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump({
            "run_id": run_result.run_id,
            "started_at": run_result.started_at,
            "finished_at": run_result.finished_at,
            "d_before": run_result.d_before,
            "d_after": run_result.d_after,
            "delta_d": run_result.delta_d,
            "completed": run_result.completed,
            "failed": run_result.failed,
            "results": run_result.results,
        }, f, ensure_ascii=False, indent=2, default=str)
    print(f"\n  Report: {report_path}")

    return 0 if run_result.failed == 0 else 1


def cmd_evaluate_status(args) -> int:
    """查看评测状态和 D 值."""
    from moodify.calibration.online import CalibrationState

    storage_dir = str(getattr(args, "output_dir", "outputs"))

    print(f"\n=== Moodify AI Evaluation Status ===")
    print(f"  Storage: {storage_dir}\n")

    try:
        state = CalibrationState.load(storage_dir)
        summary = state.summary()

        print(f"  D value: {summary['estimated_D']:.3f} (target: 0.40)")
        print(f"  Total processed: {summary['total_processed']}")
        print(f"  Target: D=0.15 at n≈50, D=0.30 at n≈200\n")

        print(f"  Per-emotion breakdown:")
        print(f"  {'Code':6s} {'n':6s} {'bias':8s} {'confidence':11s} {'rho':8s}")
        print(f"  {'-'*6} {'-'*6} {'-'*8} {'-'*11} {'-'*8}")
        for code, info in summary["emotions"].items():
            rho_str = f"{info['rho']:.3f}" if info["rho"] is not None else "N/A"
            print(f"  {code:6s} {info['n']:6d} {info['mu_bias']:+8.2f} {info['confidence']:11.2f} {rho_str:>8s}")

        # D 值进度条 (ASCII 友好)
        d = summary["estimated_D"]
        bar_len = 30
        filled = int(bar_len * d / 0.40)
        bar = "#" * filled + "-" * (bar_len - filled)
        print(f"\n  D: [{bar}] {d:.3f} / 0.40")

    except Exception as e:
        print(f"  Error loading calibration state: {e}")
        print(f"  D: 0.050 (initial)")

    return 0


def cmd_evaluate_single(args) -> int:
    """对单个音频文件运行 AI 评测."""
    from moodify.calibration.online import CalibrationState
    from moodify.evaluation.judges import EvaluatorOrchestrator
    from moodify.diagnosis.engine import DiagnosisEngine
    from moodify.orchestration.workflow_engine import WorkflowOrchestrator
    from moodify.orchestration.state_transfer import StateTransferEngine
    from moodify.knowledge.emotion_targets import EMOTION_TARGETS_V2, KEY_TO_CODE

    audio_path = args.audio_path
    emotion = args.emotion
    storage_dir = str(getattr(args, "output_dir", "outputs"))

    if not Path(audio_path).exists():
        print(f"ERROR: File not found: {audio_path}")
        return 1

    print(f"\n=== AI Evaluation: {Path(audio_path).name} × {emotion} ===")

    # D 值前
    try:
        state_before = CalibrationState.load(storage_dir)
        d_before = state_before.d_value()
    except Exception:
        d_before = 0.05

    # 处理
    print(f"  Processing...")
    orch = WorkflowOrchestrator()
    result = orch.process(audio_path, emotion, output_dir=storage_dir)

    if not result.success:
        print(f"  FAILED: {result}")
        return 1

    # 诊断
    print(f"  Diagnosing...")
    engine = DiagnosisEngine()
    ws_before = engine.diagnose_quick(audio_path)
    ws_after = engine.diagnose_quick(result.output_path)

    ws_raw_proc = StateTransferEngine.diagnostic_to_process(ws_before)
    ws_proc_proc = StateTransferEngine.diagnostic_to_process(ws_after)
    ws_before_5d = ws_raw_proc.to_array()
    ws_after_5d = ws_proc_proc.to_array()

    # 情绪信息
    emotion_code = KEY_TO_CODE.get(emotion, emotion)
    emotion_info = EMOTION_TARGETS_V2.get(emotion_code, EMOTION_TARGETS_V2.get("GA", {}))
    emotion_name = emotion_info.get("name_cn", emotion_code)
    emotion_desc = emotion_info.get("primary", "")

    # AI 评测
    print(f"  AI evaluating (3 judges)...")
    evaluator = EvaluatorOrchestrator()
    assessment = evaluator.evaluate(
        raw_audio_path=audio_path,
        processed_audio_path=result.output_path,
        raw_ws=ws_before.to_dict(),
        processed_ws=ws_after.to_dict(),
        emotion_code=emotion_code,
        emotion_name=emotion_name,
        emotion_desc=emotion_desc,
        params_applied=result.best_params or {},
        proxy_score=max(result.scores[0] if result.scores else 0, 0),
        strength_vector=result.best_strength or {},
        ws_before_5d=ws_before_5d,
        ws_after_5d=ws_after_5d,
        storage_dir=storage_dir,
    )

    # D 值后
    try:
        state_after = CalibrationState.load(storage_dir)
        d_after = state_after.d_value()
    except Exception:
        d_after = d_before

    # 打印结果
    print(f"\n  === AI Assessment Result ===")
    print(f"  Final Score:    {assessment.final_score:.1f} / 100")
    print(f"  Confidence:      {assessment.consensus_confidence:.1%}")
    print(f"  Consensus Std:   {assessment.consensus_std:.2f}")
    print(f"  Proxy Score:     {assessment.proxy_score:.1f}")
    print(f"  Real EDS Equiv:  {assessment.real_eds_equivalent:.1f}")
    print(f"  Proxy Error:     {abs(assessment.proxy_score - assessment.real_eds_equivalent):.1f}")

    print(f"\n  === Judge Breakdown ===")
    for j in assessment.judges:
        print(f"  {j.name:18s} overall={j.overall:5.1f}  emotion={j.emotion_score:5.1f}  quality={j.quality_score:5.1f}  conf={j.confidence:.0%}")

    print(f"\n  === Calibration ===")
    print(f"  D: {d_before:.3f} → {d_after:.3f} ({d_after-d_before:+.3f})")

    if d_after - d_before > 0.001:
        bar_len = 30
        filled = int(bar_len * d_after / 0.40)
        bar = "█" * filled + "░" * (bar_len - filled)
        print(f"      [{bar}] {d_after:.3f} / 0.40")

    return 0
