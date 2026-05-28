"""ProcessingHistory — 处理记录存储 + 余弦相似度检索 + 时间衰减"""
import json
import math
import numpy as np
from dataclasses import dataclass, asdict
from pathlib import Path
from datetime import datetime


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


class ProcessingHistory:

    def __init__(self, storage_dir: str = "outputs"):
        self._path = Path(storage_dir) / "processing_history.jsonl"

    def save(self, record: ProcessingRecord) -> None:
        self._path.parent.mkdir(parents=True, exist_ok=True)
        with open(self._path, "a", encoding="utf-8") as f:
            f.write(json.dumps(asdict(record), ensure_ascii=False) + "\n")

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
