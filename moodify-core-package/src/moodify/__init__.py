"""
Moodify Core Engine — AI 音乐情绪波场显影器
=============================================
基于情绪波工程学 150+ 篇论文的工程实现。

Sub-packages:
  moodify.diagnosis      — 五维 18 参数诊断引擎
  moodify.processing     — DSP 处理算子
  moodify.knowledge      — 情绪工艺库 + 风险模型
  moodify.orchestration  — 六阶段工作流 + 状态转移
  moodify.api            — REST API
"""

__version__ = "0.1.0"

from moodify.data_types import (
    # Diagnosis types
    WaveStateDiagnosis,
    SpectrumDiagnosis,
    DynamicsDiagnosis,
    SpaceDiagnosis,
    LayersDiagnosis,
    EmotionDiagnosis,
    # Process types
    WaveState,
    SpectrumState,
    DynamicsState,
    SpaceState,
    LayersState,
    EmotionState,
    # Craft types
    CraftCard,
    CraftCardV2,
    EmotionTarget,
    # Experiment types
    AudioRecord,
    Experiment,
)

# ── MATH/PHYS Foundation 基础设施 (SPEC-011 批次 0) ──

from moodify.uncertainty import UncertaintyResult, ConfidenceLevel
from moodify.protocol import (
    MeasurementRecord,
    PROTOCOL_VERSION,
    STFT_CONFIG_STANDARD,
    STFT_CONFIG_QUICK,
)
from moodify.fingerprint import ProcessorFingerprint, compute_thd, estimate_cr_eff
from moodify.conservation import ConservationReport, audit_conservation
from moodify.icc import compute_icc
