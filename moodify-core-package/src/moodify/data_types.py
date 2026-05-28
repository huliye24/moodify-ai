"""
Moodify Lab 数据类型定义
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
#  WaveState_Diagnosis — 完整 18 参数诊断数据结构 (SPEC §2.2)
# ============================================================================

@dataclass
class SpectrumDiagnosis:
    """频谱维度 5 参数"""
    S1_SubPresence: float = 0.0      # RMS(20-60Hz) / RMS(full) [dB]
    S2_BassWarmth: float = 0.0       # RMS(60-250Hz) / RMS(full) [dB]
    S3_MidClarity: float = 0.0       # 1 - masking_index(250-5000Hz) [0-1]
    S4_AirBand: float = 0.0          # RMS(8-16kHz) / RMS(full) [dB]
    S5_SpectralTilt: float = 0.0     # linear fit log(f) vs log(amp) [dB/oct]

    def to_dict(self) -> dict:
        return {
            "S1_SubPresence": self.S1_SubPresence,
            "S2_BassWarmth": self.S2_BassWarmth,
            "S3_MidClarity": self.S3_MidClarity,
            "S4_AirBand": self.S4_AirBand,
            "S5_SpectralTilt": self.S5_SpectralTilt,
        }


@dataclass
class DynamicsDiagnosis:
    """动态维度 4 参数"""
    D1_LRA: float = 0.0              # Loudness Range per EBU 3342 [LU]
    D2_ChorusImpact: float = 0.0     # LUFS(chorus) - LUFS(verse) [LU]
    D3_MicroDynamics: float = 0.0    # mean(|momentary - short-term|) [LU]
    D4_PLR: float = 0.0              # Peak-to-Loudness Ratio [dB]

    def to_dict(self) -> dict:
        return {
            "D1_LRA": self.D1_LRA,
            "D2_ChorusImpact": self.D2_ChorusImpact,
            "D3_MicroDynamics": self.D3_MicroDynamics,
            "D4_PLR": self.D4_PLR,
        }


@dataclass
class SpaceDiagnosis:
    """空间维度 4 参数"""
    SP1_Correlation: float = 0.0     # mean phase correlation 100-8000Hz [0-1]
    SP2_ForeBackSep: float = 0.0     # M energy / S energy (midband) [dB]
    SP3_RT60Consist: float = 0.0     # std(RT60 per octave band) [s]
    SP4_WidthHealth: bool = True     # corr(2k-8k) > 0 AND mono compatible

    def to_dict(self) -> dict:
        return {
            "SP1_Correlation": self.SP1_Correlation,
            "SP2_ForeBackSep": self.SP2_ForeBackSep,
            "SP3_RT60Consist": self.SP3_RT60Consist,
            "SP4_WidthHealth": self.SP4_WidthHealth,
        }


@dataclass
class LayersDiagnosis:
    """层级维度 4 参数"""
    L1_VocalSNR: float = 0.0         # RMS(1-4kHz) / RMS(background same band) [dB]
    L2_BassClarity: float = 0.0      # 1 - entropy(normalized 20-250Hz) [0-1]
    L3_DrumDetect: float = 0.0       # transient detection rate [0-1]
    L4_LayerCount: int = 3           # 主观评分 [1-6]

    def to_dict(self) -> dict:
        return {
            "L1_VocalSNR": self.L1_VocalSNR,
            "L2_BassClarity": self.L2_BassClarity,
            "L3_DrumDetect": self.L3_DrumDetect,
            "L4_LayerCount": self.L4_LayerCount,
        }


@dataclass
class EmotionDiagnosis:
    """情绪维度 4 参数"""
    E1_Direction: int = 5            # 情绪方向明确度 [1-10]
    E2_Richness: int = 5             # 情绪层次丰富度 [1-10]
    E3_FatigueRisk: float = 0.0      # (roughness × LUFS) / max(LRA,0.1)
    E4_SectionCont: float = 0.0      # 1 - mean(cosine_distance between sections) [0-1]

    def to_dict(self) -> dict:
        return {
            "E1_Direction": self.E1_Direction,
            "E2_Richness": self.E2_Richness,
            "E3_FatigueRisk": self.E3_FatigueRisk,
            "E4_SectionCont": self.E4_SectionCont,
        }


@dataclass
class WaveStateDiagnosis:
    """五维波场诊断状态 — 完整 18 参数 (SPEC §2.2)"""
    Spectrum: SpectrumDiagnosis = field(default_factory=SpectrumDiagnosis)
    Dynamics: DynamicsDiagnosis = field(default_factory=DynamicsDiagnosis)
    Space: SpaceDiagnosis = field(default_factory=SpaceDiagnosis)
    Layers: LayersDiagnosis = field(default_factory=LayersDiagnosis)
    Emotion: EmotionDiagnosis = field(default_factory=EmotionDiagnosis)
    audio_path: str = ""
    duration_s: float = 0.0
    sample_rate: int = 44100
    timestamp: datetime = field(default_factory=datetime.now)

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
        }

    def get_auto_params(self) -> dict[str, float]:
        """提取全部 14 个自动测量参数"""
        return {
            "S1_SubPresence": self.Spectrum.S1_SubPresence,
            "S2_BassWarmth": self.Spectrum.S2_BassWarmth,
            "S3_MidClarity": self.Spectrum.S3_MidClarity,
            "S4_AirBand": self.Spectrum.S4_AirBand,
            "S5_SpectralTilt": self.Spectrum.S5_SpectralTilt,
            "D1_LRA": self.Dynamics.D1_LRA,
            "D2_ChorusImpact": self.Dynamics.D2_ChorusImpact,
            "D3_MicroDynamics": self.Dynamics.D3_MicroDynamics,
            "D4_PLR": self.Dynamics.D4_PLR,
            "SP1_Correlation": self.Space.SP1_Correlation,
            "SP2_ForeBackSep": self.Space.SP2_ForeBackSep,
            "SP3_RT60Consist": self.Space.SP3_RT60Consist,
            "L3_DrumDetect": self.Layers.L3_DrumDetect,
            "E3_FatigueRisk": self.Emotion.E3_FatigueRisk,
            "E4_SectionCont": self.Emotion.E4_SectionCont,
        }

    def is_complete(self) -> bool:
        """检查 14 自动参数是否全部有效（非 NaN, 非 Inf）"""
        import math
        for name, val in self.get_auto_params().items():
            if val is None or math.isnan(val) or math.isinf(val):
                return False
        return True
