"""Moodify Deep Ear: time-localised spectral, dynamics and stereo diagnostics."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import soundfile as sf
from scipy.signal import stft


BANDS = {
    "sub": (20, 80), "bass": (80, 250), "low_mid": (250, 500),
    "presence": (2000, 5000), "harsh": (3000, 8000),
    "air": (10000, 20000),
}


def db(x: np.ndarray | float) -> np.ndarray | float:
    return 20.0 * np.log10(np.maximum(x, 1e-12))


def robust_z(x: np.ndarray) -> np.ndarray:
    med = np.median(x)
    mad = np.median(np.abs(x - med))
    return (x - med) / max(1.4826 * mad, 1e-9)


def analyse(path: Path) -> tuple[dict, np.ndarray, np.ndarray, np.ndarray]:
    audio, sr = sf.read(path, dtype="float32", always_2d=True)
    mono = audio.mean(axis=1)
    nperseg, hop = 8192, 2048
    freqs, times, z = stft(mono, fs=sr, nperseg=nperseg,
                           noverlap=nperseg-hop, boundary=None, padded=False)
    mag = np.abs(z)
    power = mag ** 2
    spec_db = db(mag / max(float(mag.max()), 1e-12))
    total = power.sum(axis=0) + 1e-18
    rms_db = db(np.sqrt(total / power.shape[0]))
    centroid = (freqs[:, None] * power).sum(axis=0) / total
    cumulative = np.cumsum(power, axis=0)
    roll99_idx = np.argmax(cumulative >= total[None, :] * 0.99, axis=0)
    roll99 = freqs[roll99_idx]
    flux = np.r_[0.0, np.sqrt(np.sum(np.maximum(0, np.diff(mag, axis=1)) ** 2, axis=0))]
    flux_z = robust_z(flux)

    band_db: dict[str, np.ndarray] = {}
    for name, (lo, hi) in BANDS.items():
        mask = (freqs >= lo) & (freqs < min(hi, sr / 2))
        band_db[name] = 10 * np.log10(power[mask].sum(axis=0) + 1e-18)

    # One-second stereo correlation, aligned to spectrogram frames by interpolation.
    block = sr
    corr_t, corr_v = [], []
    for start in range(0, len(audio), block):
        seg = audio[start:start+block]
        if len(seg) < sr // 4:
            continue
        left, right = seg[:, 0], seg[:, 1]
        denom = np.std(left) * np.std(right)
        corr_t.append((start + len(seg) / 2) / sr)
        corr_v.append(float(np.corrcoef(left, right)[0, 1]) if denom > 1e-12 else 1.0)
    corr = np.interp(times, corr_t, corr_v) if corr_t else np.ones_like(times)

    loud_z = robust_z(rms_db)
    harsh_rel = band_db["harsh"] - 10 * np.log10(total)
    low_rel = 10 * np.log10(
        10 ** (band_db["sub"] / 10) + 10 ** (band_db["bass"] / 10) + 1e-18
    ) - 10 * np.log10(total)
    harsh_z, low_z, roll_z = robust_z(harsh_rel), robust_z(low_rel), robust_z(roll99)

    events = []
    def add_events(kind: str, score: np.ndarray, threshold: float, direction: str, detail: str) -> None:
        idx = np.flatnonzero(score > threshold if direction == "high" else score < -threshold)
        if not len(idx):
            return
        groups = np.split(idx, np.where(np.diff(idx) > 1)[0] + 1)
        for group in groups:
            if not len(group):
                continue
            peak = group[np.argmax(np.abs(score[group]))]
            events.append({
                "type": kind, "start_s": round(float(times[group[0]]), 2),
                "end_s": round(float(times[group[-1]] + hop / sr), 2),
                "peak_s": round(float(times[peak]), 2),
                "severity_z": round(float(abs(score[peak])), 2), "detail": detail,
            })

    add_events("energy_drop", loud_z, 3.5, "low", "局部能量显著低于全曲稳态，检查停顿或拼接")
    add_events("energy_surge", loud_z, 3.5, "high", "局部能量突增，检查削波或段落跳变")
    add_events("harshness_risk", harsh_z, 3.0, "high", "3–8 kHz 相对能量异常，检查齿音/刺耳共振")
    add_events("low_end_buildup", low_z, 3.0, "high", "20–250 Hz 相对能量异常，检查低频堆积")
    add_events("bandwidth_shift", roll_z, 3.5, "low", "99% 能量带宽局部收窄，检查编码/生成边界")
    add_events("transient_cluster", flux_z, 4.0, "high", "谱通量异常，检查点击、爆音或密集瞬态")
    phase_idx = np.flatnonzero(corr < -0.1)
    for i in phase_idx[:20]:
        events.append({"type": "phase_risk", "start_s": round(float(times[i]), 2),
                       "end_s": round(float(times[i] + 1), 2), "peak_s": round(float(times[i]), 2),
                       "severity_z": round(float(-corr[i]), 2), "detail": "左右声道负相关，检查单声道抵消"})
    events.sort(key=lambda e: (-e["severity_z"], e["peak_s"]))

    result = {
        "source": str(path), "duration_s": round(len(audio) / sr, 3), "sample_rate": sr,
        "analysis": {
            "median_rms_db": round(float(np.median(rms_db)), 2),
            "median_centroid_hz": round(float(np.median(centroid)), 1),
            "median_rolloff99_hz": round(float(np.median(roll99)), 1),
            "stereo_correlation_median": round(float(np.median(corr)), 3),
            "stereo_correlation_min": round(float(np.min(corr)), 3),
            "event_count": len(events),
        },
        "events": events[:60],
        "method": {"fft": nperseg, "hop": hop, "window_s": round(nperseg/sr, 4),
                   "event_thresholds": "robust median/MAD z-scores"},
    }
    return result, times, freqs, spec_db


def render(result: dict, times: np.ndarray, freqs: np.ndarray, spec_db: np.ndarray, out: Path) -> None:
    fig, ax = plt.subplots(figsize=(24, 11), facecolor="#050608")
    ax.set_facecolor("#050608")
    mesh = ax.pcolormesh(times, freqs, np.clip(spec_db, -100, 0), shading="auto",
                         cmap="viridis", vmin=-100, vmax=0, rasterized=True)
    ax.set_ylim(0, min(24000, freqs[-1]))
    ax.set_xlim(0, result["duration_s"])
    ax.set_xlabel("TIME (s)", color="white")
    ax.set_ylabel("FREQUENCY (Hz)", color="white")
    ax.tick_params(colors="white")
    for spine in ax.spines.values(): spine.set_color("#888")
    colors = {"harshness_risk": "#ff5b5b", "low_end_buildup": "#ffae42",
              "energy_drop": "#64b5f6", "energy_surge": "#ffd54f",
              "bandwidth_shift": "#ba68c8", "transient_cluster": "#ef5350",
              "phase_risk": "#00e5ff"}
    for event in result["events"][:24]:
        ax.axvspan(event["start_s"], event["end_s"], color=colors.get(event["type"], "white"), alpha=.13)
        ax.axvline(event["peak_s"], color=colors.get(event["type"], "white"), alpha=.45, lw=.7)
    cb = fig.colorbar(mesh, ax=ax, pad=.01)
    cb.set_label("dBFS-relative", color="white")
    cb.ax.tick_params(colors="white")
    ax.set_title("MOODIFY DEEP EAR — FULL-BAND TIME/FREQUENCY DIAGNOSTIC", color="white", pad=14)
    fig.tight_layout()
    fig.savefig(out, dpi=160, facecolor=fig.get_facecolor())
    plt.close(fig)


def write_report(result: dict, out: Path) -> None:
    a = result["analysis"]
    lines = ["# Moodify Deep Ear 深度听检", "", f"- 输入：`{result['source']}`",
             f"- 时长：{result['duration_s']} s / {result['sample_rate']} Hz",
             f"- 中位频谱质心：{a['median_centroid_hz']} Hz",
             f"- 中位 99% 能量带宽：{a['median_rolloff99_hz']} Hz",
             f"- 立体声相关性：median {a['stereo_correlation_median']} / min {a['stereo_correlation_min']}",
             f"- 自动事件：{a['event_count']}", "", "## 优先检查时间轴", "",
             "| 类型 | 起止 | 峰值 | 强度 | 判断 |", "|---|---:|---:|---:|---|"]
    for e in result["events"][:30]:
        lines.append(f"| {e['type']} | {e['start_s']}–{e['end_s']} s | {e['peak_s']} s | {e['severity_z']} | {e['detail']} |")
    lines += ["", "## 使用边界", "", "事件表示需要听检的异常候选，不等于自动判定为缺陷。",
              "必须结合分轨、乐段语境和处理前后差分确认后，才能下发 DAW 操作。"]
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("audio", type=Path)
    p.add_argument("--output-dir", type=Path, required=True)
    args = p.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    result, times, freqs, spec_db = analyse(args.audio)
    (args.output_dir / "deep_ear.json").write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    write_report(result, args.output_dir / "deep_ear_report.md")
    render(result, times, freqs, spec_db, args.output_dir / "deep_ear_fullband.png")
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
