"""
mpl_library.py — Moodify Parameter Library (SPEC §17)
=======================================================
三维索引: parameter_type × emotion_target × song_type
支持查询 (含回退链) + 贝叶斯更新 (N >= 20)

回退策略 (§17.3):
  1. 精确匹配 parameter + emotion + song_type
  2. song_type="*" 通配
  3. 同情绪大类匹配
  4. 全局默认值 (来自 GA 温柔觉醒)
"""

import json
import math
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class MPLEntry:
    """MPL 单条目 (§17.2)"""
    parameter: str
    emotion_target: str
    song_type: str = "*"

    best_range_min: float = 0.0
    best_range_max: float = 1.0
    recommendation: float = 0.5
    safety_boundary: float = 1.0
    risk_zone_below: float = -999.0
    risk_zone_above: float = 999.0
    unit: str = ""

    verified_count: int = 0
    version: str = "1.0"
    last_updated: str = ""
    evidence_sources: list[dict] = field(default_factory=list)

    def __post_init__(self):
        if not self.last_updated:
            self.last_updated = datetime.now().strftime("%Y-%m-%d")

    def to_dict(self) -> dict:
        return {
            "parameter": self.parameter,
            "emotion_target": self.emotion_target,
            "song_type": self.song_type,
            "best_range": {"min": self.best_range_min, "max": self.best_range_max, "unit": self.unit},
            "recommendation": self.recommendation,
            "safety_boundary": self.safety_boundary,
            "risk_zone": {"below": self.risk_zone_below, "above": self.risk_zone_above},
            "verified_count": self.verified_count,
            "version": self.version,
            "last_updated": self.last_updated,
            "evidence_sources": self.evidence_sources,
        }

    def confidence_level(self) -> str:
        if self.verified_count >= 50:
            return "L5-充分验证"
        elif self.verified_count >= 20:
            return "L4-可靠"
        elif self.verified_count >= 10:
            return "L3-初步"
        elif self.verified_count > 0:
            return "L2-探索"
        return "L1-默认"


# 情绪大类映射
EMOTION_CLASSES = {
    "gentle_awakening": "gentle",
    "healing_warmth": "gentle",
    "sacred_ethereal": "sacred",
    "urban_danger": "urban",
    "dark_romantic": "dark",
    "wasteland_mechanical": "wasteland",
    "lonely_whitespace": "lonely",
    "cinematic": "cinematic",
}

# 参数类型定义
PARAMETER_TYPES = [
    "eq.low_shelf", "eq.peak_vocal", "eq.high_shelf",
    "comp.ratio", "comp.attack", "comp.release", "comp.threshold",
    "reverb.t60", "reverb.dry_wet", "reverb.width",
    "harmonic.drive", "stereo.width",
]

# P-key -> MPL parameter type mapping
PARAM_KEY_MAP = {
    "P02_vocal_presence_gain": "eq.peak_vocal",
    "P05_proximity_low_gain": "eq.low_shelf",
    "P15_high_shelf_gain": "eq.high_shelf",
    "P06_compression_ratio": "comp.ratio",
    "P07_compression_attack": "comp.attack",
    "P08_compression_release": "comp.release",
    "P09_compression_threshold": "comp.threshold",
    "P10_reverb_t60": "reverb.t60",
    "P11_reverb_dry_wet": "reverb.dry_wet",
    "P12_reverb_width": "reverb.width",
    "P13_harmonic_drive": "harmonic.drive",
}


