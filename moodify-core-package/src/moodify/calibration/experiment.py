"""校准实验 — 生成多版本 → AI 排序 → Spearman ρ → 冲突记录。

用法:
  python -m moodify.calibration.experiment \
    --songs "song1.wav,song2.wav,song3.wav" \
    --emotions "GA,DR"

输出 outputs/calibration/report.json
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from datetime import datetime

import numpy as np
import soundfile


@dataclass
class VersionResult:
    version_id: str
    params: dict
    proxy_score: float
    strength_vector: dict
    output_path: str

@dataclass
class SongCalibration:
    song_name: str
    emotion: str
    discriminable: bool
    proxy_ranks: list[int]
    ai_ranks: list[int]
    ai_distances: list[float]
    spearman_rho: float
    conflicts: list[dict] = field(default_factory=list)
    versions: list[VersionResult] = field(default_factory=list)

@dataclass
class CalibrationReport:
    date: str
    listener: str
    aggregate_spearman_rho: float
    groups: list[dict]
    summary: dict


def run_calibration(
    songs: list[str],
    emotions: list[str],
    output_dir: str = "outputs/calibration",
    listener = None,
    n_versions: int = 5,
) -> CalibrationReport:
    """校准实验主入口。

    Args:
        songs: 输入音频路径列表
        emotions: 情绪代码列表 ["GA", "DR"]
        output_dir: 输出目录
        listener: AudioListener 实例, 默认 DiagnosisListener
        n_versions: 每首歌生成的版本数

    Returns:
        CalibrationReport
    """
    from moodify.calibration.listener import DiagnosisListener

    if listener is None:
        listener = DiagnosisListener()

    os.makedirs(output_dir, exist_ok=True)
    all_groups = []

    for emotion in emotions:
        for song_path in songs:
            song_name = os.path.splitext(os.path.basename(song_path))[0]
            print(f"\n{'='*60}")
            print(f"  {song_name}  →  {emotion}")
            print(f"{'='*60}")

            try:
                group = _calibrate_one(song_path, emotion, listener,
                                       output_dir, n_versions)
                all_groups.append(group)
                print(f"  discriminable: {group.discriminable}")
                print(f"  Spearman ρ:    {group.spearman_rho:.3f}")
                if group.conflicts:
                    print(f"  conflicts:     {len(group.conflicts)}")
                    for c in group.conflicts:
                        print(f"    - {c['version_id']}: proxy_rank={c['proxy_rank']}, ai_rank={c['ai_rank']}")
            except Exception as e:
                import traceback
                traceback.print_exc()
                print(f"  FAILED: {e}")

    # 聚合
    rho_values = [g.spearman_rho for g in all_groups if not np.isnan(g.spearman_rho)]
    aggregate_rho = float(np.mean(rho_values)) if rho_values else 0.0

    discriminable_count = sum(1 for g in all_groups if g.discriminable)
    high_rho_count = sum(1 for r in rho_values if r >= 0.7)
    total_conflicts = sum(len(g.conflicts) for g in all_groups)

    report = CalibrationReport(
        date=datetime.now().isoformat(),
        listener=listener.name(),
        aggregate_spearman_rho=round(aggregate_rho, 3),
        groups=[_group_to_dict(g) for g in all_groups],
        summary={
            "n_groups": len(all_groups),
            "n_discriminable": discriminable_count,
            "discriminable_ratio": round(discriminable_count / max(1, len(all_groups)), 2),
            "aggregate_rho": round(aggregate_rho, 3),
            "high_rho_groups": high_rho_count,
            "total_conflicts": total_conflicts,
            "verdict": _verdict(aggregate_rho),
        },
    )

    report_path = os.path.join(output_dir, "report.json")
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(report.__dict__ if hasattr(report, '__dict__') else
                  {"date": report.date, "listener": report.listener,
                   "aggregate_spearman_rho": report.aggregate_spearman_rho,
                   "groups": report.groups, "summary": report.summary},
                  f, ensure_ascii=False, indent=2, default=str)
    print(f"\n  Report → {report_path}")
    print(f"  Aggregate Spearman ρ: {aggregate_rho:.3f}  [{_verdict(aggregate_rho)}]")

    return report


def _calibrate_one(
    song_path: str,
    emotion: str,
    listener,
    output_dir: str,
    n_versions: int,
) -> SongCalibration:
    """对一首歌 + 一个情绪做校准。"""
    from moodify.knowledge.craft_chains import get_recommended_params
    from moodify.knowledge.emotion_targets import resolve_emotion, KEY_TO_CODE

    # 解析情绪
    emotion_key = resolve_emotion(emotion)
    emotion_code = KEY_TO_CODE.get(emotion_key, emotion)

    # 加载音频
    audio, sr = soundfile.read(song_path)
    audio = audio.astype(np.float32)

    # Phase 1: 诊断 + 搜索
    from moodify.diagnosis.engine import DiagnosisEngine
    from moodify.optimizer.search import search_optimal_strengths, strength_to_params

    engine = DiagnosisEngine()
    ws_diag = engine.diagnose_quick(song_path)

    results = search_optimal_strengths(ws_diag, emotion, top_k=n_versions - 2)

    # 构造版本: 覆盖完整的强度范围以保证多样性
    chain_order = ["spectrum", "dynamic", "space", "layer", "master"]
    versions = []

    # v0: light — 所有维度轻度处理
    light_strength = {d: 0.15 for d in chain_order}
    light_params = strength_to_params(light_strength, emotion_code)
    versions.append(("light", light_params, light_strength, 0.0))

    # v1: preset — 推荐值基线
    preset_params = get_recommended_params(emotion_code)
    versions.append(("preset", preset_params,
                     {d: 0.5 for d in chain_order}, 0.0))

    # v2: search top-1 — 代理最优
    if results:
        s, p, score = results[0]
        versions.append(("search_top1", p, s, score))
    else:
        versions.append(("search_top1", preset_params,
                         {d: 0.5 for d in chain_order}, 0.0))

    # v3: aggressive — 所有维度重度处理
    aggressive_strength = {d: 0.85 for d in chain_order}
    aggressive_params = strength_to_params(aggressive_strength, emotion_code)
    versions.append(("aggressive", aggressive_params, aggressive_strength, 0.0))

    # v4: cross-emotion — 跨情绪参数 (极端测试代理边界)
    cross_code = _pick_cross_emotion(emotion_code)
    cross_params = get_recommended_params(cross_code)
    cross_strength = {d: 0.85 for d in chain_order}
    versions.append((f"cross_{cross_code}", cross_params, cross_strength, 0.0))

    # Phase 3: 对每个版本跑 DSP
    from moodify.processing.spectral_chain import SpectralDSPChain
    chain = SpectralDSPChain()

    version_results = []
    processed_audios = []
    song_base = os.path.splitext(os.path.basename(song_path))[0]
    version_dir = os.path.join(output_dir, f"{song_base}_{emotion_code}")
    os.makedirs(version_dir, exist_ok=True)

    for idx, (vid, params, strength, proxy) in enumerate(versions):
        try:
            processed = chain.process(audio, sr, params)
        except Exception:
            processed = audio

        out_path = os.path.join(version_dir, f"v{idx}_{vid}.wav")
        soundfile.write(out_path, processed, sr)

        version_results.append(VersionResult(
            version_id=vid, params=params,
            proxy_score=float(proxy), strength_vector=strength,
            output_path=out_path,
        ))
        processed_audios.append(processed)

    # Layer 1: 可辨性
    discriminable = listener.is_discriminable(processed_audios, sr)

    if not discriminable:
        return SongCalibration(
            song_name=os.path.basename(song_path),
            emotion=emotion_code,
            discriminable=False,
            proxy_ranks=list(range(1, len(versions) + 1)),
            ai_ranks=list(range(1, len(versions) + 1)),
            ai_distances=[0.0] * len(versions),
            spearman_rho=float('nan'),
            versions=version_results,
        )

    # Layer 2: AI 排序
    ai_ranks, ai_distances, _ = listener.rank_versions(
        processed_audios, sr, emotion_code
    )

    # proxy 排序: 按 proxy_score 降序
    proxy_scores = [v.proxy_score for v in version_results]
    proxy_order = np.argsort([-s for s in proxy_scores])  # 降序
    proxy_ranks = np.zeros(len(version_results), dtype=int)
    for rank_pos, idx in enumerate(proxy_order):
        proxy_ranks[idx] = rank_pos + 1
    proxy_ranks = proxy_ranks.tolist()

    # Layer 3: Spearman ρ + 冲突检测
    from scipy.stats import spearmanr
    try:
        rho_result = spearmanr(proxy_ranks, ai_ranks)
        rho = float(rho_result.statistic)
    except Exception:
        rho = float('nan')

    conflicts = []
    for i in range(len(version_results)):
        rank_diff = abs(proxy_ranks[i] - ai_ranks[i])
        if rank_diff >= 2:
            conflicts.append({
                "version_id": version_results[i].version_id,
                "proxy_rank": proxy_ranks[i],
                "ai_rank": ai_ranks[i],
                "rank_diff": rank_diff,
                "proxy_score": version_results[i].proxy_score,
                "ai_distance": round(ai_distances[i], 4),
            })

    return SongCalibration(
        song_name=os.path.basename(song_path),
        emotion=emotion_code,
        discriminable=True,
        proxy_ranks=proxy_ranks,
        ai_ranks=ai_ranks,
        ai_distances=[round(d, 4) for d in ai_distances],
        spearman_rho=round(rho, 3) if not np.isnan(rho) else float('nan'),
        conflicts=conflicts,
        versions=version_results,
    )


def _group_to_dict(g: SongCalibration) -> dict:
    return {
        "song": g.song_name,
        "emotion": g.emotion,
        "discriminable": g.discriminable,
        "spearman_rho": g.spearman_rho,
        "proxy_ranks": g.proxy_ranks,
        "ai_ranks": g.ai_ranks,
        "conflicts": g.conflicts,
        "versions": [
            {"id": v.version_id, "proxy_score": v.proxy_score,
             "output": v.output_path}
            for v in g.versions
        ],
    }


def _verdict(rho: float) -> str:
    if np.isnan(rho):
        return "NO_DATA"
    if rho >= 0.7:
        return "PROXY_RELIABLE — 代理可用于精排"
    if rho >= 0.5:
        return "PROXY_USABLE — 代理用于粗筛, 精排需混合策略"
    return "PROXY_UNRELIABLE — 代理需重构"


def _pick_cross_emotion(emotion_code: str) -> str:
    """选择一个参数风格差异大的跨情绪对照。

    GA(温柔) ↔ WL(嚎哭): 压缩比和失真差异最大
    SE(安详) ↔ UD(不安): 混响和动态差异最大
    其他: 回退到 WL
    """
    cross_map = {"GA": "WL", "WL": "GA", "SE": "UD", "UD": "SE",
                 "LW": "HL", "HL": "LW", "DR": "CN", "CN": "DR"}
    return cross_map.get(emotion_code, "WL")


# ── CLI ────────────────────────────────────────────────────

if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser(description="Moodify 代理指标校准实验")
    ap.add_argument("--songs", required=True,
                    help="逗号分隔的输入音频路径")
    ap.add_argument("--emotions", default="GA,DR",
                    help="逗号分隔的情绪代码 (默认: GA,DR)")
    ap.add_argument("--output-dir", default="outputs/calibration",
                    help="输出目录 (默认: outputs/calibration)")
    ap.add_argument("--versions", type=int, default=5,
                    help="每首歌版本数 (默认: 5)")
    args = ap.parse_args()

    songs = [s.strip() for s in args.songs.split(",")]
    emotions = [e.strip() for e in args.emotions.split(",")]

    run_calibration(songs, emotions, args.output_dir, n_versions=args.versions)
