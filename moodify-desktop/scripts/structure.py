"""结构分析（Moodify Studio 结构阶段 · MSE / Musical-Structural Engineering）。

写出 `<case>/studio/structure.json`。

为什么存在（DEEP-PROCESSING-GAP-SCAN-001）
  V3/V4 流程把「结构」定为独立阶段（`STRUCTURED ← midi/*.mid 非空`），
  但**没有任何模块回答过这首歌的结构是什么**：BPM 多少、拍在哪、哪里换了段落、
  能量怎么走。Core 里只有一个数据类型 `auditory/structure.py::StructureContext`，
  没有任何检测实现（`docs/REPOSITORY_STATUS.md` 如实记为 `ABSENT`）。
  于是「结构」阶段实际只等于「有一个 MIDI 文件」——方案无从知道歌曲的骨架。

本模块补上可测量的那一半：**从音频测出结构事实**，写进产物。

它不是什么
  - 不是段落语义判断：`section_*` 只是「能量/音色发生持续变化的边界」，
    它**不知道**哪段是主歌、哪段是副歌。标签必须由人或由后续模型给出。
  - 不是曲式真值：段落边界检测在流行乐上本来就不是精确科学。产物里带
    `confidence` 与 `method`，不允许被读成定论。

依赖
  只用 numpy + scipy。不引入 librosa/sklearn/pandas：2026-10-05 的故障证明
  这条链在 numpy 2.x 上会因为 pandas 的 C-ABI 崩溃（详见 dsp_separate.py 的注释）。
  节拍与段落检测用自相关 + 谱通量 + 结构自相似矩阵即可完成。

用法: python structure.py <input.wav> [--out FILE] [--max-seconds N]
"""
import argparse
import hashlib
import json
import os
import sys
import time

EPS = 1e-12
# 结构分析用的 STFT：比分离用的窗更短，时间分辨率更高（拍点定位需要）
N_FFT = 2048
HOP = 512
# 段落检测的特征帧率（Hz）：每秒 ~2 帧足够刻画段落变化
SECTION_FPS = 2.0


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def _load_mono(path, max_seconds=0.0):
    import numpy as np
    import soundfile as sf

    info = sf.info(path)
    frames = int(max_seconds * info.samplerate) if max_seconds else -1
    y, sr = sf.read(path, always_2d=True, dtype="float32", frames=frames)
    mono = y.mean(axis=1) if y.shape[1] > 1 else y[:, 0]
    return np.asarray(mono, dtype=np.float64), sr, y.shape[1]


def onset_envelope(mono, sr):
    """谱通量 onset 包络 + 帧率。"""
    import numpy as np
    from scipy import signal

    f, t, Z = signal.stft(mono, fs=sr, window="hann", nperseg=N_FFT,
                          noverlap=N_FFT - HOP, boundary="zeros", padded=True)
    mag = np.abs(Z)
    # 对数压缩后再取正差：对小能量变化更敏感，且抑制纯响度变化
    logmag = np.log1p(10.0 * mag)
    flux = np.maximum(0.0, np.diff(logmag, axis=1)).sum(axis=0)
    frame_rate = sr / HOP
    if flux.size:
        flux = flux - flux.mean()
        std = flux.std()
        if std > EPS:
            flux = flux / std
    return flux.astype(np.float64), frame_rate, mag, t


