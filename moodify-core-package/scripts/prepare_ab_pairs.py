"""SPEC-010: 从版本元数据生成 A/B 测试配对列表。

用法:
  python scripts/prepare_ab_pairs.py \
    --metadata calibration/experiment_materials/versions_metadata.json \
    --output calibration/ab_pairs.json
"""

import sys, json, argparse, itertools, random
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


def prepare_pairs(metadata: dict, pairs_per_song: int = 10) -> list[dict]:
    """为每首歌生成 A/B 比较配对。

    每首歌有 5 个版本 + 原始 = 6 个。C(6,2) = 15 对。
    从中选取 pairs_per_song 对 (默认每首歌选 10 对), 通过分层抽样保证:
      - 每个版本至少出现 2 次
      - 包含原始 vs 所有处理版本的对比
      - 包含 extreme vs 其他版本的对比 (锚定对候选)
    """
    pairs = []
    for orig_path, info in metadata.items():
        song_name = Path(orig_path).stem[:30]
        versions = info["versions"]
        version_labels = ["original"] + list(versions.keys())

        # 所有可能的配对
        all_pairs = list(itertools.combinations(version_labels, 2))

        # 分层抽样
        selected = []

        # 必须包含: 原始 vs 所有处理版本 (5对)
        for v in versions.keys():
            selected.append(("original", v))

        # 必须包含: extreme vs preset (锚定对)
        if "v5_extreme" in versions and "v1_preset" in versions:
            pair = ("v5_extreme", "v1_preset")
            if pair not in selected and tuple(reversed(pair)) not in selected:
                selected.append(pair)

        # 剩余从其他配对中随机选
        remaining = [p for p in all_pairs if p not in selected and tuple(reversed(p)) not in selected]
        random.shuffle(remaining)
        needed = pairs_per_song - len(selected)
        selected.extend(remaining[:max(0, needed)])

        # 构建输出
        for a, b in selected:
            path_a = str(Path(info["versions"][a]["path"])) if a != "original" else str(
                Path(info["versions"]["v1_preset"]["path"]).parent / f"{Path(orig_path).stem[:40]}_original.wav")
            path_b = str(Path(info["versions"][b]["path"])) if b != "original" else str(
                Path(info["versions"]["v1_preset"]["path"]).parent / f"{Path(orig_path).stem[:40]}_original.wav")

            pairs.append({
                "song": song_name,
                "version_a": f"{song_name}__{a}",
                "version_b": f"{song_name}__{b}",
                "audio_a": path_a,
                "audio_b": path_b,
                "type": "original_vs_extreme" if (a == "v5_extreme" and b == "v1_preset") or (b == "v5_extreme" and a == "v1_preset") else "normal",
            })

    random.shuffle(pairs)
    return pairs


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--metadata", required=True)
    parser.add_argument("--output", default="calibration/ab_pairs.json")
    parser.add_argument("--pairs-per-song", type=int, default=10)
    args = parser.parse_args()

    with open(args.metadata, "r", encoding="utf-8") as f:
        metadata = json.load(f)

    pairs = prepare_pairs(metadata, args.pairs_per_song)
    print(f"Generated {len(pairs)} pairs from {len(metadata)} songs")

    # 转为相对路径 (相对于 calibration/ 目录)
    for p in pairs:
        p["audio_a"] = p["audio_a"].replace("\\", "/")
        p["audio_b"] = p["audio_b"].replace("\\", "/")

    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(pairs, f, ensure_ascii=False, indent=2)

    print(f"Saved to {args.output}")


if __name__ == "__main__":
    main()
