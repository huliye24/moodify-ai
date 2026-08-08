"""Generate RBJ vs Legacy FFT EQ frequency response curves for AEP-ACU-002."""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import math
from pathlib import Path

OUT_DIR = Path(__file__).resolve().parent / "reports"
DATA_DIR = Path(__file__).resolve().parent / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)
OUT_DIR.mkdir(parents=True, exist_ok=True)

plt.rcParams["font.family"] = "Microsoft YaHei"
plt.rcParams["font.size"] = 9

C = {
    "rbj": "#0D6EFD",
    "fft": "#DC3545",
    "theory": "#198754",
    "bg": "#FFFFFF",
    "text": "#212529",
    "grid": "#E0E0E0",
}

SR = 44100.0


# ── Legacy FFT EQ curves (same logic as old _apply_shelf_freq / _apply_peak_freq) ──
def legacy_shelf_response(freqs, freq_hz, gain_db, stype):
    if abs(gain_db) < 0.1:
        return np.ones(len(freqs))
    gain_lin = 10.0 ** (gain_db / 20.0)
    if stype == "low":
        curve = 1.0 + (gain_lin - 1.0) * (1.0 / (1.0 + np.exp((freqs - freq_hz) / (freq_hz * 0.3))))
    else:
        curve = 1.0 + (gain_lin - 1.0) * (1.0 / (1.0 + np.exp(-(freqs - freq_hz) / (freq_hz * 0.3))))
    return curve


def legacy_peak_response(freqs, freq_hz, gain_db, q):
    if abs(gain_db) < 0.1:
        return np.ones(len(freqs))
    gain_lin = 10.0 ** (gain_db / 20.0)
    bw = freq_hz / max(q, 0.1)
    curve = 1.0 + (gain_lin - 1.0) * np.exp(-((freqs - freq_hz) / bw) ** 2)
    return curve


# ── RBJ EQ using our implementation ──
from moodify.processing.rbj_eq import (
    rbj_low_shelf_coeffs,
    rbj_high_shelf_coeffs,
    rbj_peaking_coeffs,
)


def rbj_response(coeff_fn, freqs_hz, *args):
    """Compute RBJ frequency response at specified frequencies using scipy freqz."""
    from scipy.signal import freqz
    b, a = coeff_fn(*args)
    # Evaluate at specific frequencies
    worN = 2 * math.pi * freqs_hz / SR
    _, h = freqz(b, a, worN=worN)
    return np.abs(h)


