"""SPEC-010: 生成 EDSR 校准实验的多版本音频素材。

每首歌生成 5 个版本:
  V1: preset — 工艺卡推荐值 (baseline)
  V2: search_top1 — 5D搜索最优
  V3: search_diverse — 搜索中与V2不同的另一个候选
  V4: llm — DeepSeek推荐 (API可用时) 或 search_top2
  V5: extreme — 边界测试 (P15 +3dB, P02 +2dB)

用法:
  python scripts/generate_calibration_versions.py \
    --audio_dir 07Music/albums/CAD-ALB-001_Cadeau001_UnwrittenSelf/CAD-ALB-001_RELEASE_SELECTION_RAW/ \
    --output_dir calibration/experiment_materials/ \
    --emotions GA SE CN LW HL
"""

import os, sys, json, time, argparse
from pathlib import Path
import numpy as np
import soundfile as sf

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from moodify.diagnosis.engine import DiagnosisEngine
from moodify.knowledge.craft_chains import get_recommended_params
from moodify.knowledge.emotion_targets import resolve_emotion, KEY_TO_CODE, EMOTION_TARGETS_V2
from moodify.processing.spectral_chain import SpectralDSPChain


def generate_versions(audio_path: str, emotion_code: str, output_dir: str):
    """为单首歌生成 5 个处理版本。"""
    audio, sr = sf.read(audio_path)
    audio = audio.astype(np.float32)
    if audio.ndim == 1:
        audio = np.column_stack([audio, audio])

    engine = DiagnosisEngine()
    ws = engine.diagnose_quick(audio_path)

    song_name = Path(audio_path).stem[:40]
    song_dir = Path(output_dir) / song_name
    song_dir.mkdir(parents=True, exist_ok=True)
    chain = SpectralDSPChain()

    versions = {}

    # V1: preset baseline
    t0 = time.perf_counter()
    v1_params = get_recommended_params(emotion_code)
    v1_audio = chain.process(audio, sr, v1_params)
    v1_path = song_dir / f"{song_name}_v1_preset_{emotion_code}.wav"
    sf.write(str(v1_path), v1_audio, sr, subtype='PCM_16')
    versions["v1_preset"] = {"params": v1_params, "path": str(v1_path),
                              "elapsed_ms": (time.perf_counter() - t0) * 1000}

    # V2-V4: search + LLM
    from moodify.optimizer.search import search_optimal_strengths
    results = search_optimal_strengths(ws, emotion_code, top_k=4, n_samples=2000)

    for label, idx in [("v2_search_top1", 0), ("v3_search_diverse", 2)]:
        if idx < len(results):
            t0 = time.perf_counter()
            params = results[idx][1]
            ver_audio = chain.process(audio, sr, params)
            ver_path = song_dir / f"{song_name}_{label}_{emotion_code}.wav"
            sf.write(str(ver_path), ver_audio, sr, subtype='PCM_16')
            versions[label] = {"params": params, "path": str(ver_path),
                               "proxy_score": results[idx][2],
                               "elapsed_ms": (time.perf_counter() - t0) * 1000}

    # V4: LLM or search_top2
    t0 = time.perf_counter()
    v4_params = None
    try:
        from moodify.llm.client import DeepSeekClient
        from moodify.llm.prompt_assembler import assemble_rag_prompt
        llm = DeepSeekClient()
        if llm.available:
            from moodify.diagnosis.defect_classifier import DefectClassifier
            classifier = DefectClassifier()
            defects = classifier.classify(ws, emotion_code)
            defects_list = [{"parameter": d.parameter, "severity": d.severity} for d in defects]
            emotion_name = EMOTION_TARGETS_V2.get(emotion_code, {}).get("name_zh", emotion_code)
            prompt = assemble_rag_prompt(ws.to_dict(), defects_list, emotion_name, "", [])
            result = llm.recommend_params(prompt)
            if result and "parameters" in result:
                v4_params = {p["param_name"]: p["value"] for p in result["parameters"]}
    except Exception:
        pass

    if v4_params is None and len(results) >= 3:
        v4_params = results[1][1]  # search_top2 as fallback

    if v4_params:
        v4_audio = chain.process(audio, sr, v4_params)
        v4_path = song_dir / f"{song_name}_v4_llm_{emotion_code}.wav"
        sf.write(str(v4_path), v4_audio, sr, subtype='PCM_16')
        versions["v4_llm"] = {"params": v4_params, "path": str(v4_path),
                              "elapsed_ms": (time.perf_counter() - t0) * 1000}

    # V5: extreme — 测试代理指标边界
    t0 = time.perf_counter()
    v5_params = dict(v1_params)
    v5_params["P15_high_shelf_gain"] = v5_params.get("P15_high_shelf_gain", 0) + 3.0
    v5_params["P02_vocal_presence_gain"] = v5_params.get("P02_vocal_presence_gain", 0) + 2.0
    v5_audio = chain.process(audio, sr, v5_params)
    v5_path = song_dir / f"{song_name}_v5_extreme_{emotion_code}.wav"
    sf.write(str(v5_path), v5_audio, sr, subtype='PCM_16')
    versions["v5_extreme"] = {"params": v5_params, "path": str(v5_path),
                              "elapsed_ms": (time.perf_counter() - t0) * 1000}

    # 保存原始音频供对比
    orig_path = song_dir / f"{song_name}_original.wav"
    sf.write(str(orig_path), audio, sr, subtype='PCM_16')

    return versions


def main():
    parser = argparse.ArgumentParser(description="生成 EDSR 校准实验的多版本音频")
    parser.add_argument("--audio_dir", required=True)
    parser.add_argument("--output_dir", default="calibration/experiment_materials")
    parser.add_argument("--emotions", nargs="+", default=["GA", "SE", "CN", "LW", "HL"])
    parser.add_argument("--limit", type=int, default=5, help="最多处理几首歌")
    args = parser.parse_args()

    wav_files = sorted(Path(args.audio_dir).glob("*.wav"))[:args.limit]
    if not wav_files:
        print(f"No .wav files found in {args.audio_dir}")
        sys.exit(1)

    print(f"Found {len(wav_files)} WAV files")
    print(f"Emotions: {args.emotions}")
    print(f"Total versions: {len(wav_files)} songs × {len(args.emotions)} emotions × 5 versions = {len(wav_files) * len(args.emotions) * 5}")
    print()

    all_versions = {}
    for wav_path in wav_files:
        emotion_code = args.emotions[hash(wav_path.name) % len(args.emotions)]
        print(f"Processing: {wav_path.name} → {emotion_code}")
        versions = generate_versions(str(wav_path), emotion_code, args.output_dir)
        all_versions[str(wav_path)] = {"emotion": emotion_code, "versions": versions}
        print(f"  Generated {len(versions)} versions")

    # 保存元数据
    meta_path = Path(args.output_dir) / "versions_metadata.json"
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(all_versions, f, ensure_ascii=False, indent=2, default=str)

    total = sum(len(v["versions"]) for v in all_versions.values())
    print(f"\nDone. {total} versions saved to {args.output_dir}")
    print(f"Metadata: {meta_path}")


if __name__ == "__main__":
    main()
