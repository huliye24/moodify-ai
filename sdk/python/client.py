"""
Moodify Python SDK Client

Provides developer-friendly access to Moodify auditory intelligence capabilities.
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional, Union

from .models import AudioAnalysisResult, MRSResult, ProcessingResult
from .exceptions import APIError, ValidationError


class MoodifyClient:
    """
    Main client for Moodify API.

    Example:
        >>> client = MoodifyClient(api_key="your-key")
        >>> result = client.analyze_audio("audio.wav")
        >>> print(result.duration)

    Args:
        api_key: Moodify API key
        base_url: API base URL (default: https://api.moodify.ai)
        timeout: Request timeout in seconds (default: 30.0)
        max_retries: Maximum retry attempts (default: 3)
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: str = "https://api.moodify.ai",
        timeout: float = 30.0,
        max_retries: int = 3
    ):
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.max_retries = max_retries

        # Future: Initialize HTTP client
        # self._client = httpx.Client(
        #     base_url=self.base_url,
        #     timeout=self.timeout,
        #     headers={"Authorization": f"Bearer {self.api_key}"}
        # )

    def analyze_audio(
        self,
        audio_path: Union[str, Path],
        options: Optional[dict] = None
    ) -> AudioAnalysisResult:
        """
        Analyze audio file and extract auditory features.

        Args:
            audio_path: Path to audio file
            options: Analysis options (e.g., {"detailed": True})

        Returns:
            AudioAnalysisResult with extracted features

        Raises:
            ValidationError: If file is invalid
            APIError: If API request fails

        Example:
            >>> result = client.analyze_audio("song.wav")
            >>> print(result.spectral_centroid)
        """
        audio_path = Path(audio_path)

        if not audio_path.exists():
            raise ValidationError(f"Audio file not found: {audio_path}")

        # Future: Actual API call
        # response = self._client.post(
        #     "/api/v1/analyze",
        #     files={"audio": open(audio_path, "rb")}
        # )
        # return AudioAnalysisResult.from_response(response.json())

        # Placeholder implementation
        return AudioAnalysisResult(
            id="placeholder-id",
            audio_path=str(audio_path),
            duration=0.0,
            sample_rate=44100,
            features={},
            metadata={"status": "placeholder"}
        )

    def evaluate_audio(
        self,
        audio_path: Union[str, Path],
        reference_path: Optional[Union[str, Path]] = None
    ) -> MRSResult:
        """
        Evaluate audio quality using MRS (Moodify Reconstruction Score).

        Args:
            audio_path: Path to audio file to evaluate
            reference_path: Optional reference audio for comparison

        Returns:
            MRSResult with quality scores

        Raises:
            ValidationError: If file is invalid
            APIError: If API request fails

        Example:
            >>> result = client.evaluate_audio("processed.wav")
            >>> print(f"MRS Score: {result.overall}")
        """
        audio_path = Path(audio_path)

        if not audio_path.exists():
            raise ValidationError(f"Audio file not found: {audio_path}")

        # Future: Actual API call
        # response = self._client.post(
        #     "/api/v1/evaluate",
        #     files={"audio": open(audio_path, "rb")}
        # )
        # return MRSResult.from_response(response.json())

        # Placeholder implementation
        return MRSResult(
            id="placeholder-id",
            audio_path=str(audio_path),
            overall=0.0,
            fidelity=0.0,
            balance=0.0,
            clarity=0.0,
            version="0.1.0"
        )

    def process_audio(
        self,
        audio_path: Union[str, Path],
        operation: str = "reconstruct",
        options: Optional[dict] = None
    ) -> ProcessingResult:
        """
        Process audio with intelligent operations.

        Args:
            audio_path: Path to audio file
            operation: Processing operation ("reconstruct", "enhance", etc.)
            options: Processing options

        Returns:
            ProcessingResult with processed audio info

        Raises:
            ValidationError: If file or operation is invalid
            APIError: If API request fails

        Example:
            >>> result = client.process_audio(
            ...     "input.wav",
            ...     operation="reconstruct"
            ... )
            >>> print(result.output_path)
        """
        audio_path = Path(audio_path)

        if not audio_path.exists():
            raise ValidationError(f"Audio file not found: {audio_path}")

        # Future: Actual API call
        # response = self._client.post(
        #     "/api/v1/process",
        #     files={"audio": open(audio_path, "rb")},
        #     data={"operation": operation, "options": options}
        # )
        # return ProcessingResult.from_response(response.json())

        # Placeholder implementation
        return ProcessingResult(
            id="placeholder-id",
            input_path=str(audio_path),
            output_path="placeholder-output.wav",
            operation=operation,
            status="completed",
            metadata={}
        )

    def health_check(self) -> dict:
        """
        Check API health status.

        Returns:
            Dict with status information

        Example:
            >>> status = client.health_check()
            >>> print(status["status"])
        """
        # Future: Actual API call
        # response = self._client.get("/health")
        # return response.json()

        return {"status": "ok", "version": "0.1.0"}

    def close(self) -> None:
        """Close client and release resources."""
        # Future: self._client.close()
        pass

    def __enter__(self) -> MoodifyClient:
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Context manager exit."""
        self.close()


class AsyncMoodifyClient:
    """
    Async client for Moodify API (Future implementation).

    Example:
        >>> async with AsyncMoodifyClient(api_key="xxx") as client:
        ...     result = await client.analyze_audio("audio.wav")
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: str = "https://api.moodify.ai",
        timeout: float = 30.0
    ):
        self.api_key = api_key
        self.base_url = base_url
        self.timeout = timeout
        # Future: self._client = httpx.AsyncClient(...)

    async def analyze_audio(
        self,
        audio_path: Union[str, Path],
        options: Optional[dict] = None
    ) -> AudioAnalysisResult:
        """Async analyze audio."""
        raise NotImplementedError("Async client coming in future version")

    async def evaluate_audio(
        self,
        audio_path: Union[str, Path],
        reference_path: Optional[Union[str, Path]] = None
    ) -> MRSResult:
        """Async evaluate audio."""
        raise NotImplementedError("Async client coming in future version")

    async def process_audio(
        self,
        audio_path: Union[str, Path],
        operation: str = "reconstruct",
        options: Optional[dict] = None
    ) -> ProcessingResult:
        """Async process audio."""
        raise NotImplementedError("Async client coming in future version")

    async def close(self) -> None:
        """Close async client."""
        pass

    async def __aenter__(self) -> AsyncMoodifyClient:
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Async context manager exit."""
        await self.close()
