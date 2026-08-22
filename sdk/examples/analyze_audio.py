"""
Example: Analyze Audio

Demonstrates how to analyze audio and extract features.
"""

from pathlib import Path

from moodify import MoodifyClient
from moodify.exceptions import ValidationError, APIError


def main():
    """Analyze audio file example."""

    # Initialize client
    # In production, use your actual API key
    client = MoodifyClient(
        api_key="your-api-key-here",  # Replace with your key
        base_url="https://api.moodify.ai"
    )

    # Path to audio file
    audio_path = Path("audio.wav")  # Replace with your file

    # Check if file exists
    if not audio_path.exists():
        print(f"Error: File not found: {audio_path}")
        print("Please provide a valid audio file path.")
        return

    print(f"Analyzing: {audio_path}")
    print("-" * 40)

    try:
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
                if isinstance(value, dict):
                    print(f"  {key}:")
                    for sub_key, sub_value in value.items():
                        print(f"    {sub_key}: {sub_value}")
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
    except APIError as e:
        print(f"API error: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")

    finally:
        # Close client
        client.close()


if __name__ == "__main__":
    main()
