"""Generate synthetic example audio for Moodify QA testing.

This script creates a synthetic audio file with known characteristics
for testing the QA system.
"""

import numpy as np
import soundfile as sf
from pathlib import Path


def generate_example_audio(
    duration: float = 10.0,
    sample_rate: int = 44100,
    output_path: str = "example.wav",
):
    """Generate a synthetic stereo audio file with mixed characteristics."""

    samples = int(duration * sample_rate)
    t = np.linspace(0, duration, samples)

    # Left channel: sine wave with harmonics
    left = (
        0.3 * np.sin(2 * np.pi * 440 * t) +  # A4
        0.2 * np.sin(2 * np.pi * 880 * t) +  # A5
        0.1 * np.sin(2 * np.pi * 1320 * t)   # E6
    )

    # Right channel: same with slight phase shift
    right = (
        0.3 * np.sin(2 * np.pi * 440 * t + 0.1) +
        0.2 * np.sin(2 * np.pi * 880 * t + 0.05) +
        0.1 * np.sin(2 * np.pi * 1320 * t + 0.02)
    )

    # Add some noise
    noise_level = 0.001
    left += np.random.normal(0, noise_level, samples)
    right += np.random.normal(0, noise_level, samples)

    # Normalize to prevent clipping
    max_val = max(np.max(np.abs(left)), np.max(np.abs(right)))
    left = left / max_val * 0.9
    right = right / max_val * 0.9

    # Combine into stereo
    stereo = np.column_stack([left, right])

    # Save
    sf.write(output_path, stereo, sample_rate, subtype='PCM_16')
    print(f"Generated: {output_path}")
    print(f"  Duration: {duration}s")
    print(f"  Sample rate: {sample_rate} Hz")
    print(f"  Channels: 2 (stereo)")


if __name__ == "__main__":
    output = Path(__file__).parent / "example.wav"
    generate_example_audio(output_path=str(output))
