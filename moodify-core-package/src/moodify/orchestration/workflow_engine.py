"""
workflow_engine.py — 六阶段工作流编排器 (SPEC §10)
=====================================================
Phase 0: 情绪解析 -> Phase 1: 诊断 -> Phase 1.5: 参数选择
-> Phase 2: 音频加载 -> Phase 3: 频谱增强 (HPSS)
-> Phase 4: 空间重构 -> Phase 5: 再合成 -> Phase 6: 情绪显影 + 母带

技术路线: Phase 3 使用 HPSS 频谱分解替代 Demucs 深度学习源分离。
HPSS 基于 FFT 中值滤波, <1s 完成, 无 DL 伪影, 更适合 AI 音乐特性。
"""

import os
import time
import uuid
import logging
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass, field
from enum import Enum

import numpy as np
import soundfile

logger = logging.getLogger(__name__)


class PhaseStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass
class PhaseResult:
    phase: int
    name: str
    status: PhaseStatus
    output: dict = field(default_factory=dict)
    warnings: list[str] = field(default_factory=list)
    elapsed_ms: float = 0.0
    gate_passed: bool = True


@dataclass
class WorkflowResult:
    """六阶段工作流完整结果"""
    phases: list[PhaseResult]
    input_path: str
    output_path: str
    emotion_target: str
    wave_state_before: dict
    wave_state_after: dict
    delta: dict
    whs_before: float
    whs_after: float
    eds: float
    total_risk: float
    risk_level: str
    total_elapsed_ms: float
    success: bool
    process_id: str = ""
    # 扩展字段 (SPEC-013: AI 评测管道)
    scores: list[float] = field(default_factory=list)       # proxy scores per candidate
    candidates: list[dict] = field(default_factory=list)    # 15-DSP param dicts
    strengths: list[dict] = field(default_factory=list)     # 5-D strength vectors
    best_params: dict = field(default_factory=dict)          # 实际使用的 15 DSP params
    best_strength: dict = field(default_factory=dict)       # 实际使用的 5D strength


@dataclass
class PipelineContext:
    """流水线上下文 — 消除 process() 中的散落局部变量。

    每个字段由对应的流水线阶段填充。
    process() 只做编排, 不持有中间状态。
    """
    input_path: str
    emotion_target: str
    platform: str
    output_dir: str

    # Phase 0 填充
    emotion_parsed: dict = field(default_factory=dict)
    # Phase 1 填充
    diagnosis = None
    defects: list = field(default_factory=list)
    whs_before: float = 0.0
    # Phase 1.5 填充
    candidates: list = field(default_factory=list)   # list[dict] 15-param dicts
    strengths: list = field(default_factory=list)    # list[dict] 5D strength vectors
    scores: list = field(default_factory=list)       # list[float] proxy scores
    # Phase 2 填充
    audio: np.ndarray | None = None
    sr: int = 44100
    # Phase 3-6 填充
    best_idx: int = 0
    best_output: str = ""
    best_eds: float = -999.0
    best_whs: float = 0.0
    best_params: dict = field(default_factory=dict)
    best_strength: dict = field(default_factory=dict)
    # 后处理填充
    narrative: dict | None = None
    phases: list = field(default_factory=list)
    process_id: str = ""
    total_start: float = 0.0


