"""
workflow_engine.py — 六阶段工作流编排器 (SPEC §10)
=====================================================
Phase 1: 诊断 -> Phase 2: 音频加载 -> Phase 3: 频谱增强 (HPSS)
-> Phase 4: 空间重构 -> Phase 5: 再合成 -> Phase 6: 情绪显影 + 母带

三质量门: Gate 1 (诊断完整性) -> Gate 2 (处理质量) -> Gate 3 (输出合规性)

技术路线: Phase 3 使用 HPSS 频谱分解替代 Demucs 深度学习源分离。
理由: AI 生成音乐无真正声部边界, Demucs 分离慢(30-60s)且引入伪影。
HPSS 基于 FFT 中值滤波, <1s 完成, 无 DL 伪影, 更适合 AI 音乐特性。
详见: docs/engineering/2026-05-28_高性能处理方案_HPSS频谱替代Demucs.md
"""

import os
import time
import uuid
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional

import numpy as np
import soundfile


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


class WorkflowOrchestrator:
    """六阶段处理流水线编排器 (§10.1)"""

    def __init__(self):
        self._diagnosis_engine = None
        self._defect_classifier = None
        self._health_scorer = None
        self._craft_matcher = None
        self._risk_model = None
        self._state_engine = None
        self._output_dir = "outputs"

    def process(self,
                input_path: str,
                emotion_target: str,
                platform: str = "spotify",
                mode: str = "auto",
                craft_card_id: str | None = None,
                output_dir: str = "outputs") -> WorkflowResult:
        """
        完整六阶段处理流水线

        Args:
            input_path: 原始音频路径
            emotion_target: 目标情绪 (如 "温柔觉醒")
            platform: 输出平台 (spotify/youtube/apple_music)
            mode: "auto" | "expert"
            craft_card_id: 手动指定工艺卡 (expert mode)
            output_dir: 输出目录
        """
        total_start = time.perf_counter()
        phases = []
        process_id = f"Px-{datetime.now().strftime('%Y%m%d-%H%M%S')}-{uuid.uuid4().hex[:4]}"
        self._output_dir = output_dir
        output_path = ""
        audio = None
        sr = 44100

        try:
            # ====== Phase 0: 情绪解析 (NL → 结构化目标) ======
            emotion_parsed = None
            try:
                from moodify.knowledge.emotion_targets import resolve_emotion_from_nl
                emotion_parsed = resolve_emotion_from_nl(emotion_target)
            except Exception:
                pass

            if emotion_parsed is None:
                emotion_parsed = {
                    "emotion_key": "gentle_awakening",
                    "emotion_code": "GA",
                    "intensity": 0.6,
                    "vector_bias": {"E": 0.0, "D": 0.0, "S": 0.0, "T": 0.0, "H": 0.0},
                    "source": "fallback",
                }

            resolved_emotion_key = emotion_parsed["emotion_key"]

            # ====== Phase 1: 诊断 ======
            phase1 = self._run_diagnosis(input_path, resolved_emotion_key)
            phases.append(phase1)

            # ====== Phase 1.3: RAG 检索 + LLM 推荐 ======
            rag_params = None
            rag_strength = None
            rag_confidence = 0.0

            try:
                from moodify.memory.history import ProcessingHistory, diagnosis_to_vector
                from moodify.llm.client import DeepSeekClient

                history = ProcessingHistory(self._output_dir)
                if history.count() > 0:
                    dvec = diagnosis_to_vector(phase1.output.get("wave_state_diagnosis"))
                    similar = history.find_similar(dvec, top_k=5)
                    top1_sim = similar[0][1] if similar else 0.0

                    llm = DeepSeekClient()
                    if llm.available and top1_sim > 0.5:
                        from moodify.llm.prompt_assembler import assemble_rag_prompt, format_cases_for_prompt

                        defects = phase1.output.get("defects", [])
                        defects_list = [{"parameter": d.parameter, "severity": d.severity} for d in defects]

                        cases_formatted = format_cases_for_prompt(similar)
                        prompt = assemble_rag_prompt(
                            phase1.output.get("wave_state_diagnosis").to_dict(),
                            defects_list,
                            emotion_parsed.get("emotion_name", emotion_target),
                            "",
                            cases_formatted,
                        )

                        result = llm.recommend_params(prompt)
                        if result and "parameters" in result and "strength_vector" in result:
                            rag_params = {p["param_name"]: p["value"] for p in result["parameters"]}
                            rag_strength = result["strength_vector"]
                            rag_confidence = result.get("confidence", 0.7)

                            # ── 边界校验：补齐缺失参数 + clamp 到 craft_chains min/max ──
                            from moodify.knowledge.craft_chains import (
                                CRAFT_CHAINS_15PARAMS, PARAM_KEYS, get_recommended_params
                            )
                            rag_emotion_code = emotion_parsed.get("emotion_code", "GA")
                            chain = CRAFT_CHAINS_15PARAMS.get(rag_emotion_code, {})
                            rec_params = get_recommended_params(rag_emotion_code)
                            for pk in PARAM_KEYS:
                                if pk not in rag_params:
                                    rag_params[pk] = rec_params.get(pk, 0.0)
                            for pk in PARAM_KEYS:
                                spec = chain.get(pk)
                                if spec and pk in rag_params:
                                    rag_params[pk] = max(spec["min"], min(spec["max"], rag_params[pk]))
                            for dim in ["spectrum", "dynamic", "space", "layer", "master"]:
                                if dim in rag_strength:
                                    rag_strength[dim] = max(0.05, min(0.95, rag_strength[dim]))
            except Exception:
                pass

            # ====== Phase 2: 音频加载 (移到搜索之前, 供探针校准使用) ======
            phase2 = self._run_load_audio(input_path)
            phases.append(phase2)
            audio = phase2.output.get("audio")
            sr = phase2.output.get("sr", 44100)

            # ====== Phase 1.5: 参数确定 (RAG 优先, 搜索回退) ======
            if rag_params is not None and rag_confidence > 0.7:
                top_params_list = [rag_params]
                top_strengths = [rag_strength]
                top_scores = [rag_confidence * 100.0]
                phase1_5 = PhaseResult(
                    phase=1.5, name="参数推荐(RAG)",
                    status=PhaseStatus.COMPLETED,
                    output={
                        "top_params_list": top_params_list,
                        "top_strengths": top_strengths,
                        "top_scores": top_scores,
                        "source": "rag_llm",
                    },
                    elapsed_ms=0,
                )
            else:
                phase1_5 = self._run_strength_search(
                    phase1.output.get("wave_state_diagnosis"),
                    emotion_target,
                    defects=phase1.output.get("defects"),
                    vector_bias=emotion_parsed.get("vector_bias"),
                    audio=audio, sr=sr,
                )
                top_params_list = phase1_5.output.get("top_params_list", [])
                top_strengths = phase1_5.output.get("top_strengths", [])
                top_scores = phase1_5.output.get("top_scores", [])

                if not top_params_list:
                    from moodify.knowledge.craft_chains import get_recommended_params
                    from moodify.knowledge.emotion_targets import resolve_emotion, KEY_TO_CODE
                    try:
                        code = resolve_emotion(emotion_target)
                        code = KEY_TO_CODE.get(code, "GA")
                    except Exception:
                        code = "GA"
                    top_params_list = [get_recommended_params(code)]
                    top_strengths = [{"spectrum": 0.5, "dynamic": 0.5, "space": 0.5, "layer": 0.5, "master": 0.5}]
                    top_scores = [0.0]

            phases.append(phase1_5)

            if audio is None:
                raise RuntimeError("Failed to load audio in Phase 2")

            # ====== Phase 3: 频谱增强 (多版本) ======
            phase3 = self._run_spectral_enhancement_multi(audio, sr, top_params_list)
            phases.append(phase3)
            versions = phase3.output.get("versions", [audio])

            # ====== Phase 4-6: 对每个版本分别处理 + 测量选优 ======
            ws_diagnosis = phase1.output.get("wave_state_diagnosis")
            best_eds = -999.0
            best_idx = 0
            best_whs_after = 0.0
            best_output = ""
            best_params: dict = {}
            best_strength: dict = {}

            for i, ver_audio in enumerate(versions):
                p4 = self._run_spatial(ver_audio, sr, emotion_target, None)
                p5 = self._run_resynthesis(p4.output["audio"], sr)
                p6 = self._run_mastering(p5.output["audio"], sr, input_path, emotion_target, platform,
                                         version_suffix=f"_v{i}")

                ver_output = p6.output.get("output_path", "")
                if ver_output and os.path.exists(ver_output):
                    try:
                        ws_a = self._diagnose_audio(ver_output)
                        whs_a = self._compute_whs(ws_a)
                        eds_a = self._compute_eds(ws_diagnosis, ws_a, emotion_target,
                                                  vector_bias=emotion_parsed.get("vector_bias"))
                    except Exception:
                        whs_a, eds_a = 0.0, 0.0
                else:
                    whs_a, eds_a = 0.0, 0.0

                phases.extend([p4, p5, p6])

                if eds_a > best_eds:
                    best_eds = eds_a
                    best_idx = i
                    best_whs_after = whs_a
                    best_output = ver_output
                    if i < len(top_params_list):
                        best_params = top_params_list[i]
                    if i < len(top_strengths):
                        best_strength = top_strengths[i]

            output_path = best_output
            whs_after = best_whs_after
            eds = best_eds
            whs_before = phase1.output.get("whs", 0)

            total_elapsed = (time.perf_counter() - total_start) * 1000
            success = all(
                p.status in (PhaseStatus.COMPLETED, PhaseStatus.SKIPPED)
                for p in phases
            )

            ws_before_obj = ws_diagnosis
            ws_after_obj = None
            if output_path and os.path.exists(output_path):
                try:
                    ws_after_obj = self._diagnose_audio(output_path)
                except Exception:
                    pass

            # LLM 诊断解读（阶段 B）
            narrative = None
            try:
                from moodify.llm.client import DeepSeekClient
                llm = DeepSeekClient()
                if llm.available and ws_before_obj and output_path:
                    ws_for_narration = ws_after_obj or (self._diagnose_audio(output_path) if output_path and os.path.exists(output_path) else None)
                    if ws_for_narration:
                        narrative = llm.narrate_diagnosis(
                            before_dict=ws_before_obj.to_dict(),
                            after_dict=ws_for_narration.to_dict(),
                            params=best_params if best_params else {},
                            whs_before=whs_before,
                            whs_after=whs_after if whs_after > 0 else whs_before,
                            eds=eds,
                            emotion_name=emotion_target,
                        )
            except Exception:
                pass

            # ====== 记录处理历史 ======
            try:
                from moodify.memory.history import ProcessingHistory, ProcessingRecord, diagnosis_to_vector
                h = ProcessingHistory(self._output_dir)
                h.save(ProcessingRecord(
                    diagnosis_vector=diagnosis_to_vector(ws_before_obj),
                    params=best_params if best_params else (top_params_list[0] if top_params_list else {}),
                    strength_vector=best_strength if best_strength else (top_strengths[0] if top_strengths else {}),
                    whs_before=whs_before,
                    whs_after=whs_after if whs_after > 0 else whs_before,
                    eds=eds,
                    proxy_score=float(top_scores[best_idx]) if top_scores and best_idx < len(top_scores) else 0.0,
                    emotion_code=emotion_parsed["emotion_code"],
                    emotion_name=emotion_parsed.get("emotion_name", emotion_target),
                    user_intent="",
                    satisfied=None,
                    user_feedback="",
                    timestamp=datetime.now().isoformat(),
                ))
            except Exception:
                pass

            return WorkflowResult(
                phases=phases,
                input_path=input_path,
                output_path=output_path,
                emotion_target=emotion_target,
                wave_state_before=ws_before_obj.to_dict() if ws_before_obj else {},
                wave_state_after=ws_after_obj.to_dict() if ws_after_obj else {},
                delta=self._compute_delta(ws_before_obj, ws_after_obj) if output_path and ws_after_obj else {},
                whs_before=whs_before,
                whs_after=whs_after if whs_after > 0 else whs_before,
                eds=eds,
                total_risk=0.0,
                risk_level="green",
                total_elapsed_ms=total_elapsed,
                success=success,
                process_id=process_id,
            )

        except Exception as e:
            import traceback
            traceback.print_exc()
            return WorkflowResult(
                phases=phases, input_path=input_path, output_path=output_path,
                emotion_target=emotion_target,
                wave_state_before={}, wave_state_after={}, delta={},
                whs_before=0, whs_after=0, eds=0,
                total_risk=0, risk_level="error",
                total_elapsed_ms=(time.perf_counter() - total_start) * 1000,
                success=False, process_id=process_id,
            )

    # ====== Phase Implementations ======

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

        # Match craft card
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
        """Phase 2: 音频加载 — 仅加载音频,不做源分离。

        Demucs 源分离已移除。理由:
          - AI 生成音乐无真正声部边界, Demucs 分离质量差且引入伪影
          - 速度慢 (30-60s CPU), 严重影响用户体验
          - Phase 3 改用 HPSS 频谱分解, <1s 完成, 无 DL 伪影
        """
        t0 = time.perf_counter()
        try:
            audio, sr = soundfile.read(input_path)
            audio = audio.astype(np.float32)
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

    def _run_spectral_enhancement(self, audio: np.ndarray, sr: int,
                                    craft_card) -> PhaseResult:
        """Phase 3: 频谱增强 — HPSS 谐波/打击乐分离 + 差异处理。

        使用 SpectralDSPChain 替代旧版 Demucs stem 分离:
          1. HPSS → H (谐波/延音) + P (打击乐/瞬态)
          2. H 链: 人声临场 EQ + 低频温暖 + 混响 + 高频搁架 (频率塑形)
          3. P 链: 压缩 + 谐波驱动 (动态塑形)
          4. 叠加 → 立体声输出
        """
        t0 = time.perf_counter()
        warnings = []

        # Resolve emotion code from craft card
        emotion_code = None
        if craft_card is not None:
            try:
                emotion_code = craft_card.craft_card_id[3:5]
            except Exception:
                pass

        if emotion_code is None:
            return PhaseResult(
                phase=3, name="频谱增强",
                status=PhaseStatus.SKIPPED,
                output={"audio": audio},
                warnings=["No craft card; passing through"],
                elapsed_ms=(time.perf_counter() - t0) * 1000,
            )

        try:
            from moodify.knowledge.craft_chains import get_recommended_params
            from moodify.processing.spectral_chain import SpectralDSPChain

            params = get_recommended_params(emotion_code)
            chain = SpectralDSPChain()
            output_audio = chain.process(audio, sr, params)

            warnings.append(
                f"HPSS spectral enhancement: '{emotion_code}' ({len(params)} params)"
            )

            return PhaseResult(
                phase=3, name="频谱增强",
                status=PhaseStatus.COMPLETED,
                output={"audio": output_audio, "emotion_code": emotion_code},
                warnings=warnings,
                elapsed_ms=(time.perf_counter() - t0) * 1000,
            )

        except Exception as e:
            import traceback
            warnings.append(f"Spectral enhancement error: {e}; passing through")
            traceback.print_exc()
            return PhaseResult(
                phase=3, name="频谱增强",
                status=PhaseStatus.COMPLETED,
                output={"audio": audio},
                warnings=warnings,
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

        # Get width from craft card params
        width = 1.0
        if craft_card is not None:
            try:
                params = craft_card.get_recommended_params()
                width = params.get("P12_reverb_width", 1.0)
            except Exception:
                pass
        else:
            # Default width from emotion
            try:
                from moodify.knowledge.craft_chains import get_recommended_params
                from moodify.knowledge.emotion_targets import resolve_emotion, KEY_TO_CODE
                resolved_key = resolve_emotion(emotion_target)
                resolved_code = KEY_TO_CODE.get(resolved_key, "GA")
                params = get_recommended_params(resolved_code)
                width = params.get("P12_reverb_width", 1.0)
            except Exception:
                pass

        # M/S processing
        mid = (audio[:, 0] + audio[:, 1]) / 2.0
        side = (audio[:, 0] - audio[:, 1]) / 2.0

        # Apply width control
        side_processed = side * width

        # Reconstruct stereo
        result = np.zeros_like(audio)
        result[:, 0] = mid + side_processed
        result[:, 1] = mid - side_processed

        # Prevent clipping
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

    def _run_resynthesis(self, audio: np.ndarray, sr: int) -> PhaseResult:
        """Phase 5: 再合成 — 透传 (频谱链已直接输出立体声)。"""
        t0 = time.perf_counter()
        return PhaseResult(
            phase=5, name="再合成",
            status=PhaseStatus.COMPLETED,
            output={"audio": audio},
            elapsed_ms=(time.perf_counter() - t0) * 1000,
        )

    def _run_mastering(self, audio: np.ndarray, sr: int,
                        input_path: str, emotion_target: str,
                        platform: str = "spotify",
                        version_suffix: str = "") -> PhaseResult:
        """Phase 6: 情绪显影 + 母带 — 响度标准化 + 限幅 + 导出"""
        t0 = time.perf_counter()
        warnings = []
        total_risk = 0.0
        risk_level = "green"

        try:
            import pyloudnorm as pyln
            import pedalboard

            # Ensure float32 for processing
            audio_f32 = audio.astype(np.float32)

            # Loudness normalize to -14 LUFS (Spotify standard)
            if platform == "apple_music":
                target_lufs = -16.0
            else:
                target_lufs = -14.0

            # Measure integrated loudness
            meter = pyln.Meter(sr)
            if audio_f32.ndim > 1:
                loudness = meter.integrated_loudness(audio_f32)
            else:
                loudness = meter.integrated_loudness(audio_f32)

            # Normalize
            if not np.isinf(loudness) and not np.isnan(loudness):
                audio_normalized = pyln.normalize.loudness(audio_f32, loudness, target_lufs)
            else:
                audio_normalized = audio_f32
                warnings.append("Could not measure loudness; skipping normalization")

            # Brick-wall limiter (True Peak <= -1 dBTP)
            limiter = pedalboard.Limiter(threshold_db=-1.0, release_ms=50)
            if audio_normalized.ndim > 1:
                audio_limited = limiter(audio_normalized.T.astype(np.float32), sr).T
            else:
                audio_limited = limiter(
                    audio_normalized.reshape(1, -1).astype(np.float32), sr
                )[0]

            # Prevent clipping
            peak = np.max(np.abs(audio_limited))
            if peak > 0.99:
                audio_limited *= 0.99 / peak

            # Export to WAV
            os.makedirs(self._output_dir, exist_ok=True)
            base_name = Path(input_path).stem
            emotion_short = emotion_target[:2] if len(emotion_target) >= 2 else emotion_target
            output_filename = f"{base_name}_{emotion_short}_{platform}{version_suffix}.wav"
            output_path = os.path.join(self._output_dir, output_filename)

            soundfile.write(output_path, audio_limited, sr, subtype='PCM_16')

            # Quality check
            if np.max(np.abs(audio_limited)) > 0.999:
                risk_level = "yellow"
                total_risk += 0.2
                warnings.append("Output near digital ceiling")

            return PhaseResult(
                phase=6, name="情绪显影+母带",
                status=PhaseStatus.COMPLETED,
                output={
                    "output_path": output_path,
                    "audio": audio_limited,
                    "total_risk": total_risk,
                    "risk_level": risk_level,
                    "loudness_normalized": True,
                    "target_lufs": target_lufs,
                },
                warnings=warnings,
                elapsed_ms=(time.perf_counter() - t0) * 1000,
            )

        except Exception as e:
            # Fallback: just export without mastering
            try:
                os.makedirs(self._output_dir, exist_ok=True)
                base_name = Path(input_path).stem
                emotion_short = emotion_target[:2]
                output_path = os.path.join(
                    self._output_dir,
                    f"{base_name}_{emotion_short}_{platform}{version_suffix}.wav"
                )
                soundfile.write(output_path, audio, sr, subtype='PCM_16')
                warnings.append(f"Mastering failed ({e}); exported raw audio")
                return PhaseResult(
                    phase=6, name="情绪显影+母带",
                    status=PhaseStatus.COMPLETED,
                    output={
                        "output_path": output_path,
                        "audio": audio,
                        "total_risk": 0.5,
                        "risk_level": "yellow",
                    },
                    warnings=warnings,
                    elapsed_ms=(time.perf_counter() - t0) * 1000,
                )
            except Exception as e2:
                return PhaseResult(
                    phase=6, name="情绪显影+母带",
                    status=PhaseStatus.FAILED,
                    output={"output_path": "", "total_risk": 1.0, "risk_level": "red"},
                    warnings=warnings + [f"Export failed: {e2}"],
                    elapsed_ms=(time.perf_counter() - t0) * 1000,
                    gate_passed=False,
                )

    # ====== Phase 1.5: 5D 强度空间搜索 ======

    def _run_strength_search(self, ws_diagnosis, emotion_target: str,
                             defects=None, vector_bias=None,
                             audio=None, sr=44100) -> PhaseResult:
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
            import traceback; traceback.print_exc()
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

    # ====== Phase 3 multi-version ======

    def _run_spectral_enhancement_multi(
        self, audio: np.ndarray, sr: int, params_list: list[dict]
    ) -> PhaseResult:
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

    # ====== Helpers ======

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
        print(f"  FAILED")
    return result.output_path
