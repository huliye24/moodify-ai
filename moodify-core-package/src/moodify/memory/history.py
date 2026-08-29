"""ProcessingHistory — 处理记录存储 + 余弦相似度检索 + 时间衰减

Schema v1 — 2026-05-29 固化。字段含义:
  diagnosis_vector: L2归一化的18参数诊断向量 (可变长但必须 ≥10)
  params: 15参数 DSP 设置 {P01_vocal_presence_freq: 4000, ...}
  strength_vector: 5D 强度 {spectrum: 0.6, dynamic: 0.5, ...}
  whs_before/after: 处理前后 WHS 健康分 [0-100]
  eds: 情绪距离改善分 [-100, 100]
  proxy_score: 搜索阶段代理预估的 EDS
  emotion_code: 2字符情绪代码 (GA/DR/WL/UD/SE/CN/NS/EX)
  emotion_name: 情绪中文名
  user_intent: 用户原始意图文本 (未实现, 空串)
  satisfied: 用户是否满意 (None=未收集)
  user_feedback: 用户反馈文本 (未实现, 空串)
  timestamp: ISO 8601 格式时间戳
  schema_version: 常数 1
"""
import json
import math
import logging
import numpy as np
from dataclasses import dataclass, asdict
from pathlib import Path
from datetime import datetime

logger = logging.getLogger(__name__)

SCHEMA_VERSION = 1
VALID_EMOTION_CODES = {"GA", "DR", "WL", "UD", "SE", "CN", "NS", "EX"}


@dataclass
class ProcessingRecord:
    diagnosis_vector: list[float]
    params: dict[str, float]
    strength_vector: dict[str, float]
    whs_before: float
    whs_after: float
    eds: float
    proxy_score: float
    emotion_code: str
    emotion_name: str
    user_intent: str
    satisfied: bool | None
    user_feedback: str
    timestamp: str
    schema_version: int = SCHEMA_VERSION


class ProcessingHistory:

    def __init__(self, storage_dir: str = "outputs"):
        self._path = Path(storage_dir) / "processing_history.jsonl"

    def save(self, record: ProcessingRecord) -> None:
        self._validate(record)
        self._path.parent.mkdir(parents=True, exist_ok=True)
        with open(self._path, "a", encoding="utf-8") as f:
            f.write(json.dumps(asdict(record), ensure_ascii=False) + "\n")

    @staticmethod
    def _validate(r: ProcessingRecord) -> None:
        """保存前校验 — 防止损坏数据进入历史。"""
        if len(r.diagnosis_vector) < 10:
            raise ValueError(f"diagnosis_vector too short: {len(r.diagnosis_vector)} < 10")
        if not (-100.0 <= r.eds <= 100.0):
            raise ValueError(f"eds out of range: {r.eds}")
        if not (0.0 <= r.whs_before <= 100.0):
            raise ValueError(f"whs_before out of range: {r.whs_before}")
        if not (0.0 <= r.whs_after <= 100.0):
            raise ValueError(f"whs_after out of range: {r.whs_after}")
        if r.emotion_code not in VALID_EMOTION_CODES:
            logger.debug(f"unknown emotion_code: {r.emotion_code}")
        if r.schema_version != SCHEMA_VERSION:
            raise ValueError(f"schema_version mismatch: {r.schema_version} != {SCHEMA_VERSION}")
        sv = r.strength_vector
        for dim in ["spectrum", "dynamic", "space", "layer", "master"]:
            if dim in sv and not (0.0 <= sv[dim] <= 1.0):
                raise ValueError(f"strength_vector.{dim} out of [0,1]: {sv[dim]}")

    def load_all(self) -> list[ProcessingRecord]:
        if not self._path.exists():
            return []
        records = []
        with open(self._path, "r", encoding="utf-8") as f:
            for line in f:
                try:
                    records.append(ProcessingRecord(**json.loads(line)))
                except Exception:
                    pass
        return records

    def find_similar(
        self, query_vector: list[float], top_k: int = 5
    ) -> list[tuple[ProcessingRecord, float]]:
        """余弦相似度 + 时间衰减。半衰期 180 天。跳过 >365 天记录。"""
        records = self.load_all()
        if not records:
            return []

        now = datetime.now()
        q = np.array(query_vector, dtype=np.float64)
        scored = []
        for r in records:
            try:
                age_days = (now - datetime.fromisoformat(r.timestamp)).days
            except Exception:
                age_days = 0
            if age_days > 365:
                continue
            v = np.array(r.diagnosis_vector, dtype=np.float64)
            cos = float(np.dot(q, v) / (np.linalg.norm(q) * np.linalg.norm(v) + 1e-8))
            time_decay = math.exp(-age_days / 180.0)
            scored.append((r, cos * time_decay))
        scored.sort(key=lambda x: x[1], reverse=True)
        return scored[:top_k]

    def count(self) -> int:
        return len(self.load_all())


def diagnosis_to_vector(diagnosis) -> list[float]:
    """WaveStateDiagnosis → L2 归一化向量。排除布尔和主观参数。"""
    d = diagnosis.to_dict()
    vec = []
    skip = {"SP4_WidthHealth", "E1_Direction", "E2_Richness"}
    for dim_name in ["Spectrum", "Dynamics", "Space", "Layers", "Emotion"]:
        for key, val in d[dim_name].items():
            if key in skip:
                continue
            vec.append(float(val) if not isinstance(val, bool) else (1.0 if val else 0.0))
    arr = np.array(vec, dtype=np.float64)
    norm = np.linalg.norm(arr)
    return (arr / norm).tolist() if norm > 1e-8 else arr.tolist()
