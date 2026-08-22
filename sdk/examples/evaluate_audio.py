"""
Example: Evaluate Audio Quality

Demonstrates how to evaluate audio quality using MRS.
"""

from pathlib import Path

from moodify import MoodifyClient
from moodify.exceptions import ValidationError, APIError


def main():
    """Evaluate audio quality example."""

    # Initialize client
    client = MoodifyClient(
        api_key="your-api-key-here",  # Replace with your key
        base_url="https://api.moodify.ai"
    )

    # Path to audio file
    audio_path = Path("audio.wav")  # Replace with your file

    if not audio_path.exists():
        print(f"Error: File not found: {audio_path}")
        return

    print(f"Evaluating: {audio_path}")
    print("-" * 40)

    try:
        # Evaluate audio quality
        result = client.evaluate_audio(audio_path)

        # Print MRS scores
        print("MRS Evaluation Results")
        print("=" * 40)
        print(f"Overall Score: {result.overall:.1f}/100")
        print(f"Fidelity:      {result.fidelity:.1f}/100")
        print(f"Balance:       {result.balance:.1f}/100")
        print(f"Clarity:       {result.clarity:.1f}/100")
        print(f"Version:       {result.version}")

        # Quality assessment
        print("\nQuality Assessment:")
        print("-" * 40)

        if result.is_high_quality:
            print("✓ High Quality Audio")
        elif result.is_acceptable:
            print("○ Acceptable Quality")
        else:
            print("✗ Low Quality - Improvements Recommended")

        # Get recommendations
        recommendations = result.get_recommendations()
        if recommendations:
            print("\nRecommendations:")
            for i, rec in enumerate(recommendations, 1):
                print(f"  {i}. {rec}")
        else:
            print("\nNo specific recommendations - audio looks good!")

        # Print additional details if available
        if result.details:
            print("\nAdditional Details:")
            for key, value in result.details.items():
                print(f"  {key}: {value}")

        print("\nEvaluation complete!")

    except ValidationError as e:
        print(f"Validation error: {e}")
    except APIError as e:
        print(f"API error: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")

    finally:
        client.close()


if __name__ == "__main__":
    main()
