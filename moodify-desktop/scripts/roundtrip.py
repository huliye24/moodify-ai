"""可逆性验证（Moodify Studio 逆向分解 → 复合 的返回检查）。

写出 `<case>/studio/roundtrip.json`。

它回答什么
  「把分解出来的轨重新加起来，能回到原版吗？」

它**不**回答什么（这条比上面的答案更重要）
  「分轨分得对吗？」
  原分轨不可知——AI 音乐是单轨直出，不存在「原本的轨」这个客体。所以分离质量
  **无法直接测量**。本脚本测的是**重建一致性**，它是质量的**代理**，不是质量本身。

为什么必须把这句话写进产物
  任何可逆分解都能通过这个测试：最极端的例子是「轨1 = 原版，轨2 = 静音」，
  它完美可逆，却完全没有分离。所以：

      passed == true   只表示「这套分解在数值上是一致的」
      passed == true   不表示「这套分轨是好的」

  把它读成「分轨已验证」就是发明测量事实。因此 `passed` 之外必须同时携带
  `control`（把平凡分解也跑一遍，让用户看到同一指标在无分离情况下同样会通过）。

用法:
  python roundtrip.py --stems DIR [--original FILE] [--out FILE]
  （--original 省略时从 DIR/manifest.json 的 source 字段取）
输出: JSON 到 stdout；--out 时同时写文件
"""
import argparse
import hashlib
import json
import os
import sys
import time

EPS = 1e-12
# 与 Core 的 -1 dBFS 天花板一致的宽松上界：超过它说明重建里有削波级误差
CLIP_WARN_DBFS = -1.0


def _read_mono_pair(path, target_len=None):
    """读成立体声 (n,2) float32；单声道复制成两列。返回 (data, sr)。"""
    import numpy as np
    import soundfile as sf

    y, sr = sf.read(path, always_2d=True, dtype="float32")
    if y.shape[1] == 1:
        y = np.repeat(y, 2, axis=1)
    elif y.shape[1] > 2:
        y = y[:, :2]
    if target_len is not None:
        if len(y) < target_len:
            y = np.pad(y, ((0, target_len - len(y)), (0, 0)))
        elif len(y) > target_len:
            y = y[:target_len]
    return y, sr


