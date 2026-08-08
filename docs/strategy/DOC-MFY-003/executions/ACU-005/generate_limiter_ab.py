"""Generate AEP-ACU-005 AB comparison curves."""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import math
from pathlib import Path

OUT_DIR = Path(__file__).resolve().parent / "assets"
DATA_DIR = Path(__file__).resolve().parent / "data"
OUT_DIR.mkdir(parents=True, exist_ok=True)
DATA_DIR.mkdir(parents=True, exist_ok=True)

plt.rcParams["font.family"] = "Microsoft YaHei"
plt.rcParams["font.size"] = 9

from moodify.processing.limiter import (
    apply_limiter_tp, apply_limiter_legacy,
    measure_true_peak, measure_low_freq_thd,
)

SR = 44100


def plot_envelope_comparison():
    """Plot gain reduction envelope: legacy (zero attack) vs new (1ms attack)."""
    freq, dur = 60, 0.1
    t = np.arange(int(SR * dur)) / SR
    tone = np.sin(2 * np.pi * freq * t) * 0.95

    r_old = apply_limiter_legacy(tone, SR, ceiling_db=-6.0, release_ms=50.0)
    r_new, audit = apply_limiter_tp(tone, SR, ceiling_dbtp=-6.0, attack_ms=1.0, release_ms=50.0)

    # Compute gain reduction envelopes
    ceiling_lin = 10 ** (-6.0 / 20.0)
    env = np.abs(tone)

    # Legacy gain
    gain_old = np.ones(len(tone))
    gr = 1.0
    rel_coeff = math.exp(-1.0 / (50.0 * SR / 1000.0))
    for n in range(len(tone)):
        tg = min(1.0, ceiling_lin / max(env[n], 1e-15))
        if tg < gr:
            gr = tg  # zero attack
        else:
            gr = rel_coeff * gr + (1 - rel_coeff) * tg
        gain_old[n] = gr

    # New gain (from audit has max GR only; recompute envelope)
    att_coeff = math.exp(-1.0 / (1.0 * SR / 1000.0))
    la = max(1, int(1.5 * SR / 1000.0))
    gain_new = np.ones(len(tone))
    gr = 1.0
    for n in range(len(tone)):
        end = min(n + la, len(tone))
        peak = float(np.max(env[n:end]))
        tg = min(1.0, ceiling_lin / max(peak, 1e-15))
        if tg < gr:
            gr = att_coeff * gr + (1 - att_coeff) * tg
        else:
            gr = rel_coeff * gr + (1 - rel_coeff) * tg
        gain_new[n] = gr

    fig, axes = plt.subplots(2, 1, figsize=(12, 8))

    # Top: waveform overlay
    ax = axes[0]
    ax.plot(t * 1000, tone, color="gray", alpha=0.4, lw=0.5, label="Input")
    ax.plot(t * 1000, r_old, color="#DC3545", lw=1.5, label="Legacy (zero attack)")
    ax.plot(t * 1000, r_new, color="#0D6EFD", lw=1.5, label="New (1ms attack + lookahead)")
    ax.axhline(10**(-6.0/20.0), color="gray", ls=":", alpha=0.5)
    ax.axhline(-10**(-6.0/20.0), color="gray", ls=":", alpha=0.5)
    ax.set_xlabel("Time (ms)")
    ax.set_ylabel("Amplitude")
    ax.set_title("60 Hz Tone: Legacy vs New Limiter @ -6 dB Ceiling")
    ax.legend(fontsize=8)
    ax.grid(True, alpha=0.3)
    ax.set_xlim(40, 60)

    # Bottom: gain reduction envelope
    ax2 = axes[1]
    ax2.plot(t * 1000, 20 * np.log10(gain_old + 1e-15), color="#DC3545", lw=1.5, label="Legacy gain (zero attack)")
    ax2.plot(t * 1000, 20 * np.log10(gain_new + 1e-15), color="#0D6EFD", lw=1.5, label="New gain (1ms attack)")
    ax2.set_xlabel("Time (ms)")
    ax2.set_ylabel("Gain Reduction (dB)")
    ax2.set_title("Gain Reduction Envelope")
    ax2.legend(fontsize=8)
    ax2.grid(True, alpha=0.3)
    ax2.set_xlim(40, 60)

    fig.suptitle("AEP-ACU-005: Limiter Envelope Comparison", fontsize=13, fontweight="bold")
    fig.tight_layout()
    fig.savefig(str(OUT_DIR / "envelope_comparison.png"), dpi=150, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print("  -> envelope_comparison.png")


def plot_true_peak_curve():
    """Plot sample peak vs true peak across frequencies."""
    freqs = [100, 500, 1000, 2000, 5000, 8000, 10000, 12000, 15000, 18000]
    sp_vals, tp_vals = [], []
    dur = 0.5

    for f in freqs:
        t = np.arange(int(SR * dur)) / SR
        tone = np.sin(2 * np.pi * f * t) * 0.9
        sp = 20 * math.log10(np.max(np.abs(tone)) + 1e-15)
        tp = measure_true_peak(tone, SR, 4)
        sp_vals.append(sp)
        tp_vals.append(tp)

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.semilogx(freqs, sp_vals, "o-", color="#0D6EFD", lw=2, label="Sample Peak (dBFS)")
    ax.semilogx(freqs, tp_vals, "s-", color="#DC3545", lw=2, label="True Peak (dBTP)")
    ax.fill_between(freqs, sp_vals, tp_vals, alpha=0.2, color="#DC3545", label="Inter-Sample Peak Risk")
    ax.set_xlabel("Frequency (Hz)")
    ax.set_ylabel("Peak Level (dB)")
    ax.set_title("AEP-ACU-005: Sample Peak vs True Peak by Frequency (4x OS)")
    ax.legend(fontsize=9)
    ax.grid(True, alpha=0.3)
    ax.set_ylim(-5, 1)

    fig.tight_layout()
    fig.savefig(str(OUT_DIR / "true_peak_curve.png"), dpi=150, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print("  -> true_peak_curve.png")


def plot_thd_comparison():
    """THD sweep across different ceiling levels."""
    ceilings = [-1, -2, -3, -4, -6, -8, -12]
    thd_legacy, thd_new = [], []
    freq, dur = 60, 0.3
    t = np.arange(int(SR * dur)) / SR
    tone = np.sin(2 * np.pi * freq * t) * 0.9

    for c in ceilings:
        r_old = apply_limiter_legacy(tone, SR, ceiling_db=c, release_ms=50.0)
        r_new, _ = apply_limiter_tp(tone, SR, ceiling_dbtp=c, attack_ms=1.0, release_ms=50.0)
        thd_legacy.append(measure_low_freq_thd(r_old, SR))
        thd_new.append(measure_low_freq_thd(r_new, SR))

    fig, ax = plt.subplots(figsize=(9, 5))
    x = np.arange(len(ceilings))
    w = 0.35
    ax.bar(x - w/2, thd_legacy, w, color="#DC3545", label="Legacy (zero attack)")
    ax.bar(x + w/2, thd_new, w, color="#0D6EFD", label="New (1ms attack)")
    ax.set_xticks(x)
    ax.set_xticklabels([f"{c} dB" for c in ceilings])
    ax.set_xlabel("Ceiling")
    ax.set_ylabel("THD (%)")
    ax.set_title("AEP-ACU-005: Low-Frequency THD vs Ceiling (60 Hz)")
    ax.legend(fontsize=9)
    ax.grid(True, alpha=0.3, axis="y")

    fig.tight_layout()
    fig.savefig(str(OUT_DIR / "thd_before_after.png"), dpi=150, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print("  -> thd_before_after.png")


if __name__ == "__main__":
    print("Generating AEP-ACU-005 assets...")
    plot_envelope_comparison()
    plot_true_peak_curve()
    plot_thd_comparison()
    print("Done.")