def estimate_tempo(flux, frame_rate):
    """自相关估计 BPM。返回 (bpm, confidence)。

    倍频歧义必须显式处理，否则会稳定地报错一倍。实测：某曲真实 ~128 BPM，
    自相关在 63.9 BPM 处峰最高（lag 88 恰是 lag 44 的两倍）——
    因为「每两拍一次强音」在自相关里天然更强。所以这里不只做 >150 折半，
    而是比较 lag 与其一半处的自相关：若一半处可观测（≥ 峰值的 85%），
    取更快的那个解释。这是启发式，因此置信度如实反映两者有多接近。
    """
    import numpy as np

    if flux.size < 8:
        return None, 0.0
    ac = np.correlate(flux, flux, mode="full")[flux.size - 1:]
    lo = max(1, int(frame_rate * 60.0 / 200.0))   # 上限 200 BPM
    hi = min(len(ac) - 1, int(frame_rate * 60.0 / 40.0))  # 下限 40 BPM
    if hi <= lo + 1:
        return None, 0.0
    window = ac[lo:hi]
    peak_lag = lo + int(np.argmax(window))
    peak_val = float(ac[peak_lag])

    # 倍频检查：一半的 lag = 两倍的速度
    half_lag = peak_lag // 2
    octave_note = None
    if half_lag >= lo and float(ac[half_lag]) >= 0.85 * peak_val:
        octave_note = (f"自相关在一半 lag ({half_lag}) 处为峰值的 "
                       f"{float(ac[half_lag]) / (peak_val + EPS):.2f}，"
                       f"因此取更快的解释（{60.0 * frame_rate / half_lag:.1f} BPM）。")
        peak_lag = half_lag
        peak_val = float(ac[peak_lag])

    bpm = 60.0 * frame_rate / peak_lag
    if bpm > 200.0:
        bpm = bpm / 2.0
    mean = float(np.mean(np.abs(window))) + EPS
    confidence = float(min(1.0, max(0.0, (peak_val / mean - 1.0) / 4.0)))
    return float(bpm), confidence, octave_note


def beat_grid(flux, frame_rate, bpm):
    """把拍点放在 onset 包络的局部峰上（不是均匀网格）。"""
    import numpy as np
    from scipy import signal as sig

    if not bpm:
        return []
    period = 60.0 / bpm
    # 平滑包络后找峰，再按周期吸附到最近的峰
    smooth = sig.medfilt(flux, kernel_size=5)
    min_dist = max(1, int(period * frame_rate * 0.5))
    peaks, props = sig.find_peaks(smooth, distance=min_dist,
                                  height=float(np.percentile(smooth, 60)))
    if peaks.size == 0:
        return []
    heights = props.get("peak_heights")
    order = np.argsort(heights)[::-1][: max(8, int(len(flux) / frame_rate / period))]
    chosen = np.sort(peaks[order])
    return [round(float(p) / frame_rate, 3) for p in chosen]


def self_similarity(mag, sr):
    """结构自相似矩阵：把频谱按 ~2 fps 聚合，算帧间余弦相似度。"""
    import numpy as np

    hop_frames = max(1, int(round((sr / HOP) / SECTION_FPS)))
    n_blocks = mag.shape[1] // hop_frames
    if n_blocks < 4:
        return None, hop_frames
    trimmed = mag[:, : n_blocks * hop_frames]
    # 用对数能量 + 频带聚合降维（1/3 倍频程式的粗分组）
    logmag = np.log1p(10.0 * trimmed)
    bands = 32
    edges = np.linspace(0, logmag.shape[0], bands + 1).astype(int)
    feats = np.stack([logmag[edges[i]:edges[i + 1]].mean(axis=0)
                      for i in range(bands)], axis=0)
    feats = feats.reshape(bands, n_blocks, hop_frames).mean(axis=2)
    norm = np.linalg.norm(feats, axis=0, keepdims=True) + EPS
    feats = feats / norm
    return (feats.T @ feats), hop_frames