# ═══════════════════════════════════════════════════════════════════════
# Plot 1: Low Shelf Comparison (200 Hz, ±6 dB)
# ═══════════════════════════════════════════════════════════════════════
def plot_low_shelf():
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))

    for ax, gain_db, title_suffix in zip(axes, [6.0, -6.0], ["+6 dB", "-6 dB"]):
        freqs = np.logspace(1, 4.3, 500)

        # RBJ
        rbj_mag = rbj_response(rbj_low_shelf_coeffs, freqs, 200.0, 0.707, gain_db, SR)
        rbj_db = 20 * np.log10(rbj_mag + 1e-15)

        # Legacy FFT
        legacy_lin = legacy_shelf_response(freqs, 200.0, gain_db, "low")
        legacy_db = 20 * np.log10(legacy_lin + 1e-15)

        ax.semilogx(freqs, rbj_db, color=C["rbj"], lw=2, label="RBJ Biquad")
        ax.semilogx(freqs, legacy_db, color=C["fft"], lw=2, ls="--", label="Legacy FFT Sigmoid")

        ax.axvline(200, color="gray", ls=":", alpha=0.5)
        ax.axhline(gain_db, color="gray", ls=":", alpha=0.3)
        ax.axhline(0, color="gray", ls=":", alpha=0.3)

        ax.set_xlabel("Frequency (Hz)")
        ax.set_ylabel("Gain (dB)")
        ax.set_title(f"Low Shelf 200 Hz {title_suffix}")
        ax.legend(fontsize=8)
        ax.grid(True, alpha=0.3, color=C["grid"])
        ax.set_xlim(10, 20000)

    fig.suptitle("AEP-ACU-002: Low Shelf EQ — RBJ vs Legacy FFT",
                 fontsize=13, fontweight="bold", color=C["text"])
    fig.tight_layout()
    path = OUT_DIR / "aep_acu_002_low_shelf_comparison.png"
    fig.savefig(str(path), dpi=150, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print(f"  -> {path.name}")


# ═══════════════════════════════════════════════════════════════════════
# Plot 2: High Shelf Comparison (6 kHz, ±6 dB)
# ═══════════════════════════════════════════════════════════════════════
def plot_high_shelf():
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))

    for ax, gain_db, title_suffix in zip(axes, [6.0, -6.0], ["+6 dB", "-6 dB"]):
        freqs = np.logspace(1, 4.3, 500)

        rbj_mag = rbj_response(rbj_high_shelf_coeffs, freqs, 6000.0, 0.707, gain_db, SR)
        rbj_db = 20 * np.log10(rbj_mag + 1e-15)

        legacy_lin = legacy_shelf_response(freqs, 6000.0, gain_db, "high")
        legacy_db = 20 * np.log10(legacy_lin + 1e-15)

        ax.semilogx(freqs, rbj_db, color=C["rbj"], lw=2, label="RBJ Biquad")
        ax.semilogx(freqs, legacy_db, color=C["fft"], lw=2, ls="--", label="Legacy FFT Sigmoid")

        ax.axvline(6000, color="gray", ls=":", alpha=0.5)
        ax.axhline(gain_db, color="gray", ls=":", alpha=0.3)
        ax.axhline(0, color="gray", ls=":", alpha=0.3)

        ax.set_xlabel("Frequency (Hz)")
        ax.set_ylabel("Gain (dB)")
        ax.set_title(f"High Shelf 6 kHz {title_suffix}")
        ax.legend(fontsize=8)
        ax.grid(True, alpha=0.3, color=C["grid"])
        ax.set_xlim(10, 20000)

    fig.suptitle("AEP-ACU-002: High Shelf EQ — RBJ vs Legacy FFT",
                 fontsize=13, fontweight="bold", color=C["text"])
    fig.tight_layout()
    path = OUT_DIR / "aep_acu_002_high_shelf_comparison.png"
    fig.savefig(str(path), dpi=150, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print(f"  -> {path.name}")


# ═══════════════════════════════════════════════════════════════════════
# Plot 3: Peaking Comparison (1 kHz, Q=1.0, ±6 dB)
# ═══════════════════════════════════════════════════════════════════════
def plot_peaking():
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))

    combos = [(6.0, "+6 dB, Q=1.0"), (-6.0, "-6 dB, Q=1.0")]

    for ax, (gain_db, title_suffix) in zip(axes, combos):
        freqs = np.logspace(1, 4.3, 500)

        rbj_mag = rbj_response(rbj_peaking_coeffs, freqs, 1000.0, 1.0, gain_db, SR)
        rbj_db = 20 * np.log10(rbj_mag + 1e-15)

        legacy_lin = legacy_peak_response(freqs, 1000.0, gain_db, 1.0)
        legacy_db = 20 * np.log10(legacy_lin + 1e-15)

        ax.semilogx(freqs, rbj_db, color=C["rbj"], lw=2, label="RBJ Biquad")
        ax.semilogx(freqs, legacy_db, color=C["fft"], lw=2, ls="--", label="Legacy FFT Gaussian")

        ax.axvline(1000, color="gray", ls=":", alpha=0.5)
        ax.axhline(gain_db, color="gray", ls=":", alpha=0.3)
        ax.axhline(0, color="gray", ls=":", alpha=0.3)

        ax.set_xlabel("Frequency (Hz)")
        ax.set_ylabel("Gain (dB)")
        ax.set_title(f"Peaking 1 kHz {title_suffix}")
        ax.legend(fontsize=8)
        ax.grid(True, alpha=0.3, color=C["grid"])
        ax.set_xlim(10, 20000)

    fig.suptitle("AEP-ACU-002: Peaking EQ — RBJ vs Legacy FFT",
                 fontsize=13, fontweight="bold", color=C["text"])
    fig.tight_layout()
    path = OUT_DIR / "aep_acu_002_peaking_comparison.png"
    fig.savefig(str(path), dpi=150, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print(f"  -> {path.name}")


# ═══════════════════════════════════════════════════════════════════════
# Plot 4: All five RBJ filter types (showcase)
# ═══════════════════════════════════════════════════════════════════════
def plot_all_types():
    fig, ax = plt.subplots(1, 1, figsize=(12, 7))

    freqs = np.logspace(1, 4.3, 800)

    # Low shelf
    mag = rbj_response(rbj_low_shelf_coeffs, freqs, 200.0, 0.707, 6.0, SR)
    ax.semilogx(freqs, 20 * np.log10(mag + 1e-15), color="#0D6EFD", lw=2, label="Low Shelf 200 Hz +6 dB")

    # High shelf
    mag = rbj_response(rbj_high_shelf_coeffs, freqs, 6000.0, 0.707, -6.0, SR)
    ax.semilogx(freqs, 20 * np.log10(mag + 1e-15), color="#FD7E14", lw=2, label="High Shelf 6 kHz -6 dB")

    # Peaking
    mag = rbj_response(rbj_peaking_coeffs, freqs, 1000.0, 1.0, 6.0, SR)
    ax.semilogx(freqs, 20 * np.log10(mag + 1e-15), color="#198754", lw=2, label="Peaking 1 kHz +6 dB Q=1")

    # HPF
    from moodify.processing.rbj_eq import rbj_highpass_coeffs, rbj_lowpass_coeffs
    mag = rbj_response(rbj_highpass_coeffs, freqs, 80.0, 0.707, SR)
    ax.semilogx(freqs, 20 * np.log10(mag + 1e-15), color="#6F42C1", lw=2, label="High Pass 80 Hz Q=0.707")

    # LPF
    mag = rbj_response(rbj_lowpass_coeffs, freqs, 8000.0, 0.707, SR)
    ax.semilogx(freqs, 20 * np.log10(mag + 1e-15), color="#DC3545", lw=2, label="Low Pass 8 kHz Q=0.707")

    ax.axhline(0, color="gray", ls=":", alpha=0.3)
    ax.set_xlabel("Frequency (Hz)")
    ax.set_ylabel("Gain (dB)")
    ax.set_title("AEP-ACU-002: All Five RBJ Biquad Filter Types", fontsize=13,
                 fontweight="bold", color=C["text"])
    ax.legend(fontsize=7.5, loc="lower left")
    ax.grid(True, alpha=0.3, color=C["grid"])
    ax.set_xlim(10, 20000)
    ax.set_ylim(-40, 15)

    fig.tight_layout()
    path = OUT_DIR / "aep_acu_002_all_filter_types.png"
    fig.savefig(str(path), dpi=150, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print(f"  -> {path.name}")


# ═══════════════════════════════════════════════════════════════════════
# Plot 5: RBJ Peaking Q comparison (shows standard Q behaviour)
# ═══════════════════════════════════════════════════════════════════════
def plot_q_comparison():
    fig, ax = plt.subplots(1, 1, figsize=(12, 6))

    freqs = np.logspace(1, 4.3, 800)
    q_values = [0.5, 1.0, 2.0, 4.0]
    colors = ["#0D6EFD", "#198754", "#FD7E14", "#DC3545"]

    for q, color in zip(q_values, colors):
        mag = rbj_response(rbj_peaking_coeffs, freqs, 1000.0, q, 6.0, SR)
        db = 20 * np.log10(mag + 1e-15)
        ax.semilogx(freqs, db, color=color, lw=2, label=f"Q={q}")

        # Also show legacy for Q=1.0
        if q == 1.0:
            legacy_lin = legacy_peak_response(freqs, 1000.0, 6.0, 1.0)
            legacy_db = 20 * np.log10(legacy_lin + 1e-15)
            ax.semilogx(freqs, legacy_db, color="gray", lw=1.5, ls="--",
                       label="Legacy Gaussian (Q=1.0)")

    ax.axvline(1000, color="gray", ls=":", alpha=0.3)
    ax.axhline(6, color="gray", ls=":", alpha=0.2)
    ax.axhline(3, color="gray", ls=":", alpha=0.2)
    ax.axhline(0, color="gray", ls=":", alpha=0.2)
    ax.set_xlabel("Frequency (Hz)")
    ax.set_ylabel("Gain (dB)")
    ax.set_title("AEP-ACU-002: RBJ Peaking Q Comparison (1 kHz, +6 dB)",
                 fontsize=13, fontweight="bold", color=C["text"])
    ax.legend(fontsize=8)
    ax.grid(True, alpha=0.3, color=C["grid"])
    ax.set_xlim(50, 20000)
    ax.set_ylim(-2, 8)

    fig.tight_layout()
    path = OUT_DIR / "aep_acu_002_q_comparison.png"
    fig.savefig(str(path), dpi=150, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print(f"  -> {path.name}")


# ═══════════════════════════════════════════════════════════════════════
# Main
# ═══════════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    print("Generating AEP-ACU-002 frequency response curves...")
    plot_low_shelf()
    plot_high_shelf()
    plot_peaking()
    plot_all_types()
    plot_q_comparison()
    print("Done.")
