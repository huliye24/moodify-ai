"""DSP 快速分离（Moodify Studio 逆向分解 · 引擎 A：秒级，非模型）。

原理：
  1. 中置声道估计（center-pan extraction）：人声多居中，按 L/R 相似度逐样本加权，
     相似处归人声，其余归伴奏。Audacity「人声减除」同源思路的独立实现。
  2. HPSS 谱分解：对幅度谱做**中值滤波**分出谐波（持续音）与打击（瞬态）。
     这是 librosa.decompose.hpss 的同一算法，此处用 scipy 直接实现。

为什么不再依赖 librosa（2026-10-05，DEEP-PROCESSING-GAP-SCAN-001）
  本脚本原先调用 `librosa.decompose.hpss`。这条导入链是：
      librosa.decompose → sklearn → pandas → numpy C-ABI
  在 numpy 2.x 环境下，只要 pandas 是按旧 numpy 编译的，导入即抛

      ValueError: numpy.dtype size changed, may indicate binary incompatibility

  于是「快速分离」在真实机器上**必然崩溃**，③ 逆向分解整段不可达——
  而这正是它被反复报告「深度处理有问题」的根因。HPSS 本身只需要中值滤波，
  scipy.ndimage 就够了；把重依赖链换成 scipy，等于把这一段的失败面清零。

诚实边界（不变）：非神经网络分离，有人声残留与伪影；产物用于快速观察、
选段试听和 MIDI 前处理，**不构成母带级分轨**。需要母带级分轨请用模型引擎
（`model_separate.py`，Demucs htdemucs）。

用法: python dsp_separate.py <input.wav> --outdir DIR
输出: DIR/<曲名>__<stem>.wav + DIR/manifest.json（引擎、参数、源 sha256）
"""
import argparse
import hashlib
import json
import os
import time

import numpy as np
import soundfile as sf
from scipy import ndimage, signal

EPS = 1e-6

# STFT 参数：4096 窗 / 1024 跳，与 HPSS 的谐波-瞬态时间尺度匹配
N_FFT = 4096
HOP = 1024
# 中值滤波核长（帧）：谐波沿时间方向平滑，瞬态沿频率方向平滑
HARMONIC_KERNEL = 31
PERCUSSIVE_KERNEL = 31


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


def _soft_mask(mag, kernel, axis):
    """单侧中值滤波 → 软掩码。axis=1 沿时间（谐波），axis=0 沿频率（瞬态）。"""
    size = [1, 1]
    size[axis] = kernel
    other = 1 - axis
    size_other = [1, 1]
    size_other[other] = kernel
    filt = ndimage.median_filter(mag, size=tuple(size))
    return filt


def hpss_split(y):
    """HPSS：谐波（持续）与打击（瞬态）。返回 (harm, perc)，与输入同长度。

    做法与 librosa 一致：分别沿时间轴与频率轴对幅度谱做中值滤波，得到两个
    估计谱，再用二者的相对大小构造软掩码，最后逆变换回时域。
    """
    mono = y.mean(axis=1) if y.shape[1] > 1 else y[:, 0]
    n = len(mono)

    f, t, Z = signal.stft(
        mono, fs=1.0, window="hann", nperseg=N_FFT, noverlap=N_FFT - HOP,
        boundary="zeros", padded=True,
    )
    mag = np.abs(Z)
    harm_est = ndimage.median_filter(mag, size=(1, HARMONIC_KERNEL))
    perc_est = ndimage.median_filter(mag, size=(PERCUSSIVE_KERNEL, 1))
    total = harm_est + perc_est + EPS
    mask_h = harm_est / total

    _, h = signal.istft(Z * mask_h, fs=1.0, window="hann", nperseg=N_FFT,
                        noverlap=N_FFT - HOP, boundary="zeros")
    _, p = signal.istft(Z * (1.0 - mask_h), fs=1.0, window="hann", nperseg=N_FFT,
                        noverlap=N_FFT - HOP, boundary="zeros")

    h = np.asarray(h[:n], dtype=np.float32)
    p = np.asarray(p[:n], dtype=np.float32)
    if len(h) < n:  # 极端短输入：补零而不是让下游拿到长度不一的轨
        h = np.pad(h, (0, n - len(h)))
        p = np.pad(p, (0, n - len(p)))
    return h, p


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

    print("HPSS 谐波/打击分解中…（scipy 中值滤波）", flush=True)
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
        "engine_grade": "PREVIEW_NOT_MASTERING_GRADE",
        "engine_note": "非模型快速分离：中置声道估计 + HPSS 谱分解（scipy 中值滤波）；"
                       "有人声残留与伪影，供快速观察/选段试听/MIDI 前处理，"
                       "不构成母带级分轨。母带级分轨请用模型引擎（Demucs）。",
        "algorithm": {
            "center_extract": "mask = (1 - |L-R|/(|L|+|R|))^2",
            "hpss": "median-filter soft mask on magnitude STFT",
            "n_fft": N_FFT,
            "hop": HOP,
            "harmonic_kernel": HARMONIC_KERNEL,
            "percussive_kernel": PERCUSSIVE_KERNEL,
        },
        # 本引擎产出的是**两套相互重叠的分解**，不是一个四轨分解：
        #   {vocals, instrumental} 与 {harmonic, percussive} 各自都是原版的一个完整划分。
        # 四轨相加 = 2 × 原版，所以「可逆性」必须按划分来验，不能把四个加在一起。
        # 这个字段就是给 roundtrip.py 的机器可读声明（否则它只能靠猜）。
        "partition": {
            "primary": ["vocals", "instrumental"],
            "alternates": [["harmonic", "percussive"]],
            "note": "两套划分各自完整；不同划分之间重叠，不可相加。",
        },
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
    print(json.dumps({"ok": True, "engine": manifest["engine"],
                      "elapsed_s": manifest["elapsed_s"]}, ensure_ascii=False), flush=True)


if __name__ == "__main__":
    main()