def detect_sections(ssm, hop_frames, sr, min_section_s=8.0):
    """用 novelty 曲线（对角核沿 SSM 卷积）找段落边界。

    阈值必须**自适应**：实测某曲的 novelty 在标准化后最大只有 0.36，
    固定 0.5 的阈值会一条边界都找不到，然后产品会显示「整首一段」——
    那不是「没有段落」，是我们的阈值不适用于这首曲子。所以这里按分位数取阈值，
    并把找不到边界的情形如实标成 `none_detected`，而不是假装整首就是一段。
    """
    import numpy as np
    from scipy import signal as sig

    if ssm is None or ssm.shape[0] < 8:
        return [], [], {"status": "insufficient_frames",
                        "frames": 0 if ssm is None else int(ssm.shape[0])}
    n = ssm.shape[0]
    # checkerboard 核：段落内部相似、跨段落不相似 → 边界处响应最大
    L = min(32, max(4, n // 8))
    if L % 2:
        L += 1
    half = L // 2
    kernel = np.zeros((L, L))
    kernel[:half, half:] = 1.0
    kernel[half:, :half] = 1.0
    kernel -= kernel.mean()
    novelty = np.zeros(n)
    for i in range(half, n - half):
        novelty[i] = float(np.sum(ssm[i - half:i + half, i - half:i + half] * kernel))
    novelty = novelty - novelty.mean()
    std = novelty.std()
    if std <= EPS:
        return [], [], {"status": "flat_novelty", "frames": n}
    novelty = novelty / std

    frame_s = hop_frames / (sr / HOP)
    min_gap = max(1, int(min_section_s / frame_s))

    # 自适应阈值：0.5σ 与 90 分位取较小者（分位数对小样本更稳）
    height = min(0.5, float(np.percentile(novelty, 90)))
    peaks, props = sig.find_peaks(novelty, distance=min_gap, height=height, prominence=0.3)
    times = [round(float(p) * frame_s, 3) for p in peaks]
    strengths = [round(float(h), 3) for h in props.get("peak_heights", [])]
    diag = {
        "status": "ok" if times else "none_detected",
        "frames": n,
        "kernel": L,
        "frame_s": round(frame_s, 3),
        "threshold": round(height, 3),
        "novelty_max": round(float(novelty.max()), 3),
        "note": None if times else
                "在自适应阈值下没有找到边界。这表示**本方法**没测到明确的段落变化，"
                "不表示这首歌没有段落结构。",
    }
    return times, strengths, diag


def energy_profile(mono, sr, fps=SECTION_FPS):
    """RMS 能量随时间（dBFS，满幅 1.0 参考）与谱质心。

    RMS 用**时域分块**算，不从 STFT 幅度反推：STFT 的幅度是窗和归一化过的
    （`max|Z|` 只有 0.31，而真实峰值 0.67），直接拿它当电平会低报十几 dB——
    这种「看起来像测量」的错数比没有数更糟。
    """
    import numpy as np
    from scipy import signal as sig

    hop = max(1, int(sr / fps))
    win = hop * 2
    if len(mono) < win:
        return [], []
    starts = range(0, len(mono) - win + 1, hop)
    rms_db = [round(float(20.0 * np.log10(np.sqrt(np.mean(mono[s:s + win] ** 2)) + EPS)), 2)
              for s in starts]

    # 谱质心照常用 STFT（它只关心频率分布，与绝对电平无关）
    f, _t, Z = sig.stft(mono, fs=sr, window="hann", nperseg=win, noverlap=win - hop,
                        boundary="zeros", padded=True)
    mag = np.abs(Z) + EPS
    centroid = np.sum(f[:, None] * mag, axis=0) / np.sum(mag, axis=0)
    cent = [round(float(v), 1) for v in centroid]
    return rms_db, cent


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("input")
    ap.add_argument("--out", help="写出 structure.json 的路径")
    ap.add_argument("--max-seconds", type=float, default=0.0,
                    help="只分析前 N 秒（调试用；0 = 全曲）")
    args = ap.parse_args()

    try:
        import numpy as np
    except ModuleNotFoundError as exc:
        print(json.dumps({"ok": False, "error": "DEPENDENCY_MISSING",
                          "detail": f"缺少 {exc.name}"}, ensure_ascii=False))
        return 2

    if not os.path.exists(args.input):
        print(json.dumps({"ok": False, "error": "INPUT_NOT_FOUND",
                          "detail": args.input}, ensure_ascii=False))
        return 1

    t0 = time.time()
    print(f"input: {args.input}", flush=True)
    mono, sr, channels = _load_mono(args.input, args.max_seconds)
    duration = len(mono) / sr if sr else 0.0
    print(f"  {duration:.1f}s  {sr}Hz  {channels}ch", flush=True)

    flux, frame_rate, mag, _t = onset_envelope(mono, sr)
    bpm, tempo_conf, octave_note = estimate_tempo(flux, frame_rate)
    print(f"  tempo: {bpm if bpm else 'n/a'} BPM (confidence {tempo_conf:.2f})", flush=True)

    beats = beat_grid(flux, frame_rate, bpm)
    print(f"  beats: {len(beats)}", flush=True)

    ssm, hop_frames = self_similarity(mag, sr)
    boundaries, strengths, section_diag = detect_sections(ssm, hop_frames, sr)
    print(f"  section boundaries: {len(boundaries)} ({section_diag.get('status')})", flush=True)

    rms_db, centroid = energy_profile(mono, sr)

    # 段落 = 边界切出的区间；标签是**位置编号**，不是主歌/副歌判断
    edges = [0.0] + boundaries + [round(duration, 3)]
    sections = []
    for i in range(len(edges) - 1):
        start, end = edges[i], edges[i + 1]
        if end - start < 1.0:
            continue
        idx = [j for j, v in enumerate(rms_db) if start <= j / SECTION_FPS < end]
        seg = [rms_db[j] for j in idx] or [0.0]
        sec = {
            "index": len(sections),
            "start_s": round(start, 3),
            "end_s": round(end, 3),
            "duration_s": round(end - start, 3),
            "mean_rms_db": round(float(np.mean(seg)), 2),
            "peak_rms_db": round(float(np.max(seg)), 2),
        }
        if i < len(strengths):
            sec["boundary_strength"] = strengths[i]
        sections.append(sec)

    result = {
        "schema": "moodify.studio.structure/0.1",
        "ok": True,
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "source": os.path.abspath(args.input),
        "source_sha256": sha256_file(args.input),
        "sample_rate": sr,
        "channels": channels,
        "duration_s": round(duration, 3),
        "tempo": {
            "bpm": round(bpm, 2) if bpm else None,
            "confidence": round(tempo_conf, 3),
            "method": "autocorrelation of spectral flux",
            "octave_note": octave_note,
            "note": "倍频歧义按「一半 lag 处自相关 ≥ 峰值 85% 则取更快解释」处理；仍可能差一倍。",
        },
        "beats_s": beats,
        "beat_count": len(beats),
        "sections": sections,
        "section_detection": section_diag,
        "energy_profile": {
            "fps": SECTION_FPS,
            "rms_db": rms_db,
            "spectral_centroid_hz": centroid,
        },
        "method": {
            "onset": "log-magnitude spectral flux",
            "tempo": "autocorrelation",
            "sections": "checkerboard-kernel novelty on spectral self-similarity",
            "n_fft": N_FFT,
            "hop": HOP,
        },
        "judgment_boundary": {
            "what_this_is": "从音频测出的**结构事实**：速度、拍点位置、能量/音色持续变化的边界。",
            "what_this_is_not": "不是曲式判断。`index` 是位置编号，**不是**主歌/副歌标签；"
                                "段落语义必须由人或后续模型给出。",
            "confidence_note": "段落边界在流行乐上本就不精确；0.5–1.0 的 novelty 峰值都可能是噪声。",
            "layer": "layer1_measurement + layer2_structure 的机器部分；"
                     "layer3_musical_judgment 不在此文件承诺。",
        },
        "elapsed_s": round(time.time() - t0, 2),
    }

    text = json.dumps(result, ensure_ascii=False, indent=2)
    if args.out:
        os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
        with open(args.out, "w", encoding="utf-8") as f:
            f.write(text + "\n")
        print(f"structure: {args.out}", flush=True)
    print(json.dumps({"ok": True, "bpm": result["tempo"]["bpm"],
                      "beats": result["beat_count"],
                      "sections": len(sections),
                      "elapsed_s": result["elapsed_s"]}, ensure_ascii=False), flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
