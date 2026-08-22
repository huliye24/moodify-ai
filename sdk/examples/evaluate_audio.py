#!/usr/bin/env python3
"""
Example: Evaluate audio quality with MRS

Demonstrates how to use Moodify SDK to evaluate audio quality.
"""

import sys
from pathlib import Path

# Add sdk to path (in real usage: pip install moodify-sdk)
sdk_path = Path(__file__).parent.parent / "python"
sys.path.insert(0, str(sdk_path))

from moodify import MoodifyClient
from moodify.exceptions import ValidationError, APIError


def main():
    """Evaluate audio example."""

    # Initialize client
    client = MoodifyClient(
        api_key="your-api-key-here",
        base_url="https://api.moodify.ai"
    )

    # Path to audio file
    audio_path = "path/to/your/audio.wav"

    try:
        print(f"Evaluating: {audio_path}")
        print("-" * 40)

        # Evaluate audio quality
        result = client.evaluate_audio(audio_path)

        # Print MRS scores
        print(f"Evaluation ID: {result.id}")
        print(f"MRS Version: {result.version}")
        print()
        print("Scores (0-100):")
        print(f"  Overall:   {result.overall:.1f}")
        print(f"  Fidelity:  {result.fidelity:.1f}")
        print(f"  Balance:   {result.balance:.1f}")
        print(f"  Clarity:   {result.clarity:.1f}")

        # Quality assessment
        print()
        if result.is_high_quality:
            print("✓ High quality audio")
        elif result.is_acceptable:
            print("✓ Acceptable quality")
        else:
            print("⚠ Quality needs improvement")

        # Get recommendations
        recommendations = result.get_recommendations()
        if recommendations:
            print("\nRecommendations:")
            for rec in recommendations:
                print(f"  - {rec}")

        print("\nEvaluation complete!")

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