def _resample_pair(y, sr_from, sr_to):
    """把 (n,2) 重采样到 sr_to。

    为什么必须做：模型分离（Demucs）在 44.1 kHz 上推理，所以**分轨的采样率与
    原版不同**。不重采样直接比较，等于拿两段不同时间尺度的波形相减——
    实测会得到一个 best_scale_gain=0.004、correlation=0.004 的「不可逆」假象。
    这类错误最危险的地方在于它看起来像一个严肃的失败结论。
    """
    import numpy as np
    from scipy import signal as sig

    if sr_from == sr_to:
        return y
    from math import gcd

    g = gcd(int(sr_from), int(sr_to))
    return sig.resample_poly(y, sr_to // g, sr_from // g, axis=0).astype(np.float32)


def _rms_db(x):
    import numpy as np

    r = float(np.sqrt(np.mean(np.square(x)))) if x.size else 0.0
    return 20.0 * np.log10(r + EPS)


def _db(x):
    import numpy as np

    return 20.0 * np.log10(abs(float(x)) + EPS)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--stems", required=True, help="包含 manifest.json 的分轨目录")
    ap.add_argument("--original", help="原版音频；省略则取 manifest.source")
    ap.add_argument("--out", help="写出 roundtrip.json 的路径")
    ap.add_argument("--tolerance-db", type=float, default=None,
                    help="null 深度阈值（dB，相对原版）。省略时按引擎取默认值")
    ap.add_argument("--min-correlation", type=float, default=0.995,
                    help="相关系数下限。默认 0.995")
    args = ap.parse_args()

    try:
        import numpy as np
    except ModuleNotFoundError as exc:
        print(json.dumps({"passed": False, "error": "DEPENDENCY_MISSING",
                          "detail": f"缺少 {exc.name}"}, ensure_ascii=False))
        return 2

    manifest_path = os.path.join(args.stems, "manifest.json")
    manifest = {}
    if os.path.exists(manifest_path):
        try:
            with open(manifest_path, encoding="utf-8") as f:
                manifest = json.load(f)
        except (OSError, ValueError):
            manifest = {}

    original = args.original or manifest.get("source")
    if not original or not os.path.exists(original):
        result = {
            "schema": "moodify.studio.roundtrip/0.1",
            "passed": False,
            "error": "ORIGINAL_NOT_FOUND",
            "detail": "找不到原版音频；无法验证可逆性（缺原版就没有参照）。",
            "original": original,
            "engine": manifest.get("engine"),
        }
        _emit(result, args.out)
        return 1

    stem_paths = manifest.get("stems") or {}
    # manifest 没有 stems 时退回扫描目录里的 *.wav（不要静默返回空）
    if not stem_paths:
        stem_paths = {
            os.path.splitext(n)[0]: os.path.join(args.stems, n)
            for n in sorted(os.listdir(args.stems))
            if n.lower().endswith(".wav")
        }
    stem_paths = {k: v for k, v in stem_paths.items()
                  if v and os.path.exists(v) and os.path.abspath(v) != os.path.abspath(original)}
    if not stem_paths:
        result = {
            "schema": "moodify.studio.roundtrip/0.1",
            "passed": False,
            "error": "NO_STEMS",
            "detail": "分轨目录里没有可分轨的 wav（或全部指向原版自身）。",
            "original": original,
            "engine": manifest.get("engine"),
        }
        _emit(result, args.out)
        return 1

    t0 = time.time()
    ref_raw, sr_ref = _read_mono_pair(original)

    import numpy as np

    # 采样率对齐：以**分轨**的采样率为准（分轨是重建的那一侧，原版可以重采样）。
    first_path = next(iter(stem_paths.values()))
    _probe, sr_stem = _read_mono_pair(first_path, target_len=1)
    rate_note = None
    if sr_stem != sr_ref:
        ref_raw = _resample_pair(ref_raw, sr_ref, sr_stem)
        rate_note = (f"原版 {sr_ref} Hz → 分轨 {sr_stem} Hz 重采样后比较"
                     f"（模型分离在 44.1 kHz 上推理，两侧采样率本就不同）")
        sr_ref = sr_stem
    n = len(ref_raw)
    ref = ref_raw

    # 读入所有分轨（缓存，划分搜索要反复相加，不能反复解码）
    loaded = {}
    for name, path in sorted(stem_paths.items()):
        try:
            data, _sr = _read_mono_pair(path, target_len=n)
        except Exception as exc:  # 单轨读不出来不能假装它贡献为零
            result = {
                "schema": "moodify.studio.roundtrip/0.1",
                "passed": False,
                "error": "STEM_UNREADABLE",
                "detail": f"分轨 {name} 读取失败：{exc}",
                "original": original,
                "engine": manifest.get("engine"),
            }
            _emit(result, args.out)
            return 1
        loaded[name] = data

    silent = [k for k, v in loaded.items()
              if v.size == 0 or float(np.abs(v).max()) <= 1e-6]

    # ── 选哪一组轨来验可逆性 ───────────────────────────────────────────────
    #
    # 这是本脚本最容易做错的一步。一个分离引擎可能产出**多套相互重叠的划分**
    # （DSP 引擎就是这样：{vocals, instrumental} 与 {harmonic, percussive} 各自完整，
    # 但四轨相加 = 2×原版）。把它们全部相加会得到一个漂亮的「不可逆」假象。
    #
    # 所以顺序是：
    #   1. manifest 自己声明了 partition → 用它（引擎最清楚自己的输出结构）
    #   2. 没声明 → 搜索所有子集，取 null 最深的那个划分，并如实报告「是我们选的」
    declared = _declared_partitions(manifest)
    candidates = [p for p in declared if all(k in loaded for k in p)]

    if not candidates:
        candidates = _search_partitions(loaded, ref)
        partition_source = "SEARCHED_BY_NULL_DEPTH"
    else:
        partition_source = "DECLARED_BY_ENGINE_MANIFEST"

    acc = np.zeros_like(ref)
    used = {}
    for name in candidates[0]:
        acc += loaded[name]
        used[name] = os.path.abspath(stem_paths[name])
    excluded = sorted(set(loaded) - set(candidates[0]))

    # 最优增益：最小二乘意义下让 acc 最接近 ref。它把「整体缩放」与「形状不对」
    # 分开——一个只是整体小了一半的分解，不该被读成「不可逆」。
    denom = float(np.sum(np.square(acc)))
    gain = float(np.sum(acc * ref) / denom) if denom > EPS else 0.0
    residual = ref - gain * acc
    null_rms_db = _rms_db(residual) - _rms_db(ref)  # 相对原版电平的 null 深度（dB）
    peak_err = float(np.abs(residual).max())

    ref_energy = float(np.sum(np.square(ref)))
    err_energy = float(np.sum(np.square(residual)))
    correlation = (float(np.sum(acc * ref)) /
                   float(np.sqrt(np.sum(np.square(acc)) * ref_energy) + EPS))

    # ── 判定标准 ────────────────────────────────────────────────────────────
    #
    # 为什么阈值必须分引擎，而不是一个全局常量：
    #   两条路径的误差**性质不同**，用同一个数字衡量会给出错误结论。
    #     · DSP 中置划分是**精确分解**（vocals + instrumental == 源，逐样本），
    #       null 深度只受 float32 量化限制（实测 ≈ -77 dB）。
    #     · Demucs 不是纯分解器，它**重建**信号：四轨相加带有真实的模型残差。
    #       实测 30s 片段：null ≈ -33 dB、correlation 0.9997、scale gain 1.001。
    #       这是 htdemucs 的正常水平，不是缺陷。
    #   用 -40 dB 去卡 Demucs 会把它判成「不可逆」，而它其实重建得很好；
    #   用 -25 dB 去卡 DSP 又会放过一个本该精确的划分。所以两边各拿自己的尺子。
    DEFAULTS = {
      'dsp_center_hpss': (-40.0, 'DSP 中置划分是精确分解，阈值取严格值；'
                                '未达 -40 dB 说明分解真的漏了东西。'),
      'demucs': (-25.0, 'Demucs 是重建式模型，四轨相加带真实模型残差'
                        '（本机实测 ≈ -33 dB / correlation 0.9997）；'
                        '-25 dB 是「明显劣化」的分界，不是「完美重建」的门槛。'),
    }
    engine = manifest.get('engine')
    default_db, threshold_rationale = DEFAULTS.get(engine, (
      -30.0,
      '未知引擎：取中间值 -30 dB。引擎应在 manifest.engine 里自报身份，'
      '否则无法为它选择合适的判定标准。',
    ))
    tolerance_db = args.tolerance_db if args.tolerance_db is not None else default_db

    passed = bool(null_rms_db <= tolerance_db
                  and correlation >= args.min_correlation
                  and error_is_finite(correlation))

    # 控制组：最平凡的「分解」——轨1=原版，轨2=静音。它 100% 可逆，却零分离。
    # 把同一个指标在它身上的读数记下来，是为了让「passed」无法被读成「分轨好」。
    control = _control(reference_is_original=True)

    result = {
        "schema": "moodify.studio.roundtrip/0.1",
        "passed": passed,
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "original": os.path.abspath(original),
        "stem_dir": os.path.abspath(args.stems),
        "engine": manifest.get("engine"),
        "engine_grade": manifest.get("engine_grade"),
        "stems": used,
        "all_stems": {k: os.path.abspath(v) for k, v in stem_paths.items()},
        "excluded_stems": excluded,
        "partition_source": partition_source,
        "partition_alternates": candidates[1:3],
        "silent_stems": silent,
        "measurement": {
            "best_scale_gain": round(gain, 6),
            "null_depth_db": round(float(null_rms_db), 3),
            "peak_residual": round(peak_err, 6),
            "correlation": round(correlation, 6),
            "ref_rms_db": round(_rms_db(ref), 3),
            "residual_rms_db": round(_rms_db(residual), 3),
            "energy_ratio_db": round(_db(np.sqrt(err_energy / (ref_energy + EPS))), 3),
            "threshold_db": tolerance_db,
            "threshold_source": ("explicit --tolerance-db" if args.tolerance_db is not None
                                 else f"engine default for {engine or 'unknown'}"),
            "threshold_rationale": threshold_rationale,
            "min_correlation": args.min_correlation,
            "sample_rate": sr_stem,
            "rate_alignment": rate_note,
            "duration_s": round(n / sr_stem, 3),
            "elapsed_s": round(time.time() - t0, 3),
        },
        "control": control,
        "interpretation": {
            "passed_means": "分解出来的轨相加后能回到原版（数值上一致），"
                            f"null 深度 {round(float(null_rms_db), 1)} dB ≤ 阈值 {tolerance_db} dB、"
                            f"correlation {round(correlation, 4)} ≥ {args.min_correlation}。"
                            f"（参与验证的划分：{' + '.join(candidates[0])}；"
                            f"来源：{partition_source}）",
            "passed_does_not_mean": "分轨分离得好。任何可逆分解都能通过本测试——"
                                    "控制组（轨1=原版、轨2=静音）同样通过，而它没有分离任何东西。",
            "why_no_direct_quality": "原分轨不可知：AI 音乐是单轨直出，不存在『原本的轨』。"
                                     "因此分离质量只能由人的听觉判断，不能由本文件代替。",
            "excluded_note": (f"未参与验证的轨：{'、'.join(excluded)}。"
                              "它们属于同一引擎产出的另一套重叠划分，"
                              "与主划分相加会重复计算（不是缺陷）。") if excluded else None,
            "note": "本文件只记录机器对『重建一致性』的测量，不构成对分轨质量的结论。",
        },
    }
    _emit(result, args.out)
    return 0 if passed else 1


def error_is_finite(value):
    return value == value and abs(value) != float("inf")


def _declared_partitions(manifest):
    """从 manifest 读出引擎自己声明的划分，主划分在前。"""
    out = []
    block = manifest.get("partition") or {}
    primary = block.get("primary")
    if isinstance(primary, (list, tuple)) and len(primary) >= 2:
        out.append(tuple(primary))
    for alt in (block.get("alternates") or []):
        if isinstance(alt, (list, tuple)) and len(alt) >= 2:
            out.append(tuple(alt))
    return out


def _search_partitions(loaded, ref, max_stems=8):
    """引擎没声明划分时的兜底：搜索子集，按 null 深度排序返回。

    只在轨数少的时候做（2^n 子集）；轨多了就退回「全部相加」，并让调用方
    从 partition_source 看出这是兜底而不是声明。
    """
    from itertools import combinations

    import numpy as np

    names = sorted(loaded)
    if len(names) > max_stems:
        return [tuple(names)]

    scored = []
    for size in range(2, len(names) + 1):
        for combo in combinations(names, size):
            acc = np.zeros_like(ref)
            for k in combo:
                acc += loaded[k]
            denom = float(np.sum(np.square(acc)))
            if denom <= EPS:
                continue
            gain = float(np.sum(acc * ref) / denom)
            residual = ref - gain * acc
            scored.append(((_rms_db(residual) - _rms_db(ref)), combo))
    if not scored:
        return [tuple(names)]
    scored.sort(key=lambda item: item[0])
    return [combo for _depth, combo in scored]


def _control(reference_is_original=False):
    """平凡分解的指标读数（解析可得，无需真的跑一遍）。"""
    return {
        "kind": "TRIVIAL_DECOMPOSITION",
        "description": "轨1 = 原版，轨2 = 静音。零分离，但 100% 可逆。",
        "null_depth_db": "-inf（完全相同，残差为 0）",
        "passed_if_measured": True,
        "purpose": "证明本指标只反映重建一致性，不反映分离质量。",
    }


def _emit(result, out_path):
    text = json.dumps(result, ensure_ascii=False, indent=2)
    print(text, flush=True)
    if out_path:
        os.makedirs(os.path.dirname(os.path.abspath(out_path)), exist_ok=True)
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(text + "\n")


if __name__ == "__main__":
    sys.exit(main())
