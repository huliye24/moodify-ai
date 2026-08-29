"""
Moodify Lab 数据类型定义 — MATH/PHYS Foundation 升级版 (SPEC-011 批次 1).

每个诊断参数从裸 float/int 升级为 ParameterWithUncertainty 组合体,
包含: 点估计 + 标准不确定度 + 95% CI + 层级 + 置信等级 + 来源 + 协议版本.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class SpectrumState:
    """频谱状态"""
    band_energies: dict[str, float] = field(default_factory=dict)  # 各频段能量 dB
    spectral_centroid: float = 0.0  # Hz
    crowding_ratio: dict[str, float] = field(default_factory=dict)  # 各频段拥挤度
    hri: float = 0.0  # 高频刺耳风险指数 [0, 1]


@dataclass
class DynamicsState:
    """动态状态"""
    rms_mean: float = 0.0  # dB
    rms_std: float = 0.0
    peak_mean: float = 0.0  # dB
    crest_mean: float = 0.0  # 峰均比
    dynamic_range: float = 0.0  # dB
    dfi: float = 0.0  # 动态压平指数 [0, 1]


@dataclass
class SpaceState:
    """空间状态"""
    correlation_lr: float = 0.0  # 左右相关性 [-1, 1]
    side_ratio: float = 0.0  # 侧向能量比
    false_width_risk: float = 0.0  # 假宽风险 [0, 1]


@dataclass
class LayersState:
    """层级状态"""
    vocal_ratio: float = 0.0
    drums_ratio: float = 0.0
    bass_ratio: float = 0.0
    other_ratio: float = 0.0
    vpi: float = 0.0  # 人声存在感指数 [0, 1]
    layer_adhesion: float = 0.0  # 层级粘连指数 [0, 1]


@dataclass
class EmotionState:
    """情绪状态"""
    target_emotion: str = ""
    q_emotion: float = 0.0  # 情绪显影评分 [0, 1]
    fatigue_risk: float = 0.0  # 听觉疲劳风险 [0, 1]
    overprocess_risk: float = 0.0  # 过处理风险 [0, 1]
    subjective_score: float = 0.0  # 人耳主观评分 [0, 1]
    listener_notes: str = ""


@dataclass
class WaveState:
    """五维波场状态"""
    spectrum: SpectrumState = field(default_factory=SpectrumState)
    dynamics: DynamicsState = field(default_factory=DynamicsState)
    space: SpaceState = field(default_factory=SpaceState)
    layers: LayersState = field(default_factory=LayersState)
    emotion: EmotionState = field(default_factory=EmotionState)
    timestamp: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            "spectrum": {
                "band_energies": self.spectrum.band_energies,
                "spectral_centroid": self.spectrum.spectral_centroid,
                "crowding_ratio": self.spectrum.crowding_ratio,
                "hri": self.spectrum.hri,
            },
            "dynamics": {
                "rms_mean": self.dynamics.rms_mean,
                "rms_std": self.dynamics.rms_std,
                "peak_mean": self.dynamics.peak_mean,
                "crest_mean": self.dynamics.crest_mean,
                "dynamic_range": self.dynamics.dynamic_range,
                "dfi": self.dynamics.dfi,
            },
            "space": {
                "correlation_lr": self.space.correlation_lr,
                "side_ratio": self.space.side_ratio,
                "false_width_risk": self.space.false_width_risk,
            },
            "layers": {
                "vocal_ratio": self.layers.vocal_ratio,
                "drums_ratio": self.layers.drums_ratio,
                "bass_ratio": self.layers.bass_ratio,
                "other_ratio": self.layers.other_ratio,
                "vpi": self.layers.vpi,
                "layer_adhesion": self.layers.layer_adhesion,
            },
            "emotion": {
                "target_emotion": self.emotion.target_emotion,
                "q_emotion": self.emotion.q_emotion,
                "fatigue_risk": self.emotion.fatigue_risk,
                "overprocess_risk": self.emotion.overprocess_risk,
                "subjective_score": self.emotion.subjective_score,
                "listener_notes": self.emotion.listener_notes,
            },
            "timestamp": self.timestamp.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: dict) -> "WaveState":
        """从字典创建"""
        spectrum = SpectrumState(**data.get("spectrum", {}))
        dynamics = DynamicsState(**data.get("dynamics", {}))
        space = SpaceState(**data.get("space", {}))
        layers = LayersState(**data.get("layers", {}))
        emotion = EmotionState(**data.get("emotion", {}))
        timestamp = datetime.fromisoformat(data.get("timestamp", datetime.now().isoformat()))
        return cls(
            spectrum=spectrum,
            dynamics=dynamics,
            space=space,
            layers=layers,
            emotion=emotion,
            timestamp=timestamp,
        )


@dataclass
class AudioRecord:
    """音频记录"""
    audio_id: str
    file_path: str
    source: str = ""  # Suno/Udio/本地
    style: str = ""  # 风格
    emotion_tags: list[str] = field(default_factory=list)
    metadata: dict = field(default_factory=dict)
    wave_state: Optional[WaveState] = None
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class Experiment:
    """实验记录"""
    exp_id: str
    name: str
    hypothesis: str = ""
    description: str = ""
    setup: dict = field(default_factory=dict)
    results: list[dict] = field(default_factory=list)
    conclusion: str = ""
    status: str = "pending"  # pending/running/completed/failed
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)


@dataclass
class CraftCard:
    """工艺卡"""
    card_id: str
    emotion_target: str
    wave_state_initial: Optional[WaveState] = None
    wave_state_final: Optional[WaveState] = None
    processing_chain: list[str] = field(default_factory=list)  # 处理步骤名称
    parameters: dict = field(default_factory=dict)
    quality_score: float = 0.0  # [0, 1]
    validated: bool = False
    tags: list[str] = field(default_factory=list)
    notes: str = ""
    created_at: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> dict:
        return {
            "card_id": self.card_id,
            "emotion_target": self.emotion_target,
            "wave_state_initial": self.wave_state_initial.to_dict() if self.wave_state_initial else None,
            "wave_state_final": self.wave_state_final.to_dict() if self.wave_state_final else None,
            "processing_chain": self.processing_chain,
            "parameters": self.parameters,
            "quality_score": self.quality_score,
            "validated": self.validated,
            "tags": self.tags,
            "notes": self.notes,
            "created_at": self.created_at.isoformat(),
        }


# ============================================================================
#  CraftCardV2 — 完整工艺卡 (SPEC §11)
# ============================================================================

@dataclass
class EmotionTarget:
    primary: str
    secondary: list[str] = field(default_factory=list)
    intensity: float = 0.7
    primary_class: str = ""


@dataclass
class ApplicableSources:
    ai_models: list[str] = field(default_factory=list)
    genres: list[str] = field(default_factory=list)
    vocal_types: list[str] = field(default_factory=list)


@dataclass
class DiagnosticMarkers:
    embryo_direction: str = ""
    common_defects: list[str] = field(default_factory=list)
    contraindications: list[str] = field(default_factory=list)


@dataclass
class ParameterRange:
    min: float = 0.0
    rec: float = 0.0
    max: float = 0.0
    unit: str = ""


@dataclass
class ProcessingStep:
    step: int = 0
    name: str = ""
    actions: list[dict] = field(default_factory=list)


@dataclass
class ConfidenceMetrics:
    evidence_count: int = 0
    effect_size: float = 0.0
    reproducibility: float = 0.0
    user_preference: float = 0.0
    risk_incidence: float = 0.0


@dataclass
class VersionEntry:
    version: str = "1.0"
    date: str = ""
    author: str = ""
    changes: str = ""
    rating_data: dict = field(default_factory=dict)


@dataclass
class CraftCardV2:
    """完整工艺卡 — 7 必填字段 (SPEC §11)"""
    craft_card_id: str = ""            # "CC-GA-001"
    name_zh: str = ""
    name_en: str = ""
    target_emotion: EmotionTarget = field(default_factory=EmotionTarget)
    applicable_sources: ApplicableSources = field(default_factory=ApplicableSources)
    diagnostic_markers: DiagnosticMarkers = field(default_factory=DiagnosticMarkers)
    processing_chain: list[ProcessingStep] = field(default_factory=list)
    parameter_ranges: dict[str, ParameterRange] = field(default_factory=dict)
    risk_warnings: list[str] = field(default_factory=list)
    confidence_metrics: ConfidenceMetrics = field(default_factory=ConfidenceMetrics)
    version_history: list[VersionEntry] = field(default_factory=list)
    notes: str = ""
    created_at: datetime = field(default_factory=datetime.now)

    def validate(self) -> list[str]:
        errors = []
        import re
        if not re.match(r'^CC-[A-Z]{2}-\d{3}$', self.craft_card_id):
            errors.append(f"Invalid card_id format: {self.craft_card_id}")
        if len(self.risk_warnings) < 3:
            errors.append(f"Need >= 3 risk_warnings, got {len(self.risk_warnings)}")
        if len(self.parameter_ranges) < 10:
            errors.append(f"Only {len(self.parameter_ranges)} params, expected >= 10")
        return errors

    def get_recommended_params(self) -> dict[str, float]:
        return {k: v.rec for k, v in self.parameter_ranges.items()}

    def to_dict(self) -> dict:
        return {
            "craft_card_id": self.craft_card_id,
            "name_zh": self.name_zh,
            "name_en": self.name_en,
            "target_emotion": {
                "primary": self.target_emotion.primary,
                "secondary": self.target_emotion.secondary,
                "intensity": self.target_emotion.intensity,
                "primary_class": self.target_emotion.primary_class,
            },
            "applicable_sources": {
                "ai_models": self.applicable_sources.ai_models,
                "genres": self.applicable_sources.genres,
                "vocal_types": self.applicable_sources.vocal_types,
            },
            "diagnostic_markers": {
                "embryo_direction": self.diagnostic_markers.embryo_direction,
                "common_defects": self.diagnostic_markers.common_defects,
                "contraindications": self.diagnostic_markers.contraindications,
            },
            "processing_chain": [
                {"step": p.step, "name": p.name, "actions": p.actions}
                for p in self.processing_chain
            ],
            "parameter_ranges": {
                k: {"min": v.min, "rec": v.rec, "max": v.max, "unit": v.unit}
                for k, v in self.parameter_ranges.items()
            },
            "risk_warnings": self.risk_warnings,
            "confidence_metrics": {
                "evidence_count": self.confidence_metrics.evidence_count,
                "effect_size": self.confidence_metrics.effect_size,
                "reproducibility": self.confidence_metrics.reproducibility,
                "user_preference": self.confidence_metrics.user_preference,
                "risk_incidence": self.confidence_metrics.risk_incidence,
            },
            "version_history": [
                {"version": v.version, "date": v.date, "author": v.author,
                 "changes": v.changes, "rating_data": v.rating_data}
                for v in self.version_history
            ],
            "notes": self.notes,
            "created_at": self.created_at.isoformat(),
        }


# ============================================================================
#  ParameterWithUncertainty — MATH-001 可测量量组合体 (SPEC-011 T1.1~T1.4)
# ============================================================================

@dataclass
class ParameterWithUncertainty:
    """MATH-001 可测量量 — 参数值 + 不确定度 + 元数据的组合体.

    MATH-001 公理 D: 每个报告值必须绑定 protocol_version, tool_version.
    MATH-006 §8.1: 强制报告点估计 + 标准不确定度 + 95% CI.
    PHYS-001 §2: 每个量必须显式声明层级 L0/L1/L2.
    """

    value: float = 0.0
    uncertainty: float = 0.0               # 标准不确定度 ±σ
    ci_lower: Optional[float] = None       # 95% CI 下界
    ci_upper: Optional[float] = None       # 95% CI 上界
    level: str = "L1"                      # PHYS-001 层级: L0/L1/L2
    confidence: str = "medium"             # high / medium / low / fallback
    provenance: str = "experiment"         # experiment / computed / fallback
    protocol: str = "unknown"              # 协议版本
    is_fallback: bool = False              # 是否使用回退路径
    fallback_note: str = ""                # 回退说明

    def to_dict(self) -> dict:
        return {
            "value": self.value,
            "uncertainty": self.uncertainty,
            "ci_95": [self.ci_lower, self.ci_upper],
            "level": self.level,
            "confidence": self.confidence,
            "provenance": self.provenance,
            "protocol": self.protocol,
            "is_fallback": self.is_fallback,
            "fallback_note": self.fallback_note,
        }

    @classmethod
    def from_dict(cls, d: dict) -> "ParameterWithUncertainty":
        ci = d.get("ci_95", [None, None])
        return cls(
            value=d.get("value", 0.0),
            uncertainty=d.get("uncertainty", 0.0),
            ci_lower=ci[0] if ci else None,
            ci_upper=ci[1] if len(ci) > 1 else None,
            level=d.get("level", "L1"),
            confidence=d.get("confidence", "medium"),
            provenance=d.get("provenance", "experiment"),
            protocol=d.get("protocol", "unknown"),
            is_fallback=d.get("is_fallback", False),
            fallback_note=d.get("fallback_note", ""),
        )


# ============================================================================
#  WaveState_Diagnosis — 完整 18 参数诊断数据结构 (SPEC §2.2 + SPEC-011 T1)
# ============================================================================

@dataclass
class SpectrumDiagnosis:
    """频谱维度 5 参数 — MATH-001 公理体系升级版"""
    S1_SubPresence: ParameterWithUncertainty = field(
        default_factory=ParameterWithUncertainty)
    S2_BassWarmth: ParameterWithUncertainty = field(
        default_factory=ParameterWithUncertainty)
    S3_MidClarity: ParameterWithUncertainty = field(
        default_factory=ParameterWithUncertainty)
    S4_AirBand: ParameterWithUncertainty = field(
        default_factory=ParameterWithUncertainty)
    S5_SpectralTilt: ParameterWithUncertainty = field(
        default_factory=ParameterWithUncertainty)

    def to_dict(self) -> dict:
        return {
            "S1_SubPresence": self.S1_SubPresence.to_dict(),
            "S2_BassWarmth": self.S2_BassWarmth.to_dict(),
            "S3_MidClarity": self.S3_MidClarity.to_dict(),
            "S4_AirBand": self.S4_AirBand.to_dict(),
            "S5_SpectralTilt": self.S5_SpectralTilt.to_dict(),
        }


@dataclass
class DynamicsDiagnosis:
    """动态维度 4 参数 — MATH-001 公理体系升级版"""
    D1_LRA: ParameterWithUncertainty = field(
        default_factory=ParameterWithUncertainty)
    D2_ChorusImpact: ParameterWithUncertainty = field(
        default_factory=ParameterWithUncertainty)
    D3_MicroDynamics: ParameterWithUncertainty = field(
        default_factory=ParameterWithUncertainty)
    D4_PLR: ParameterWithUncertainty = field(
        default_factory=ParameterWithUncertainty)

    def to_dict(self) -> dict:
        return {
            "D1_LRA": self.D1_LRA.to_dict(),
            "D2_ChorusImpact": self.D2_ChorusImpact.to_dict(),
            "D3_MicroDynamics": self.D3_MicroDynamics.to_dict(),
            "D4_PLR": self.D4_PLR.to_dict(),
        }


@dataclass
class SpaceDiagnosis:
    """空间维度 4 参数 — SP4 保持 bool (非测量量)"""
    SP1_Correlation: ParameterWithUncertainty = field(
        default_factory=ParameterWithUncertainty)
    SP2_ForeBackSep: ParameterWithUncertainty = field(
        default_factory=ParameterWithUncertainty)
    SP3_RT60Consist: ParameterWithUncertainty = field(
        default_factory=ParameterWithUncertainty)
    SP4_WidthHealth: bool = True     # 派生判断, 非测量量

    def to_dict(self) -> dict:
        return {
            "SP1_Correlation": self.SP1_Correlation.to_dict(),
            "SP2_ForeBackSep": self.SP2_ForeBackSep.to_dict(),
            "SP3_RT60Consist": self.SP3_RT60Consist.to_dict(),
            "SP4_WidthHealth": self.SP4_WidthHealth,
        }


@dataclass
class LayersDiagnosis:
    """层级维度 4 参数 — L4 主观评分 (L2 桥接量)"""
    L1_VocalSNR: ParameterWithUncertainty = field(
        default_factory=ParameterWithUncertainty)
    L2_BassClarity: ParameterWithUncertainty = field(
        default_factory=ParameterWithUncertainty)
    L3_DrumDetect: ParameterWithUncertainty = field(
        default_factory=ParameterWithUncertainty)
    L4_LayerCount: ParameterWithUncertainty = field(
        default_factory=lambda: ParameterWithUncertainty(value=3.0, level="L2"))

    def to_dict(self) -> dict:
        return {
            "L1_VocalSNR": self.L1_VocalSNR.to_dict(),
            "L2_BassClarity": self.L2_BassClarity.to_dict(),
            "L3_DrumDetect": self.L3_DrumDetect.to_dict(),
            "L4_LayerCount": self.L4_LayerCount.to_dict(),
        }


@dataclass
class EmotionDiagnosis:
    """情绪维度 4 参数 — E1/E2 主观评分 (L2 桥接量)"""
    E1_Direction: ParameterWithUncertainty = field(
        default_factory=lambda: ParameterWithUncertainty(value=5.0, level="L2"))
    E2_Richness: ParameterWithUncertainty = field(
        default_factory=lambda: ParameterWithUncertainty(value=5.0, level="L2"))
    E3_FatigueRisk: ParameterWithUncertainty = field(
        default_factory=ParameterWithUncertainty)
    E4_SectionCont: ParameterWithUncertainty = field(
        default_factory=ParameterWithUncertainty)

    def to_dict(self) -> dict:
        return {
            "E1_Direction": self.E1_Direction.to_dict(),
            "E2_Richness": self.E2_Richness.to_dict(),
            "E3_FatigueRisk": self.E3_FatigueRisk.to_dict(),
            "E4_SectionCont": self.E4_SectionCont.to_dict(),
        }


@dataclass
class WaveStateDiagnosis:
    """五维波场诊断状态 — 完整 18 参数 (SPEC §2.2 + SPEC-011 T2)"""
    Spectrum: SpectrumDiagnosis = field(default_factory=SpectrumDiagnosis)
    Dynamics: DynamicsDiagnosis = field(default_factory=DynamicsDiagnosis)
    Space: SpaceDiagnosis = field(default_factory=SpaceDiagnosis)
    Layers: LayersDiagnosis = field(default_factory=LayersDiagnosis)
    Emotion: EmotionDiagnosis = field(default_factory=EmotionDiagnosis)
    audio_path: str = ""
    duration_s: float = 0.0
    sample_rate: int = 44100
    timestamp: datetime = field(default_factory=datetime.now)
    # SPEC-011 T2.2~T2.3: 协议元数据
    protocol_mode: str = "full"              # "quick" or "full"
    stft_config: dict = field(default_factory=dict)  # FFT 参数快照
    # SPEC-011 T7.4: 归一化声明
    normalization_notes: list = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "Spectrum": self.Spectrum.to_dict(),
            "Dynamics": self.Dynamics.to_dict(),
            "Space": self.Space.to_dict(),
            "Layers": self.Layers.to_dict(),
            "Emotion": self.Emotion.to_dict(),
            "audio_path": self.audio_path,
            "duration_s": self.duration_s,
            "sample_rate": self.sample_rate,
            "timestamp": self.timestamp.isoformat(),
            "protocol_mode": self.protocol_mode,
            "stft_config": self.stft_config,
            "normalization_notes": self.normalization_notes,
        }

    def get_auto_params(self) -> dict[str, float]:
        """提取全部 14 个自动测量参数的点估计值"""
        return {
            "S1_SubPresence": self.Spectrum.S1_SubPresence.value,
            "S2_BassWarmth": self.Spectrum.S2_BassWarmth.value,
            "S3_MidClarity": self.Spectrum.S3_MidClarity.value,
            "S4_AirBand": self.Spectrum.S4_AirBand.value,
            "S5_SpectralTilt": self.Spectrum.S5_SpectralTilt.value,
            "D1_LRA": self.Dynamics.D1_LRA.value,
            "D2_ChorusImpact": self.Dynamics.D2_ChorusImpact.value,
            "D3_MicroDynamics": self.Dynamics.D3_MicroDynamics.value,
            "D4_PLR": self.Dynamics.D4_PLR.value,
            "SP1_Correlation": self.Space.SP1_Correlation.value,
            "SP2_ForeBackSep": self.Space.SP2_ForeBackSep.value,
            "SP3_RT60Consist": self.Space.SP3_RT60Consist.value,
            "L3_DrumDetect": self.Layers.L3_DrumDetect.value,
            "E3_FatigueRisk": self.Emotion.E3_FatigueRisk.value,
            "E4_SectionCont": self.Emotion.E4_SectionCont.value,
        }

    def is_complete(self) -> bool:
        """检查 14 自动参数是否全部有效（非 NaN, 非 Inf）"""
        import math
        for name, val in self.get_auto_params().items():
            if val is None or math.isnan(val) or math.isinf(val):
                return False
        return True
