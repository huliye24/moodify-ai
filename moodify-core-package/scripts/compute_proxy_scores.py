"""SPEC-010: 计算所有校准版本的 EDSR_proxy 分数。

用法:
  python scripts/compute_proxy_scores.py \
    --metadata calibration/experiment_materials/versions_metadata.json \
    --output calibration/proxy_scores.json
"""

import sys
import json
import argparse
from pathlib import Path
import numpy as np

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from moodify.diagnosis.engine import DiagnosisEngine
from moodify.orchestration.state_transfer import StateTransferEngine
from moodify.knowledge.emotion_targets import get_ideal_process_vector


def compute_edsr_proxy(audio_path: str, emotion_code: str) -> float:
    """计算处理音频的 EDSR_proxy。

    使用当前 proxy_evaluate 的底层逻辑:
      - 诊断 → 5D raw vector
      - 诊断处理后的音频 → 5D processed vector
      - 计算到目标情绪理想向量的马氏距离比率
    """
    from moodify.optimizer.search import get_static_sigma_inv, _mahalanobis_distance

    engine = DiagnosisEngine()

    # 原始诊断
    ws_raw = engine.diagnose_quick(audio_path)
    ws_raw_5d = StateTransferEngine.diagnostic_to_process(ws_raw).to_array()

    target = get_ideal_process_vector(emotion_code)
    sigma_inv = get_static_sigma_inv()

    dist_before = float(_mahalanobis_distance(ws_raw_5d, target, sigma_inv))

    # 处理后诊断 — 需要原始音频来对比
    # 这里用当前版本的音频文件本身作为"处理后"
    # 实际上 proxy_evaluate 不跑真实 DSP, 这里用真实诊断来测量
    ws_after = engine.diagnose_quick(audio_path)
    ws_after_5d = StateTransferEngine.diagnostic_to_process(ws_after).to_array()

    dist_after = float(_mahalanobis_distance(ws_after_5d, target, sigma_inv))

    if dist_before > 1e-8:
        eds = 100.0 * (1.0 - dist_after / dist_before)
    else:
        eds = 100.0

    return float(np.clip(eds, -100.0, 100.0))


def compute_proxy_for_original(audio_path: str, emotion_code: str) -> float:
    """计算原始音频到目标情绪的距离 (作为 baseline)。"""
    from moodify.optimizer.search import get_static_sigma_inv, _mahalanobis_distance

    engine = DiagnosisEngine()
    ws = engine.diagnose_quick(audio_path)
    ws_5d = StateTransferEngine.diagnostic_to_process(ws).to_array()

    target = get_ideal_process_vector(emotion_code)
    sigma_inv = get_static_sigma_inv()

    dist = float(_mahalanobis_distance(ws_5d, target, sigma_inv))
    # 原始音频没有 EDS (没有处理), 返回的是马氏距离
    return float(dist)


def compute_whs(audio_path: str, emotion_code: str) -> float:
    """计算 WHS 分数。"""
    from moodify.diagnosis.defect_classifier import DefectClassifier
    from moodify.diagnosis.health_scorer import HealthScorer

    engine = DiagnosisEngine()
    ws = engine.diagnose_quick(audio_path)
    classifier = DefectClassifier()
    scorer = HealthScorer()
    defects = classifier.classify(ws, emotion_code)
    return float(scorer.compute_whs(ws, defects)["WHS"])


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--metadata", required=True)
    parser.add_argument("--output", default="calibration/proxy_scores.json")
    args = parser.parse_args()

    with open(args.metadata, "r", encoding="utf-8") as f:
        metadata = json.load(f)

    scores = {}
    total = sum(len(info["versions"]) for info in metadata.values())

    i = 0
    for orig_path, info in metadata.items():
        emotion_code = info["emotion"]
        song_name = Path(orig_path).stem[:30]

        # 原始音频指标
        orig_file = Path(info["versions"]["v1_preset"]["path"]).parent / f"{Path(orig_path).stem[:40]}_original.wav"
        if orig_file.exists():
            scores[f"{song_name}__original"] = {
                "type": "original",
                "emotion": emotion_code,
                "whs": compute_whs(str(orig_file), emotion_code),
                "mahalanobis_dist": compute_proxy_for_original(str(orig_file), emotion_code),
            }

        for version_label, version_info in info["versions"].items():
            i += 1
            key = f"{song_name}__{version_label}"
            path = version_info["path"]
            print(f"[{i}/{total}] {key}")

            try:
                whs = compute_whs(path, emotion_code)
                mah_dist = compute_proxy_for_original(path, emotion_code)
                scores[key] = {
                    "type": version_label,
                    "emotion": emotion_code,
                    "path": path,
                    "whs": whs,
                    "mahalanobis_dist": mah_dist,
                    "params": version_info.get("params", {}),
                }
            except Exception as e:
                print(f"  ERROR: {e}")
                scores[key] = {"error": str(e)}

    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(scores, f, ensure_ascii=False, indent=2)

    print(f"\nScores saved to {args.output}")


if __name__ == "__main__":
    main()
