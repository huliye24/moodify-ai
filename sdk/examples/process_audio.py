"""
Example: Process Audio

Demonstrates how to process audio with intelligent operations.
"""

from pathlib import Path

from moodify import MoodifyClient
from moodify.exceptions import ValidationError, APIError, ProcessingError


def main():
    """Process audio example."""

    # Initialize client
    client = MoodifyClient(
        api_key="your-api-key-here",  # Replace with your key
        base_url="https://api.moodify.ai"
    )

    # Path to input audio
    input_path = Path("input.wav")  # Replace with your file

    if not input_path.exists():
        print(f"Error: Input file not found: {input_path}")
        return

    # Choose operation
    operation = "reconstruct"  # Options: reconstruct, enhance, normalize

    print(f"Processing: {input_path}")
    print(f"Operation: {operation}")
    print("-" * 40)

    try:
        # Process audio
        result = client.process_audio(
            audio_path=input_path,
            operation=operation,
            options={
                "quality": "high",
                "preserve_dynamics": True
            }
        )

        # Print processing info
        print(f"Processing ID: {result.id}")
        print(f"Status: {result.status}")
        print(f"Input: {result.input_path}")
        print(f"Output: {result.output_path}")

        # Check status
        if result.is_completed:
            print("\n✓ Processing completed successfully!")

            # Print metadata
            if result.metadata:
                print("\nProcessing Metadata:")
                for key, value in result.metadata.items():
                    print(f"  {key}: {value}")

            # Calculate duration
            if result.duration_seconds:
                print(f"\nProcessing time: {result.duration_seconds:.2f} seconds")

            print("\nNext steps:")
            print(f"  - Download processed audio from: {result.output_path}")
            print("  - Evaluate quality with client.evaluate_audio()")

        elif result.is_failed:
            print(f"\n✗ Processing failed: {result.error}")

        else:
            print(f"\nProcessing status: {result.status}")
            print(f"Progress: {result.progress}%")

    except ValidationError as e:
        print(f"Validation error: {e}")
    except ProcessingError as e:
        print(f"Processing error: {e}")
    except APIError as e:
        print(f"API error: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")

    finally:
        client.close()


if __name__ == "__main__":
    main()
