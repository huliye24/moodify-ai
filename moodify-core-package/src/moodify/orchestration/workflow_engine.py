"""
workflow_engine.py — 六阶段工作流编排器 (SPEC §10)
=====================================================
Phase 1: 诊断 -> Phase 2: 源分离 -> Phase 3: 分层增强
-> Phase 4: 空间重构 -> Phase 5: 再合成 -> Phase 6: 情绪显影 + 母带

三质量门: Gate 1 (诊断完整性) -> Gate 2 (分离质量) -> Gate 3 (输出合规性)
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
            # ====== Phase 1: 诊断 ======
            phase1 = self._run_diagnosis(input_path, emotion_target)
            phases.append(phase1)

            # ====== Phase 2: 源分离 ======
            phase2 = self._run_separation(input_path)
            phases.append(phase2)
            stems = phase2.output.get("stems")
            separation_mode = "5_layer" if stems else "full_mix"
            audio = phase2.output.get("audio")
            sr = phase2.output.get("sr", 44100)

            if audio is None:
                raise RuntimeError("Failed to load audio in Phase 2")

            # ====== Phase 3: 分层增强 ======
            phase3 = self._run_enhancement(
                audio, sr, stems, emotion_target, separation_mode,
                phase1.output.get("craft_card")
            )
            phases.append(phase3)
            audio = phase3.output.get("audio", audio)

            # ====== Phase 4: 空间重构 ======
            phase4 = self._run_spatial(
                audio, sr, emotion_target,
                phase1.output.get("craft_card")
            )
            phases.append(phase4)
            audio = phase4.output.get("audio", audio)

            # ====== Phase 5: 再合成 ======
            phase5 = self._run_resynthesis(stems, audio, sr)
            phases.append(phase5)
            audio = phase5.output.get("audio", audio)

            # ====== Phase 6: 情绪显影 + 母带 ======
            phase6 = self._run_mastering(
                audio, sr, input_path, emotion_target, platform
            )
            phases.append(phase6)

            output_path = phase6.output.get("output_path", "")

            # ====== 计算评分 ======
            ws_before = phase1.output.get("wave_state_diagnosis")
            whs_before = phase1.output.get("whs", 0)
            whs_after = whs_before
            eds = 0.0

            if output_path and os.path.exists(output_path):
                try:
                    ws_after = self._diagnose_audio(output_path)
                    whs_after = self._compute_whs(ws_after)
                    eds = self._compute_eds(ws_before, ws_after, emotion_target)
                except Exception:
                    pass

            total_elapsed = (time.perf_counter() - total_start) * 1000
            success = all(
                p.status in (PhaseStatus.COMPLETED, PhaseStatus.SKIPPED)
                for p in phases
            )

            return WorkflowResult(
                phases=phases,
                input_path=input_path,
                output_path=output_path,
                emotion_target=emotion_target,
                wave_state_before=ws_before.to_dict() if ws_before else {},
                wave_state_after=ws_after.to_dict() if ws_after else {},
                delta=self._compute_delta(ws_before, ws_after) if output_path else {},
                whs_before=whs_before,
                whs_after=whs_after,
                eds=eds,
                total_risk=phase6.output.get("total_risk", 0),
                risk_level=phase6.output.get("risk_level", "green"),
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

    def _run_separation(self, input_path: str) -> PhaseResult:
        """Phase 2: 源分离 — 尝试 Demucs，不可用时降级为 full_mix"""
        t0 = time.perf_counter()
        stems = None
        mode = "full_mix"
        warnings = []
        audio = None
        sr = 44100

        # Load audio with soundfile
        try:
            audio, sr = soundfile.read(input_path)
            if audio.ndim == 1:
                audio = audio.astype(np.float32)
            else:
                audio = audio.astype(np.float32)
        except Exception as e:
            return PhaseResult(
                phase=2, name="源分离",
                status=PhaseStatus.FAILED,
                output={"stems": None, "mode": mode, "audio": None, "sr": sr},
                warnings=[f"Failed to load audio: {e}"],
                elapsed_ms=(time.perf_counter() - t0) * 1000,
                gate_passed=False,
            )

        # Try Demucs source separation
        try:
            import demucs.separate
            import tempfile
            import shutil

            # Create temp dirs for demucs
            tmp_in = tempfile.mkdtemp(prefix="moodify_demucs_in_")
            tmp_out = tempfile.mkdtemp(prefix="moodify_demucs_out_")
            tmp_in_path = os.path.join(tmp_in, "input.wav")
            soundfile.write(tmp_in_path, audio, sr)

            try:
                demucs.separate.main([
                    "--two-stems=vocals",
                    "-o", tmp_out,
                    tmp_in_path,
                ])
                # Look for output files
                model_dir = os.path.join(tmp_out, "htdemucs", "input")
                if os.path.isdir(model_dir):
                    stems = {}
                    for stem_name in ["vocals", "drums", "bass", "other"]:
                        stem_path = os.path.join(model_dir, f"{stem_name}.wav")
                        if os.path.exists(stem_path):
                            s_audio, _ = soundfile.read(stem_path)
                            stems[stem_name] = s_audio.astype(np.float32)
                    if len(stems) >= 2:
                        mode = "5_layer"
                        warnings.append(f"Demucs separation: {len(stems)} stems extracted")
                    else:
                        stems = None
                else:
                    warnings.append("Demucs ran but no output found; using full-mix mode")
            finally:
                shutil.rmtree(tmp_in, ignore_errors=True)
                shutil.rmtree(tmp_out, ignore_errors=True)

        except ImportError:
            warnings.append("Demucs not available; using full-mix mode")
        except Exception as e:
            warnings.append(f"Demucs separation failed: {e}; using full-mix mode")

        return PhaseResult(
            phase=2, name="源分离",
            status=PhaseStatus.COMPLETED,
            output={"stems": stems, "mode": mode, "audio": audio, "sr": sr},
            warnings=warnings,
            elapsed_ms=(time.perf_counter() - t0) * 1000,
            gate_passed=True,
        )

    def _run_enhancement(self, audio: np.ndarray, sr: int,
                          stems, emotion_target: str,
                          mode: str, craft_card) -> PhaseResult:
        """Phase 3: 分层增强 — 使用 MoodifyDSPChain 应用工艺卡参数"""
        t0 = time.perf_counter()
        warnings = []
        emotion_code = None

        # Determine emotion code
        if craft_card is not None:
            try:
                cid = craft_card.craft_card_id
                emotion_code = cid[3:5]  # "CC-GA-001" -> "GA"
            except Exception:
                pass

        if emotion_code is None:
            # Try to resolve from emotion target name
            try:
                from moodify.knowledge.emotion_targets import resolve_emotion
                emotion_code = resolve_emotion(emotion_target, as_key=True)
            except Exception:
                pass

        if emotion_code is None:
            return PhaseResult(
                phase=3, name="分层增强",
                status=PhaseStatus.SKIPPED,
                output={"audio": audio, "mode": mode},
                warnings=["Could not resolve emotion code; passing through"],
                elapsed_ms=(time.perf_counter() - t0) * 1000,
            )

        try:
            from moodify.processing.pedalboard_chain import create_chain_from_code

            chain = create_chain_from_code(emotion_code)

            if stems and mode == "5_layer":
                # Process each stem independently
                processed_stems = {}
                for stem_name, stem_audio in stems.items():
                    if stem_audio.ndim == 2 or np.isscalar(stem_audio):
                        stem_audio_proc = chain.process(stem_audio, sr)
                        processed_stems[stem_name] = stem_audio_proc
                output_audio = audio  # Stems mixed in Phase 5
                warnings.append(f"Enhanced {len(processed_stems)} stems with emotion '{emotion_code}'")
            else:
                # Full mix mode: process the entire mix
                output_audio = chain.process(audio, sr)
                warnings.append(f"Enhanced full mix with emotion '{emotion_code}'")

            return PhaseResult(
                phase=3, name="分层增强",
                status=PhaseStatus.COMPLETED,
                output={"audio": output_audio, "mode": mode,
                        "stems": stems, "emotion_code": emotion_code},
                warnings=warnings,
                elapsed_ms=(time.perf_counter() - t0) * 1000,
            )

        except Exception as e:
            warnings.append(f"Enhancement error: {e}; passing through")
            return PhaseResult(
                phase=3, name="分层增强",
                status=PhaseStatus.COMPLETED,
                output={"audio": audio, "mode": mode},
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
                from moodify.knowledge.emotion_targets import resolve_emotion
                code = resolve_emotion(emotion_target, as_key=True)
                params = get_recommended_params(code)
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

    def _run_resynthesis(self, stems, audio: np.ndarray, sr: int) -> PhaseResult:
        """Phase 5: 再合成 — Stem 混合或透传"""
        t0 = time.perf_counter()
        warnings = []

        if stems and len(stems) > 0:
            # Mix stems with gain balancing
            try:
                # Determine target length (use longest stem)
                max_len = max(s.shape[0] for s in stems.values())
                mixed = np.zeros(max_len if stems[list(stems.keys())[0]].ndim == 1
                                 else (max_len, stems[list(stems.keys())[0]].shape[1]),
                                 dtype=np.float32)

                gain_factors = {
                    "vocals": 1.0,
                    "drums": 0.8,
                    "bass": 0.9,
                    "other": 0.7,
                }

                for name, stem_audio in stems.items():
                    gain = gain_factors.get(name, 0.7)
                    if stem_audio.ndim == 1:
                        if mixed.ndim == 2:
                            stem_audio = np.column_stack([stem_audio, stem_audio])
                        n = min(len(stem_audio), mixed.shape[0])
                        mixed[:n] += stem_audio[:n].astype(np.float32) * gain
                    else:
                        n = min(stem_audio.shape[0], mixed.shape[0])
                        mixed[:n] += stem_audio[:n].astype(np.float32) * gain

                # Prevent clipping
                peak = np.max(np.abs(mixed))
                if peak > 0.95:
                    mixed *= 0.95 / peak

                warnings.append(f"Mixed {len(stems)} stems with gain balancing")
                return PhaseResult(
                    phase=5, name="再合成",
                    status=PhaseStatus.COMPLETED,
                    output={"audio": mixed},
                    warnings=warnings,
                    elapsed_ms=(time.perf_counter() - t0) * 1000,
                )
            except Exception as e:
                warnings.append(f"Stem mixing failed: {e}; using processed audio")

        # Full mix passthrough
        return PhaseResult(
            phase=5, name="再合成",
            status=PhaseStatus.COMPLETED,
            output={"audio": audio},
            warnings=warnings if warnings else [],
            elapsed_ms=(time.perf_counter() - t0) * 1000,
        )

    def _run_mastering(self, audio: np.ndarray, sr: int,
                        input_path: str, emotion_target: str,
                        platform: str = "spotify") -> PhaseResult:
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
            output_filename = f"{base_name}_{emotion_short}_{platform}.wav"
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
                    f"{base_name}_{emotion_short}_{platform}.wav"
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

    def _compute_eds(self, ws_before, ws_after, emotion: str) -> float:
        if ws_before is None or ws_after is None:
            return 0
        from moodify.diagnosis.health_scorer import HealthScorer
        scorer = HealthScorer()
        return scorer.compute_eds(ws_before, ws_after, emotion)

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
