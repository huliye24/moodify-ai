"""Service layer for the experimental auditory-intelligence API facade."""

from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path
from typing import Any

from fastapi import UploadFile

from moodify.mrs import MRSBenchmark, MRSFeatures
from moodify.v01_analyzer import analyze

from ..schemas.audio import AudioAnalysisResponse, AudioRequest, MRSResponse


class AudioService:
    """Adapt upload data to existing analysis and experimental MRS contracts.

    This service deliberately does not invoke processing. It provides a narrow
    API boundary so a future model, GPU worker, or remote execution adapter can
    replace an implementation without putting business logic in route modules.
    """

    _ALLOWED_SUFFIXES = {".wav", ".mp3", ".flac", ".m4a", ".ogg", ".aac"}

    def __init__(self, max_upload_bytes: int | None = None) -> None:
        default_limit = 50 * 1024 * 1024
        self._max_upload_bytes = max_upload_bytes or int(
            os.environ.get("MOODIFY_MAX_UPLOAD_BYTES", str(default_limit))
        )

    async def analyze_upload(
        self,
        audio: UploadFile,
        request: AudioRequest,
    ) -> AudioAnalysisResponse:
        """Run the existing v0.1 analysis engine against a bounded temp file."""
        suffix = self._validate_filename(request.file)
        content = await audio.read(self._max_upload_bytes + 1)
        if len(content) > self._max_upload_bytes:
            raise ValueError("AUDIO_TOO_LARGE")
        if not content:
            raise ValueError("AUDIO_EMPTY")

        with tempfile.TemporaryDirectory(prefix="moodify-api-") as temp_dir:
            source = Path(temp_dir) / f"upload{suffix}"
            source.write_bytes(content)
            metrics = analyze(str(source), output_dir=temp_dir).to_dict()

        return AudioAnalysisResponse(
            duration=metrics["duration_s"],
            format=suffix.removeprefix("."),
            features={
                "sample_rate": metrics["sample_rate"],
                "channels": metrics["channels"],
                "spectrum": metrics["spectrum"],
                "dynamics": metrics["dynamics"],
                "stereo": metrics["stereo"],
            },
        )

    async def evaluate_upload(
        self,
        audio: UploadFile,
        request: AudioRequest,
        normalized_features_json: str | None = None,
    ) -> MRSResponse:
        """Analyze audio and invoke MRS only with explicit normalized features."""
        analysis = await self.analyze_upload(audio, request)
        features = self._parse_normalized_features(normalized_features_json)
        benchmark = MRSBenchmark().evaluate(request.file, features)
        result = benchmark.to_dict()
        return MRSResponse(
            score=result["quality_score"],
            metrics={"acoustic_features": analysis.features, "mrs": result},
            status=result["status"],
            method=result["method"],
        )

    @classmethod
    def _validate_filename(cls, filename: str) -> str:
        suffix = Path(filename).suffix.lower()
        if suffix not in cls._ALLOWED_SUFFIXES:
            raise ValueError("AUDIO_TYPE_UNSUPPORTED")
        return suffix

    @staticmethod
    def _parse_normalized_features(value: str | None) -> MRSFeatures | None:
        """Parse explicit MRS inputs; never infer preference from raw metrics."""
        if value is None or not value.strip():
            return None
        try:
            payload: Any = json.loads(value)
        except json.JSONDecodeError as exc:
            raise ValueError("MRS_FEATURES_INVALID") from exc
        if not isinstance(payload, dict):
            raise ValueError("MRS_FEATURES_INVALID")
        try:
            return MRSFeatures.from_mapping(payload)
        except (TypeError, ValueError) as exc:
            raise ValueError("MRS_FEATURES_INVALID") from exc
