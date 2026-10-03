"""DSP 快速分离（Moodify Studio 分离工作台 · 引擎 A）。

原理（非模型，秒级）：
  1. 中置声道估计（center-pan extraction）：人声多居中，按 L/R 相似度逐样本加权，
     相似处归人声，其余归伴奏。Audacity「人声减除」同源思路的独立实现。
  2. HPSS 谱分解（librosa）：中值滤波分出谐波（持续音）与打击（瞬态）。

诚实边界：非神经网络分离，有人声残留与伪影；产物用于快速观察、
选段试听和 MIDI 前处理，不构成母带级分轨。

用法: python dsp_separate.py <input.wav> --outdir DIR [--stems vocals,instrumental,...]
输出: DIR/<曲名>__<stem>.wav + DIR/manifest.json（引擎、参数、源 sha256）
"""
import argparse
import hashlib
import json
import os
import time

import numpy as np
import soundfile as sf

EPS = 1e-6


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def center_extract(y):
    """中置声道估计：mask = 1 - |L-R|/(|L|+|R|)，L/R 越接近越归人声。"""
    if y.shape[1] < 2:
        return y.copy(), np.zeros_like(y)
    L, R = y[:, 0], y[:, 1]
    diff, total = np.abs(L - R), np.abs(L) + np.abs(R)
    mask = 1.0 - np.clip(diff / (total + EPS), 0.0, 1.0)
    mask = mask**2  # 锐化：只有高度居中的内容才归人声
    voc = y * mask[:, None]
    return voc.astype(np.float32), (y - voc).astype(np.float32)


def hpss_split(y):
    """HPSS：谐波（持续）与打击（瞬态）。单声道退化时对中置走一遍。"""
    import librosa

    mono = y.mean(axis=1) if y.shape[1] > 1 else y[:, 0]
    H, P = librosa.decompose.hpss(librosa.stft(mono))
    h = librosa.istft(H, length=len(mono))
    p = librosa.istft(P, length=len(mono))
    return h.astype(np.float32), p.astype(np.float32)


def write_stem(path, data, sr, channels):
    if channels == 1:
        sf.write(path, data, sr)
    elif data.ndim == 1:
        sf.write(path, np.stack([data, data], axis=1), sr)
    else:
        sf.write(path, data, sr)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("input")
    ap.add_argument("--outdir", required=True)
    args = ap.parse_args()

    os.makedirs(args.outdir, exist_ok=True)
    t0 = time.time()
    y, sr = sf.read(args.input, always_2d=True, dtype="float32")
    if y.shape[1] > 2:  # >2 声道取前两（DSP 引擎按立体声处理）
        y = y[:, :2]
    base = os.path.splitext(os.path.basename(args.input))[0]

    print(f"input: {args.input}  {len(y)/sr:.1f}s  {sr}Hz  {y.shape[1]}ch", flush=True)

    stems = {}
    voc, inst = center_extract(y)
    stems["vocals"] = voc
    stems["instrumental"] = inst

    print("HPSS 谐波/打击分解中…", flush=True)
    harm, perc = hpss_split(y)
    stems["harmonic"] = harm
    stems["percussive"] = perc

    for name, data in stems.items():
        peak = float(np.abs(data).max()) if data.size else 0.0
        path = os.path.join(args.outdir, f"{base}__{name}.wav")
        write_stem(path, data, sr, y.shape[1])
        print(f"  {name:12s} peak={peak:.3f} -> {path}", flush=True)

    manifest = {
        "engine": "dsp_center_hpss",
        "engine_note": "非模型快速分离：中置声道估计 + HPSS 谱分解；有人声残留与伪影，"
                       "供快速观察/选段试听/MIDI 前处理，不构成母带级分轨。",
        "source": os.path.abspath(args.input),
        "source_sha256": sha256_file(args.input),
        "sample_rate": sr,
        "channels": int(y.shape[1]),
        "duration_s": round(len(y) / sr, 3),
        "stems": {k: os.path.abspath(os.path.join(args.outdir, f"{base}__{k}.wav"))
                  for k in stems},
        "elapsed_s": round(time.time() - t0, 2),
    }
    mpath = os.path.join(args.outdir, "manifest.json")
    with open(mpath, "w", encoding="utf-8") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)
    print(f"manifest: {mpath}", flush=True)
    print(json.dumps({"ok": True, "manifest": manifest}, ensure_ascii=False), flush=True)


if __name__ == "__main__":
    main()
