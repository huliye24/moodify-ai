#!/usr/bin/env python3
"""
Example: Analyze audio file

Demonstrates how to use Moodify SDK to analyze audio.
"""

import sys
from pathlib import Path

# Add sdk to path (in real usage: pip install moodify-sdk)
sdk_path = Path(__file__).parent.parent / "python"
sys.path.insert(0, str(sdk_path))

from moodify import MoodifyClient
from moodify.exceptions import ValidationError, APIError


def main():
    """Analyze audio example."""

    # Initialize client
    # In production, use environment variable for API key
    client = MoodifyClient(
        api_key="your-api-key-here",
        base_url="https://api.moodify.ai"
    )

    # Path to audio file
    audio_path = "path/to/your/audio.wav"

    try:
        print(f"Analyzing: {audio_path}")
        print("-" * 40)

        # Analyze audio
        result = client.analyze_audio(audio_path)

        # Print results
        print(f"Analysis ID: {result.id}")
        print(f"Duration: {result.duration:.2f} seconds")
        print(f"Sample Rate: {result.sample_rate} Hz")

        # Print features if available
        if result.features:
            print("\nFeatures:")
            for key, value in result.features.items():
                if isinstance(value, (int, float)):
                    print(f"  {key}: {value:.4f}")
                else:
                    print(f"  {key}: {value}")

        # Access specific features
        if result.spectral_centroid:
            print(f"\nSpectral Centroid: {result.spectral_centroid:.2f} Hz")

        if result.loudness_lufs:
            print(f"Loudness: {result.loudness_lufs:.2f} LUFS")

        print("\nAnalysis complete!")

    except ValidationError as e:
        print(f"Validation error: {e}")
        sys.exit(1)
    except APIError as e:
        print(f"API error: {e}")
        sys.exit(1)
    except FileNotFoundError:
        print(f"File not found: {audio_path}")
        print("Please update the audio_path variable with a valid file path.")
        sys.exit(1)


if __name__ == "__main__":
    main()
