#!/usr/bin/env python3
"""
Example: Process audio file

Demonstrates how to use Moodify SDK to process audio.
"""

import sys
from pathlib import Path

# Add sdk to path (in real usage: pip install moodify-sdk)
sdk_path = Path(__file__).parent.parent / "python"
sys.path.insert(0, str(sdk_path))

from moodify import MoodifyClient
from moodify.exceptions import ValidationError, APIError, ProcessingError


def main():
    """Process audio example."""

    # Initialize client
    client = MoodifyClient(
        api_key="your-api-key-here",
        base_url="https://api.moodify.ai"
    )

    # Path to audio file
    input_path = "path/to/your/audio.wav"

    try:
        print(f"Processing: {input_path}")
        print("-" * 40)

        # Process audio with reconstruction
        result = client.process_audio(
            audio_path=input_path,
            operation="reconstruct",
            options={
                "quality": "high",
                "preserve_dynamics": True
            }
        )

        print(f"Processing ID: {result.id}")
        print(f"Operation: {result.operation}")
        print(f"Status: {result.status}")

        if result.is_completed:
            print(f"\n✓ Processing complete!")
            print(f"Output: {result.output_path}")

            if result.duration_seconds:
                print(f"Processing time: {result.duration_seconds:.2f}s")

        elif result.is_failed:
            print(f"\n✗ Processing failed")
            if result.error:
                print(f"Error: {result.error}")

        else:
            print(f"\n⏳ Processing in progress...")
            print(f"Progress: {result.progress}%")

        # Print metadata
        if result.metadata:
            print("\nMetadata:")
            for key, value in result.metadata.items():
                print(f"  {key}: {value}")

    except ValidationError as e:
        print(f"Validation error: {e}")
        sys.exit(1)
    except ProcessingError as e:
        print(f"Processing error: {e}")
        sys.exit(1)
    except APIError as e:
        print(f"API error: {e}")
        sys.exit(1)
    except FileNotFoundError:
        print(f"File not found: {input_path}")
        print("Please update the input_path variable with a valid file path.")
        sys.exit(1)


if __name__ == "__main__":
    main()
