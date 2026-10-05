"""模型分离（Moodify Studio 逆向分解 · 引擎 B：Demucs htdemucs，母带级）。

为什么存在
  引擎 A（`dsp_separate.py`）是 DSP 中置估计 + HPSS，秒级但不是分离模型：
  有人声残留与伪影，产物只能算**预览**。V4 流程要求「逆向分解 → 多轨复合」，
  而多轨复合只有在分轨真的把乐器拆开时才有意义。本引擎提供那一步。

上游
  代码：https://github.com/adefossez/demucs （MIT）
  模型：`htdemucs` 权重随首次运行下载并缓存于 ~/.cache/torch（不再进 Git）
  产物：drums / bass / other / vocals 四轨

为什么调用上游而不是把源码拷进仓库
  `AGENTS.md` 与技术原则要求「不造第二套 Core、不自研模型」，且
  `existing > mature OSS > custom`。Demucs 是成熟上游：它自己维护模型与版本。
  我们只维护**接口与诚实边界**（本文件 + `runtime.js` 的运行时清单），
  不把上游代码变成我们的维护责任。

诚实边界（随产物一起流转，不是只在文档里）
  - `grade` 为 `MODEL_SEPARATION_NOT_VERIFIED_AGAINST_ORIGINAL_STEMS`：
    原分轨不可知（AI 音乐是单轨直出，没有「原本的轨」这个客体），
    因此「分离得对不对」**无法回答**。可测的代理只有可逆性（`roundtrip.py`）。
  - 分离不是无损：四轨相加与原版**不完全相同**。差值由 roundtrip 步骤测量。

用法: python model_separate.py <input.wav> --outdir DIR [--model htdemucs] [--device cpu|auto]
输出: DIR/<曲名>__<stem>.wav + DIR/manifest.json
"""
import argparse
import hashlib
import json
import os
import platform
import sys
import time


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("input")
    ap.add_argument("--outdir", required=True)
    ap.add_argument("--model", default="htdemucs",
                    help="demucs 预训练模型名（默认 htdemucs）")
    ap.add_argument("--device", default="auto", choices=["auto", "cpu", "cuda"])
    ap.add_argument("--clip-seconds", type=float, default=0.0,
                    help="仅处理前 N 秒（调试用；0 = 全曲）")
    args = ap.parse_args()

    os.makedirs(args.outdir, exist_ok=True)
    t0 = time.time()

    # 缺依赖必须显式失败并说清缺什么：把 ModuleNotFoundError 原样抛给用户，
    # 用户看到的是 traceback 而不是「装什么」。
    try:
        import numpy as np
        import soundfile as sf
        import torch
    except ModuleNotFoundError as exc:
        print(json.dumps({
            "ok": False,
            "error": "DEPENDENCY_MISSING",
            "detail": f"模型分离需要 torch + demucs + soundfile：缺少 {exc.name}",
            "install": "python -m pip install -r moodify-desktop/scripts/requirements-model.txt",
        }, ensure_ascii=False), flush=True)
        return 2

    try:
        from demucs.apply import apply_model
        from demucs.pretrained import get_model
    except ModuleNotFoundError as exc:
        print(json.dumps({
            "ok": False,
            "error": "DEPENDENCY_MISSING",
            "detail": f"未安装 demucs：缺少 {exc.name}",
            "install": "python -m pip install -r moodify-desktop/scripts/requirements-model.txt",
        }, ensure_ascii=False), flush=True)
        return 2

    # soundfile 的「读全部」是 frames=-1，**不是 None**：传 None 会在
    # `frames >= 0` 处抛 TypeError（这条踩过一次，症状是分离在解码阶段就崩）。
    frames = int(args.clip_seconds * 48000) if args.clip_seconds else -1
    y, sr = sf.read(args.input, always_2d=True, dtype="float32", frames=frames)
    y = y[:, :2] if y.shape[1] > 2 else y
    base = os.path.splitext(os.path.basename(args.input))[0]
    print(f"input: {args.input}  {len(y)/sr:.1f}s  {sr}Hz  {y.shape[1]}ch", flush=True)

    # demucs 在 44.1 kHz 立体声上训练；换采样率会明显劣化，所以显式重采样。
    if sr != 44100:
        import librosa
        y = librosa.resample(y.T, orig_sr=sr, target_sr=44100).T
        print(f"resampled {sr}Hz -> 44100Hz", flush=True)
        sr = 44100

    device = args.device
    if device == "auto":
        device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"device: {device}   model: {args.model}", flush=True)

    t1 = time.time()
    model = get_model(args.model)
    model.eval()
    print(f"model ready in {time.time()-t1:.1f}s   sources={list(model.sources)}", flush=True)

    wav = torch.from_numpy(np.ascontiguousarray(y.T))
    ref = wav.mean(0)
    wav = (wav - ref.mean()) / (ref.std() + 1e-8)

    t2 = time.time()
    with torch.no_grad():
        out = apply_model(model, wav[None], device=device, progress=True,
                          split=True, overlap=0.25)[0]
    elapsed = time.time() - t2
    out = out * ref.std() + ref.mean()

    stems = {}
    for name, stem in zip(model.sources, out):
        path = os.path.join(args.outdir, f"{base}__{name}.wav")
        data = stem.detach().cpu().numpy().T
        sf.write(path, data.astype(np.float32), sr)
        peak = float(np.abs(data).max()) if data.size else 0.0
        stems[name] = os.path.abspath(path)
        print(f"  {name:12s} peak={peak:.3f} -> {path}", flush=True)

    manifest = {
        "engine": "demucs",
        "engine_model": args.model,
        "engine_version": getattr(sys.modules.get("demucs"), "__version__", None),
        "engine_grade": "MODEL_SEPARATION_NOT_VERIFIED_AGAINST_ORIGINAL_STEMS",
        "engine_note": "Demucs（MIT, https://github.com/adefossez/demucs）神经网络四轨分离。"
                       "原分轨不可知，因此『分离得对不对』无法回答；可测代理是可逆性"
                       "（把四轨相加与原版比较，见 roundtrip.py）。",
        "upstream": {
            "project": "adefossez/demucs",
            "url": "https://github.com/adefossez/demucs",
            "license": "MIT",
        },
        # 声明划分：Demucs 的四轨**是一套完整分解**（相加即为原版，存在残差）。
        # 声明它是为了让 roundtrip.py 不必搜索子集去猜——引擎最清楚自己的输出结构。
        "partition": {
            "primary": list(model.sources),
            "alternates": [],
            "note": "四轨为一套完整分解；相加与原版存在神经网络重建残差，由 roundtrip.py 测量。",
        },
        "source": os.path.abspath(args.input),
        "source_sha256": sha256_file(args.input),
        "sample_rate": sr,
        "channels": int(y.shape[1]),
        "duration_s": round(len(y) / sr, 3),
        "device": device,
        "stems": stems,
        "stem_order": list(model.sources),
        "inference_elapsed_s": round(elapsed, 2),
        "elapsed_s": round(time.time() - t0, 2),
        "python": platform.python_version(),
    }
    mpath = os.path.join(args.outdir, "manifest.json")
    with open(mpath, "w", encoding="utf-8") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)
    print(f"manifest: {mpath}", flush=True)
    print(json.dumps({"ok": True, "engine": "demucs", "model": args.model,
                      "stems": list(stems), "inference_elapsed_s": manifest["inference_elapsed_s"]},
                     ensure_ascii=False), flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