class MoodifyParameterLibrary:
    """三维参数库 (§17)"""

    def __init__(self, data_dir: str = "data/mpl"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self._entries: dict[str, dict[str, dict[str, MPLEntry]]] = {}
        self._load_all()

    def _load_all(self):
        mpl_file = self.data_dir / "mpl_database.json"
        if mpl_file.exists():
            with open(mpl_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            for entry_data in data.get("entries", []):
                entry = MPLEntry(**entry_data)
                self._add_to_index(entry)

    def _save_all(self):
        entries = []
        for pd in self._entries.values():
            for ed in pd.values():
                for entry in ed.values():
                    entries.append(entry.to_dict())
        with open(self.data_dir / "mpl_database.json", "w", encoding="utf-8") as f:
            json.dump({"entries": entries, "updated_at": datetime.now().isoformat()},
                      f, ensure_ascii=False, indent=2)

    def _add_to_index(self, entry: MPLEntry):
        self._entries.setdefault(entry.parameter, {}).setdefault(
            entry.emotion_target, {})[entry.song_type] = entry

    def query(self,
              parameter: str,
              emotion_target: str,
              song_type: str | None = None) -> Optional[MPLEntry]:
        """精确查询 + 四级回退"""
        st = song_type or "*"

        # 1. 精确匹配
        e = self._get(parameter, emotion_target, st)
        if e:
            return e

        # 2. song_type 通配
        e = self._get(parameter, emotion_target, "*")
        if e:
            return e

        # 3. 同情绪大类
        target_class = EMOTION_CLASSES.get(emotion_target, emotion_target)
        for emo in self._entries.get(parameter, {}):
            if EMOTION_CLASSES.get(emo, emo) == target_class:
                for entry in self._entries[parameter][emo].values():
                    return entry

        # 4. 全局默认
        return self._get_default(parameter)

    def _get(self, param, emotion, song) -> Optional[MPLEntry]:
        try:
            return self._entries[param][emotion][song]
        except KeyError:
            return None

    def _get_default(self, param: str) -> Optional[MPLEntry]:
        from moodify.knowledge.craft_chains import CRAFT_CHAINS_15PARAMS
        ga = CRAFT_CHAINS_15PARAMS.get("GA", {})

        # Reverse map: mpl type -> P-key
        reverse_map = {v: k for k, v in PARAM_KEY_MAP.items()}
        p_key = reverse_map.get(param)
        if p_key and p_key in ga:
            p = ga[p_key]
            return MPLEntry(
                parameter=param, emotion_target="*", song_type="*",
                best_range_min=p["min"], best_range_max=p["max"],
                recommendation=p["rec"],
                safety_boundary=p.get("max", 1) * 2,
                risk_zone_below=p.get("min", -1) - 2,
                risk_zone_above=p.get("max", 1) + 2,
                unit=p.get("unit", ""),
            )
        return None

    def search(self, emotion_target: str,
               song_type: str | None = None) -> dict[str, MPLEntry]:
        """返回指定情绪和歌曲类型的全部参数条目"""
        result = {}
        for pt in PARAMETER_TYPES:
            entry = self.query(pt, emotion_target, song_type)
            if entry:
                result[pt] = entry
        return result

    def update(self, parameter: str, emotion_target: str,
               song_type: str, observed_value: float,
               source: dict | None = None) -> MPLEntry:
        """贝叶斯更新 (§17.4) — N >= 20 时自动调整 recommendation"""
        entry = self.query(parameter, emotion_target, song_type)
        if not entry:
            entry = self._get_default(parameter)
            if not entry:
                entry = MPLEntry(parameter=parameter, emotion_target=emotion_target,
                                 song_type=song_type)
            entry.emotion_target = emotion_target
            entry.song_type = song_type

        if source:
            entry.evidence_sources.append(source)

        entry.verified_count += 1
        n = entry.verified_count

        if n >= 20:
            alpha = 10.0
            prior = entry.recommendation
            posterior = (alpha * prior + observed_value) / (alpha + 1)
            entry.recommendation = round(posterior, 2)
            entry.best_range_min = round(entry.recommendation * 0.7, 2)
            entry.best_range_max = round(entry.recommendation * 1.3, 2)
            parts = entry.version.split(".")
            entry.version = f"{parts[0]}.{int(parts[1]) + 1}"

        entry.last_updated = datetime.now().strftime("%Y-%m-%d")
        self._add_to_index(entry)
        self._save_all()
        return entry

    def get_confidence_summary(self) -> dict:
        """获取整体可信度概况"""
        summary = {"L5": 0, "L4": 0, "L3": 0, "L2": 0, "L1": 0, "total": 0}
        for pd in self._entries.values():
            for ed in pd.values():
                for entry in ed.values():
                    lvl = entry.confidence_level().split("-")[0]
                    summary[lvl] += 1
                    summary["total"] += 1
        return summary

    def get_emotion_summary(self) -> dict:
        """按情绪汇总"""
        summary = {}
        for pd in self._entries.values():
            for emo, ed in pd.items():
                if emo not in summary:
                    summary[emo] = {"count": 0, "avg_verified": 0, "max_verified": 0}
                for entry in ed.values():
                    summary[emo]["count"] += 1
                    summary[emo]["avg_verified"] += entry.verified_count
                    summary[emo]["max_verified"] = max(summary[emo]["max_verified"],
                                                        entry.verified_count)
        for emo in summary:
            cnt = summary[emo]["count"]
            if cnt > 0:
                summary[emo]["avg_verified"] = round(summary[emo]["avg_verified"] / cnt, 1)
        return summary


def initialize_mpl_from_craft_cards(data_dir: str = "data/mpl") -> MoodifyParameterLibrary:
    """从 8 张工艺卡初始化 MPL 数据库 (120 基础条目)"""
    from moodify.knowledge.craft_chains import CRAFT_CHAINS_15PARAMS, PARAM_KEYS
    from moodify.knowledge.emotion_targets import EMOTION_TARGETS_V2

    mpl = MoodifyParameterLibrary(data_dir=data_dir)

    for emotion_key, target in EMOTION_TARGETS_V2.items():
        code = target["code"]
        chain = CRAFT_CHAINS_15PARAMS.get(code)
        if not chain:
            continue

        for p_key, mpl_type in PARAM_KEY_MAP.items():
            if p_key in chain:
                p = chain[p_key]
                entry = MPLEntry(
                    parameter=mpl_type,
                    emotion_target=emotion_key,
                    song_type="*",
                    best_range_min=p["min"],
                    best_range_max=p["max"],
                    recommendation=p["rec"],
                    safety_boundary=p.get("max", 1.0) * 2,
                    risk_zone_below=p.get("min", -1.0) - 2,
                    risk_zone_above=p.get("max", 1.0) + 2,
                    unit=p.get("unit", ""),
                    version="1.0",
                )
                mpl._add_to_index(entry)

    mpl._save_all()
    return mpl
