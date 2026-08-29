"""MAMSE-010 tensor views: homogeneous channel-spectral view.

The spectral view is TIME x FREQUENCY x CHANNEL over linear power on a
single log-frequency axis — a coherent space for multilinear research.
The transform is computed once per source (reused pipeline, no repeat
full-track STFT).
"""

from __future__ import annotations

import numpy as np
from scipy.signal import stft

from .contracts import AxisSpec, TensorField, TensorContractError

_LOG_FMIN_HZ = 55.0
_LOG_FMAX_HZ = 16000.0
_BANDS_PER_OCTAVE = 12
_AUDIO_N_FFT = 2048
_AUDIO_HOP = 256


def log_frequency_axis(sr: int) -> np.ndarray:
    fmax = min(_LOG_FMAX_HZ, sr / 2 - 1.0)
    octaves = np.log2(fmax / _LOG_FMIN_HZ)
    n = int(np.floor(octaves * _BANDS_PER_OCTAVE)) + 1
    return _LOG_FMIN_HZ * 2.0 ** (np.arange(n) / _BANDS_PER_OCTAVE)


def _channel_power_surface(ch: np.ndarray, sr: int) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    freqs, times, z = stft(ch, fs=sr, window="hann", nperseg=_AUDIO_N_FFT,
                           noverlap=_AUDIO_N_FFT - _AUDIO_HOP, nfft=_AUDIO_N_FFT,
                           boundary=None, padded=False)
    power = np.abs(z) ** 2
    target = log_frequency_axis(sr)
    valid = (freqs >= _LOG_FMIN_HZ) & (freqs <= min(_LOG_FMAX_HZ, sr / 2))
    src_f = freqs[valid]
    src = power[valid]
    out = np.empty((target.size, times.size), dtype=np.float64)
    for i in range(times.size):
        out[:, i] = np.interp(target, src_f, src[:, i])
    return out, times, target


def build_channel_spectral_tensor(
    samples: np.ndarray,
    sr: int,
    *,
    frame_decimation: int = 16,
) -> TensorField:
    """TIME x FREQUENCY x CHANNEL linear-power view (decimated frames).

    One STFT per channel per source. The returned field is fully observed
    (no NaN) and suitable for HOSVD.
    """
    samples = np.asarray(samples, dtype=np.float64)
    if samples.ndim != 2 or samples.shape[1] < 1:
        raise TensorContractError("samples must be [samples, channels]")
    if samples.shape[1] > 2:
        samples = samples[:, :2]
    surfaces, target = [], None
    for c in range(samples.shape[1]):
        s, t, target = _channel_power_surface(samples[:, c], sr)
        surfaces.append(s)
    stack = np.stack(surfaces, axis=2)  # [freq, time, channel]
    stack = stack[:, ::frame_decimation, :]
    time_s = t[::frame_decimation]

    axes = (
        AxisSpec("time", tuple(time_s.tolist()), unit="s", semantic_type="frame_center",
                 interpolation_policy="decimation"),
        AxisSpec("frequency", tuple(target.tolist()), unit="hz", semantic_type="log_frequency",
                 ordered=True, interpolation_policy="log_interp"),
        AxisSpec("channel", tuple(range(samples.shape[1])), unit="id", semantic_type="channel"),
    )
    return TensorField(
        "channel_spectral_view",
        np.moveaxis(stack, 0, 1),  # [time, freq, channel]
        axes,
        valid_mask=None,  # fully observed
        unit="linear_power",
        authority_class="EXPERIMENTAL_VIEW",
        provenance={"frame_decimation": frame_decimation, "n_fft": _AUDIO_N_FFT, "hop": _AUDIO_HOP,
                    "fmin_hz": _LOG_FMIN_HZ, "fmax_hz": _LOG_FMAX_HZ, "bands_per_octave": _BANDS_PER_OCTAVE},
    )