class WorkflowOrchestrator:
    """六阶段处理流水线编排器 (§10.1)

    process() 是薄壳编排器 — 编排 6 个独立阶段, 每个阶段是私有方法。
    状态通过 PipelineContext 传递, 阶段间无隐式依赖。
    """

    def __init__(self):
        self._diagnosis_engine = None
        self._defect_classifier = None
        self._health_scorer = None
        self._craft_matcher = None
        self._risk_model = None
        self._state_engine = None
        self._output_dir = "outputs"

    # ═══════════════════════════════════════════════════════════
    #  process() — 薄壳编排器
    # ═══════════════════════════════════════════════════════════

    def process(self,
                input_path: str,
                emotion_target: str,
                platform: str = "spotify",
                mode: str = "auto",
                craft_card_id: str | None = None,
                output_dir: str = "outputs") -> WorkflowResult:
        """完整处理流水线。

        编排顺序:
          Phase 0: 情绪解析    → ctx.emotion_parsed
          Phase 1: 诊断        → ctx.diagnosis, ctx.defects, ctx.whs_before
          Phase 1.5: 参数选择  → ctx.candidates, ctx.strengths, ctx.scores
          Phase 2: 音频加载    → ctx.audio, ctx.sr
          Phase 3-6: 多版本处理 → ctx.best_*
          后处理: 诊断解读 + 历史记录
        """
        ctx = PipelineContext(
            input_path=input_path, emotion_target=emotion_target,
            platform=platform, output_dir=output_dir,
        )
        ctx.process_id = f"Px-{datetime.now().strftime('%Y%m%d-%H%M%S')}-{uuid.uuid4().hex[:4]}"
        ctx.total_start = time.perf_counter()
        self._output_dir = output_dir

        try:
            self._resolve_emotion(ctx)
            self._diagnose(ctx)
            self._select_parameters(ctx)
            self._load_audio(ctx)
            self._process_candidates(ctx)
            self._finalize(ctx)
            return self._build_result(ctx)
        except Exception:
            import traceback
            traceback.print_exc()
            return WorkflowResult(
                phases=ctx.phases, input_path=input_path,
                output_path=ctx.best_output, emotion_target=emotion_target,
                wave_state_before={}, wave_state_after={}, delta={},
                whs_before=0, whs_after=0, eds=0,
                total_risk=0, risk_level="error",
                total_elapsed_ms=(time.perf_counter() - ctx.total_start) * 1000,
                success=False, process_id=ctx.process_id,
            )

    # ═══════════════════════════════════════════════════════════
    #  Pipeline stages — 每个阶段是独立的私有方法
    # ═══════════════════════════════════════════════════════════

    def _resolve_emotion(self, ctx: PipelineContext) -> None:
        """Phase 0: NL 情绪文本 → 结构化情绪目标。"""
        try:
            from moodify.knowledge.emotion_targets import resolve_emotion_from_nl
            ctx.emotion_parsed = resolve_emotion_from_nl(ctx.emotion_target)
        except Exception:
            logger.debug(f"[resolve_emotion] NL resolution failed for '{ctx.emotion_target}', using fallback")

        if not ctx.emotion_parsed:
            ctx.emotion_parsed = {
                "emotion_key": "gentle_awakening",
                "emotion_code": "GA",
                "intensity": 0.6,
                "vector_bias": {"E": 0.0, "D": 0.0, "S": 0.0, "T": 0.0, "H": 0.0},
                "source": "fallback",
            }

    def _diagnose(self, ctx: PipelineContext) -> None:
        """Phase 1: 音频诊断 + 缺陷分类。"""
        phase1 = self._run_diagnosis(ctx.input_path, ctx.emotion_parsed["emotion_key"])
        ctx.phases.append(phase1)
        ctx.diagnosis = phase1.output.get("wave_state_diagnosis")
        ctx.defects = phase1.output.get("defects", [])
        ctx.whs_before = phase1.output.get("whs", 0)

    def _select_parameters(self, ctx: PipelineContext) -> None:
        """Phase 1.5: 参数选择 — RAG 优先, 5D 搜索回退, 工艺卡保底。

        结果写入 ctx.candidates / ctx.strengths / ctx.scores。
        """
        # ── 尝试 RAG ──
        rag_params, rag_strength, rag_confidence = self._try_rag(ctx)

        if rag_params is not None and rag_confidence > 0.7:
            ctx.candidates = [rag_params]
            ctx.strengths = [rag_strength]
            ctx.scores = [rag_confidence * 100.0]
            phase1_5 = PhaseResult(
                phase=1.5, name="参数推荐(RAG)",
                status=PhaseStatus.COMPLETED,
                output={
                    "top_params_list": ctx.candidates,
                    "top_strengths": ctx.strengths,
                    "top_scores": ctx.scores,
                    "source": "rag_llm",
                },
                elapsed_ms=0,
            )
        else:
            phase1_5 = self._run_strength_search(
                ctx.diagnosis, ctx.emotion_target,
                defects=ctx.defects,
                vector_bias=ctx.emotion_parsed.get("vector_bias"),
                audio=ctx.audio, sr=ctx.sr,
            )
            ctx.candidates = phase1_5.output.get("top_params_list", [])
            ctx.strengths = phase1_5.output.get("top_strengths", [])
            ctx.scores = phase1_5.output.get("top_scores", [])

            # ── 搜索失败 → 工艺卡保底 ──
            if not ctx.candidates:
                from moodify.knowledge.craft_chains import get_recommended_params
                from moodify.knowledge.emotion_targets import resolve_emotion, KEY_TO_CODE
                try:
                    code = resolve_emotion(ctx.emotion_target)
                    code = KEY_TO_CODE.get(code, "GA")
                except Exception:
                    code = "GA"
                ctx.candidates = [get_recommended_params(code)]
                ctx.strengths = [{"spectrum": 0.5, "dynamic": 0.5, "space": 0.5,
                                  "layer": 0.5, "master": 0.5}]
                ctx.scores = [0.0]

        # ── 安全投影 (SPEC-008): DP before DSP ──
        self._apply_safety_projection(ctx, phase1_5)

        ctx.phases.append(phase1_5)

    def _apply_safety_projection(self, ctx: PipelineContext,
                                  phase1_5: PhaseResult) -> None:
        """对每个候选参数运行四级安全投影, 结果写回 ctx.candidates.

        任何 LLM/RAG/搜索来源的推荐参数在进入 DSP 前必须通过此出口。
        """
        if not ctx.candidates:
            return
        emotion_code = ctx.emotion_parsed.get("emotion_code", "GA")

        try:
            from moodify.safety.projection import project
        except ImportError:
            return

        safe_list = []
        for params in ctx.candidates:
            safe_p, proj_log = project(params, emotion_code)
            safe_list.append(safe_p)
            for entry in proj_log:
                phase1_5.warnings.append(f"[safety] {entry}")

        ctx.candidates = safe_list

    def _try_rag(self, ctx: PipelineContext) -> tuple:
        """尝试 RAG 检索 + LLM 参数推荐。

        Returns:
            (rag_params, rag_strength, rag_confidence)
            任一步失败返回 (None, None, 0.0)
        """
        try:
            from moodify.memory.history import ProcessingHistory, diagnosis_to_vector
            from moodify.llm.client import DeepSeekClient

            history = ProcessingHistory(self._output_dir)
            if history.count() == 0:
                return None, None, 0.0

            dvec = diagnosis_to_vector(ctx.diagnosis)
            similar = history.find_similar(dvec, top_k=5)
            top1_sim = similar[0][1] if similar else 0.0

            llm = DeepSeekClient()
            if not llm.available or top1_sim <= 0.5:
                return None, None, 0.0

            from moodify.llm.prompt_assembler import assemble_rag_prompt, format_cases_for_prompt

            defects_list = [{"parameter": d.parameter, "severity": d.severity}
                           for d in ctx.defects]
            cases_formatted = format_cases_for_prompt(similar)
            prompt = assemble_rag_prompt(
                ctx.diagnosis.to_dict(), defects_list,
                ctx.emotion_parsed.get("emotion_name", ctx.emotion_target),
                "", cases_formatted,
            )

            result = llm.recommend_params(prompt)
            if not (result and "parameters" in result and "strength_vector" in result):
                return None, None, 0.0

            rag_params = {p["param_name"]: p["value"] for p in result["parameters"]}
            rag_strength = result["strength_vector"]
            rag_confidence = result.get("confidence", 0.7)

            # ── 边界校验 ──
            self._validate_rag_params(rag_params, rag_strength, ctx.emotion_parsed)
            return rag_params, rag_strength, rag_confidence

        except Exception:
            return None, None, 0.0

    @staticmethod
    def _validate_rag_params(params: dict, strength: dict,
                             emotion_parsed: dict) -> None:
        """Clamp RAG 参数到 craft_chains min/max, 补齐缺失参数。"""
        from moodify.knowledge.craft_chains import (
            CRAFT_CHAINS_15PARAMS, PARAM_KEYS, get_recommended_params
        )
        emotion_code = emotion_parsed.get("emotion_code", "GA")
        chain = CRAFT_CHAINS_15PARAMS.get(emotion_code, {})
        rec = get_recommended_params(emotion_code)

        for pk in PARAM_KEYS:
            if pk not in params:
                params[pk] = rec.get(pk, 0.0)
        for pk in PARAM_KEYS:
            spec = chain.get(pk)
            if spec and pk in params:
                params[pk] = max(spec["min"], min(spec["max"], params[pk]))
        for dim in ["spectrum", "dynamic", "space", "layer", "master"]:
            if dim in strength:
                strength[dim] = max(0.05, min(0.95, strength[dim]))

    def _load_audio(self, ctx: PipelineContext) -> None:
        """Phase 2: 加载音频文件。"""
        phase2 = self._run_load_audio(ctx.input_path)
        ctx.phases.append(phase2)
        ctx.audio = phase2.output.get("audio")
        ctx.sr = phase2.output.get("sr", 44100)

        if ctx.audio is None:
            raise RuntimeError("Failed to load audio in Phase 2")

    def _process_candidates(self, ctx: PipelineContext) -> None:
        """Phase 3-6: 对每个候选参数做 DSP, 测 WHS/EDS, 选最优。

        Phase 3 (HPSS) 对所有候选批量处理。
        Phase 4-6 (空间/再合成/母带) 对每个候选独立处理。
        """
        # Phase 3: HPSS 多版本
        phase3 = self._run_spectral_enhancement_multi(ctx.audio, ctx.sr, ctx.candidates)
        ctx.phases.append(phase3)
        versions = phase3.output.get("versions", [ctx.audio])

        # Phase 4-6: 每版本独立处理 + 测量
        for i, ver_audio in enumerate(versions):
            p4 = self._run_spatial(ver_audio, ctx.sr, ctx.emotion_target, None)
            p6 = self._run_mastering(
                p4.output["audio"], ctx.sr, ctx.input_path,
                ctx.emotion_target, ctx.platform, version_suffix=f"_v{i}",
            )
            ctx.phases.extend([p4, p6])

            # 测量
            ver_output = p6.output.get("output_path", "")
            whs_a, eds_a = 0.0, 0.0
            if ver_output and os.path.exists(ver_output):
                try:
                    ws_a = self._diagnose_audio(ver_output)
                    whs_a = self._compute_whs(ws_a)
                    eds_a = self._compute_eds(
                        ctx.diagnosis, ws_a, ctx.emotion_target,
                        vector_bias=ctx.emotion_parsed.get("vector_bias"),
                    )
                except Exception as e:
                    logger.warning(f"[measurement] re-diagnose failed for version {i}: {e}")

            if eds_a > ctx.best_eds:
                ctx.best_eds = eds_a
                ctx.best_idx = i
                ctx.best_whs = whs_a
                ctx.best_output = ver_output
                if i < len(ctx.candidates):
                    ctx.best_params = ctx.candidates[i]
                if i < len(ctx.strengths):
                    ctx.best_strength = ctx.strengths[i]

    def _finalize(self, ctx: PipelineContext) -> None:
        """后处理: LLM 诊断解读 + 写入处理历史。"""
        # 诊断解读
        try:
            from moodify.llm.client import DeepSeekClient
            llm = DeepSeekClient()
            if llm.available and ctx.diagnosis and ctx.best_output:
                ws_after = self._diagnose_audio(ctx.best_output)
                if ws_after:
                    ctx.narrative = llm.narrate_diagnosis(
                        before_dict=ctx.diagnosis.to_dict(),
                        after_dict=ws_after.to_dict(),
                        params=ctx.best_params,
                        whs_before=ctx.whs_before,
                        whs_after=ctx.best_whs if ctx.best_whs > 0 else ctx.whs_before,
                        eds=ctx.best_eds,
                        emotion_name=ctx.emotion_target,
                    )
        except Exception:
            logger.debug("[narrative] LLM diagnosis narration failed (non-critical)")

        # 历史记录
        try:
            from moodify.memory.history import ProcessingHistory, ProcessingRecord, diagnosis_to_vector
            h = ProcessingHistory(self._output_dir)
            h.save(ProcessingRecord(
                diagnosis_vector=diagnosis_to_vector(ctx.diagnosis),
                params=ctx.best_params if ctx.best_params else (
                    ctx.candidates[0] if ctx.candidates else {}),
                strength_vector=ctx.best_strength if ctx.best_strength else (
                    ctx.strengths[0] if ctx.strengths else {}),
                whs_before=ctx.whs_before,
                whs_after=ctx.best_whs if ctx.best_whs > 0 else ctx.whs_before,
                eds=ctx.best_eds,
                proxy_score=float(ctx.scores[ctx.best_idx])
                if ctx.scores and ctx.best_idx < len(ctx.scores) else 0.0,
                emotion_code=ctx.emotion_parsed.get("emotion_code", "GA"),
                emotion_name=ctx.emotion_parsed.get("emotion_name", ctx.emotion_target),
                user_intent="", satisfied=None, user_feedback="",
                timestamp=datetime.now().isoformat(),
                schema_version=1,
            ))
        except Exception as e:
            logger.warning(f"[history] save failed: {e}")

        # ── 在线校准: 自动对比 proxy vs real, 更新偏差估计 ──
        try:
            from moodify.calibration.online import update_calibration
            from moodify.orchestration.state_transfer import StateTransferEngine

            ws_before_5d = StateTransferEngine.diagnostic_to_process(ctx.diagnosis).to_array()
            ws_after = self._diagnose_audio(ctx.best_output) if ctx.best_output else None
            if ws_after:
                ws_after_5d = StateTransferEngine.diagnostic_to_process(ws_after).to_array()
                update_calibration(
                    emotion_code=ctx.emotion_parsed.get("emotion_code", "GA"),
                    proxy_score=float(ctx.scores[ctx.best_idx])
                    if ctx.scores and ctx.best_idx < len(ctx.scores) else 0.0,
                    real_eds=ctx.best_eds,
                    strength_vector=ctx.best_strength if ctx.best_strength else {},
                    ws_before_5d=ws_before_5d,
                    ws_after_5d=ws_after_5d,
                    storage_dir=self._output_dir,
                )
                logger.debug(f"[calibration] updated for {ctx.emotion_parsed.get('emotion_code', 'GA')}: "
                            f"proxy={ctx.scores[ctx.best_idx] if ctx.scores and ctx.best_idx < len(ctx.scores) else 0:.0f} "
                            f"real_eds={ctx.best_eds:.0f}")
        except Exception as e:
            logger.warning(f"[calibration] update failed: {e}")

    def _build_result(self, ctx: PipelineContext) -> WorkflowResult:
        """构建 WorkflowResult。"""
        ws_after_obj = None
        if ctx.best_output and os.path.exists(ctx.best_output):
            try:
                ws_after_obj = self._diagnose_audio(ctx.best_output)
            except Exception:
                pass  # re-diagnose best_output failed — ws_after_obj stays None

        total_elapsed = (time.perf_counter() - ctx.total_start) * 1000
        success = all(
            p.status in (PhaseStatus.COMPLETED, PhaseStatus.SKIPPED)
            for p in ctx.phases
        )

        return WorkflowResult(
            phases=ctx.phases,
            input_path=ctx.input_path,
            output_path=ctx.best_output,
            emotion_target=ctx.emotion_target,
            wave_state_before=ctx.diagnosis.to_dict() if ctx.diagnosis else {},
            wave_state_after=ws_after_obj.to_dict() if ws_after_obj else {},
            delta=self._compute_delta(ctx.diagnosis, ws_after_obj)
            if ctx.best_output and ws_after_obj else {},
            whs_before=ctx.whs_before,
            whs_after=ctx.best_whs if ctx.best_whs > 0 else ctx.whs_before,
            eds=ctx.best_eds,
            total_risk=0.0,
            risk_level="green",
            total_elapsed_ms=total_elapsed,
            success=success,
            process_id=ctx.process_id,
            # SPEC-013 扩展字段
            scores=list(ctx.scores),
            candidates=list(ctx.candidates),
            strengths=list(ctx.strengths),
            best_params=dict(ctx.best_params),
            best_strength=dict(ctx.best_strength),
        )

    # ═══════════════════════════════════════════════════════════
    #  Phase Implementations (不变)
    # ═══════════════════════════════════════════════════════════

    def _run_diagnosis(self, input_path: str, emotion_target: str) -> PhaseResult:
        """Phase 1: 诊断 + 工艺卡匹配"""
        from moodify.diagnosis.engine import DiagnosisEngine
        from moodify.diagnosis.defect_classifier import DefectClassifier
        from moodify.diagnosis.health_scorer import HealthScorer
        from moodify.diagnosis.quality_gate import QualityGate
        from moodify.knowledge.emotion_targets import resolve_emotion

        t0 = time.perf_counter()
        engine = DiagnosisEngine()
        ws = engine.diagnose_quick(input_path)
        classifier = DefectClassifier()
        defects = classifier.classify(ws, emotion_target)
        scorer = HealthScorer()
        whs_result = scorer.compute_whs(ws, defects)
        elapsed = (time.perf_counter() - t0) * 1000
        gate = QualityGate.gate_1_diagnosis(ws, elapsed)

        best_card = None
        try:
            from moodify.knowledge.craft_chain_match import CraftChainMatch, generate_craft_cards_from_data
            cards = generate_craft_cards_from_data()
            matcher = CraftChainMatch()
            matches = matcher.match(defects, emotion_target, ws, cards, top_k=1)
            best_card = matches[0].craft_card if matches else None
        except Exception:
            pass

        return PhaseResult(
            phase=1, name="诊断",
            status=PhaseStatus.COMPLETED,
            output={
                "wave_state_diagnosis": ws,
                "defects": defects,
                "whs": whs_result["WHS"],
                "craft_card": best_card,
                "emotion_key": resolve_emotion(emotion_target),
            },
            warnings=gate.warnings,
            elapsed_ms=elapsed,
            gate_passed=gate.passed,
        )

    def _run_load_audio(self, input_path: str) -> PhaseResult:
        """Phase 2: 音频加载 (WAV/MP3/FLAC/...)"""
        t0 = time.perf_counter()
        try:
            from moodify.audio_io import load_audio
            audio, sr = load_audio(input_path, always_2d=False)
        except Exception as e:
            return PhaseResult(
                phase=2, name="音频加载",
                status=PhaseStatus.FAILED,
                output={"audio": None, "sr": 44100},
                warnings=[f"Failed to load audio: {e}"],
                elapsed_ms=(time.perf_counter() - t0) * 1000,
                gate_passed=False,
            )

        return PhaseResult(
            phase=2, name="音频加载",
            status=PhaseStatus.COMPLETED,
            output={"audio": audio, "sr": sr},
            elapsed_ms=(time.perf_counter() - t0) * 1000,
        )

    def _run_spectral_enhancement_multi(
        self, audio: np.ndarray, sr: int, params_list: list[dict]
    ) -> PhaseResult:
        """Phase 3: HPSS 频谱增强 — 多版本批量处理"""
        t0 = time.perf_counter()
        from moodify.processing.spectral_chain import SpectralDSPChain
        chain = SpectralDSPChain()
        versions = []
        for params in params_list:
            try:
                ver = chain.process(audio, sr, params)
                versions.append(ver)
            except Exception:
                versions.append(audio)
        return PhaseResult(
            phase=3, name="频谱增强",
            status=PhaseStatus.COMPLETED,
            output={"versions": versions, "count": len(versions)},
            elapsed_ms=(time.perf_counter() - t0) * 1000,
        )

    def _run_spatial(self, audio: np.ndarray, sr: int,
                      emotion_target: str, craft_card=None) -> PhaseResult:
        """Phase 4: 空间重构 — M/S 立体声宽度调节"""
        t0 = time.perf_counter()
        warnings = []

        if audio.ndim < 2 or audio.shape[1] < 2:
            return PhaseResult(
                phase=4, name="空间重构",
                status=PhaseStatus.COMPLETED,
                output={"audio": audio},
                warnings=["Mono audio; spatial processing skipped"],
                elapsed_ms=(time.perf_counter() - t0) * 1000,
            )

        width = 1.0
        if craft_card is not None:
            try:
                params = craft_card.get_recommended_params()
                width = params.get("P12_reverb_width", 1.0)
            except Exception:
                pass
        else:
            try:
                from moodify.knowledge.craft_chains import get_recommended_params
                from moodify.knowledge.emotion_targets import resolve_emotion, KEY_TO_CODE
                resolved_key = resolve_emotion(emotion_target)
                resolved_code = KEY_TO_CODE.get(resolved_key, "GA")
                params = get_recommended_params(resolved_code)
                width = params.get("P12_reverb_width", 1.0)
            except Exception:
                pass

        mid = (audio[:, 0] + audio[:, 1]) / 2.0
        side = (audio[:, 0] - audio[:, 1]) / 2.0
        side_processed = side * width
        result = np.zeros_like(audio)
        result[:, 0] = mid + side_processed
        result[:, 1] = mid - side_processed

        peak = np.max(np.abs(result))
        if peak > 0.98:
            result *= 0.98 / peak

        return PhaseResult(
            phase=4, name="空间重构",
            status=PhaseStatus.COMPLETED,
            output={"audio": result, "width": width},
            warnings=warnings,
            elapsed_ms=(time.perf_counter() - t0) * 1000,
        )


    # ── Phase 6 helpers ───────────────────────────────────

    @staticmethod
    def _normalize_loudness(audio_f32: np.ndarray, sr: int,
                            target_lufs: float) -> tuple[np.ndarray, list[str]]:
        """LUFS loudness normalization. Returns (audio, warnings)."""
        import pyloudnorm as pyln
        meter = pyln.Meter(sr)
        loudness = meter.integrated_loudness(audio_f32)
        if np.isinf(loudness) or np.isnan(loudness):
            return audio_f32, ["Could not measure loudness; skipping normalization"]
        return pyln.normalize.loudness(audio_f32, loudness, target_lufs), []

    @staticmethod
    def _apply_limiter(audio_f32: np.ndarray, sr: int) -> tuple[np.ndarray, float, list[str]]:
        """Peak limiter. Returns (audio, risk_delta, warnings)."""
        import pedalboard
        limiter = pedalboard.Limiter(threshold_db=-1.0, release_ms=50)
        x = audio_f32.T if audio_f32.ndim > 1 else audio_f32.reshape(1, -1)
        y = limiter(x.astype(np.float32), sr)
        result = (y.T if audio_f32.ndim > 1 else y[0]).astype(audio_f32.dtype)
        peak = np.max(np.abs(result))
        if peak > 0.99:
            result *= 0.99 / peak
        risk = 0.2 if np.max(np.abs(result)) > 0.999 else 0.0
        warnings = ["Output near digital ceiling"] if risk > 0 else []
        return result, risk, warnings

    def _export_wav(self, audio_data: np.ndarray, sr: int,
                    input_path: str, emotion_target: str,
                    platform: str, version_suffix: str) -> str:
        """Write WAV and return output path."""
        os.makedirs(self._output_dir, exist_ok=True)
        base = Path(input_path).stem
        emo = emotion_target[:2] if len(emotion_target) >= 2 else emotion_target
        path = os.path.join(self._output_dir, f"{base}_{emo}_{platform}{version_suffix}.wav")
        soundfile.write(path, audio_data, sr, subtype='PCM_16')
        return path

    def _run_mastering(self, audio: np.ndarray, sr: int,
                        input_path: str, emotion_target: str,
                        platform: str = "spotify",
                        version_suffix: str = "") -> PhaseResult:
        """Phase 6: 情绪显影 + 母带 — loudness norm → limiter → export."""
        t0 = time.perf_counter()
        target_lufs = -16.0 if platform == "apple_music" else -14.0
        warnings: list[str] = []
        total_risk = 0.0

        try:
            audio_f32 = audio.astype(np.float32)
            audio_f32, w = self._normalize_loudness(audio_f32, sr, target_lufs)
            warnings += w
            audio_f32, risk_delta, w = self._apply_limiter(audio_f32, sr)
            total_risk += risk_delta
            warnings += w
            output_path = self._export_wav(
                audio_f32, sr, input_path, emotion_target, platform, version_suffix)

            risk_level = "yellow" if total_risk > 0 else "green"
            return PhaseResult(
                phase=6, name="情绪显影+母带", status=PhaseStatus.COMPLETED,
                output={"output_path": output_path, "audio": audio_f32,
                        "total_risk": total_risk, "risk_level": risk_level,
                        "loudness_normalized": True, "target_lufs": target_lufs},
                warnings=warnings, elapsed_ms=(time.perf_counter() - t0) * 1000)
        except Exception as e:
            logger.warning(f"[mastering] failed: {e}, exporting raw audio")
            try:
                output_path = self._export_wav(
                    audio, sr, input_path, emotion_target, platform, version_suffix)
                return PhaseResult(
                    phase=6, name="情绪显影+母带", status=PhaseStatus.COMPLETED,
                    output={"output_path": output_path, "audio": audio,
                            "total_risk": 0.5, "risk_level": "yellow"},
                    warnings=[f"Mastering failed ({e}); exported raw audio"],
                    elapsed_ms=(time.perf_counter() - t0) * 1000)
            except Exception as e2:
                logger.warning(f"[mastering] export also failed: {e2}")
                return PhaseResult(
                    phase=6, name="情绪显影+母带", status=PhaseStatus.FAILED,
                    output={"output_path": "", "total_risk": 1.0, "risk_level": "red"},
                    warnings=[f"Export failed: {e2}"],
                    elapsed_ms=(time.perf_counter() - t0) * 1000, gate_passed=False)

    def _run_strength_search(self, ws_diagnosis, emotion_target: str,
                             defects=None, vector_bias=None,
                             audio=None, sr=44100) -> PhaseResult:
        """Phase 1.5: 5D 强度空间搜索"""
        t0 = time.perf_counter()
        if ws_diagnosis is None:
            return PhaseResult(
                phase=1.5, name="强度搜索", status=PhaseStatus.SKIPPED,
                output={"top_params_list": [], "top_strengths": [], "top_scores": []},
                elapsed_ms=0,
            )
        try:
            from moodify.optimizer.search import search_optimal_strengths
            results = search_optimal_strengths(ws_diagnosis, emotion_target, top_k=3,
                                               defects=defects, vector_bias=vector_bias,
                                               audio=audio, sr=sr)
            return PhaseResult(
                phase=1.5, name="强度搜索",
                status=PhaseStatus.COMPLETED,
                output={
                    "top_strengths": [r[0] for r in results],
                    "top_params_list": [r[1] for r in results],
                    "top_scores": [r[2] for r in results],
                },
                elapsed_ms=(time.perf_counter() - t0) * 1000,
            )
        except Exception as e:
            import traceback
            traceback.print_exc()
            return PhaseResult(
                phase=1.5, name="强度搜索",
                status=PhaseStatus.COMPLETED,
                output={
                    "top_params_list": [],
                    "top_strengths": [],
                    "top_scores": [],
                    "fallback_reason": str(e),
                },
                warnings=[f"Strength search failed, using recommended params: {e}"],
                elapsed_ms=(time.perf_counter() - t0) * 1000,
            )

    # ═══════════════════════════════════════════════════════════
    #  Helpers
    # ═══════════════════════════════════════════════════════════

    def _diagnose_audio(self, path: str):
        from moodify.diagnosis.engine import DiagnosisEngine
        engine = DiagnosisEngine()
        return engine.diagnose_quick(path)

    def _compute_whs(self, ws) -> float:
        if ws is None:
            return 0
        from moodify.diagnosis.defect_classifier import DefectClassifier
        from moodify.diagnosis.health_scorer import HealthScorer
        classifier = DefectClassifier()
        scorer = HealthScorer()
        defects = classifier.classify(ws)
        return scorer.compute_whs(ws, defects)["WHS"]

    def _compute_eds(self, ws_before, ws_after, emotion: str,
                     vector_bias: dict | None = None) -> float:
        if ws_before is None or ws_after is None:
            return 0
        from moodify.diagnosis.health_scorer import HealthScorer
        scorer = HealthScorer()
        target = None
        if vector_bias:
            target = scorer._get_ideal_vector(emotion).copy()
            for i, dim in enumerate(["E", "D", "S", "T", "H"]):
                target[i] += vector_bias.get(dim, 0.0)
            target = np.clip(target, 0.0, 1.0)
        return scorer.compute_eds(ws_before, ws_after, emotion, target_vec=target)

    def _compute_delta(self, ws_before, ws_after) -> dict:
        if ws_before is None or ws_after is None:
            return {}
        from moodify.orchestration.state_transfer import StateTransferEngine
        ws_raw_proc = StateTransferEngine.diagnostic_to_process(ws_before)
        ws_final_proc = StateTransferEngine.diagnostic_to_process(ws_after)
        return StateTransferEngine.compute_delta(ws_raw_proc, ws_final_proc)


def one_click_process(input_path: str,
                      emotion_target: str,
                      output_dir: str = "outputs") -> str:
    """一键处理: 自动诊断 -> 工艺匹配 -> DSP -> 母带 -> 输出"""
    orchestrator = WorkflowOrchestrator()
    result = orchestrator.process(
        input_path=input_path,
        emotion_target=emotion_target,
        platform="spotify",
        mode="auto",
        output_dir=output_dir,
    )
    if result.success:
        print(f"  OK - process_id={result.process_id}")
        print(f"  WHS: {result.whs_before:.0f} -> {result.whs_after:.0f}")
        print(f"  EDS: {result.eds:.0f}")
        print(f"  Risk: {result.total_risk:.2f} [{result.risk_level}]")
    else:
        print("  FAILED")
    return result.output_path
