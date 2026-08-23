#!/usr/bin/env python3
"""
Moodify Audio Benchmark - Baseline Evaluation

This module provides baseline implementations for audio quality evaluation
following the Moodify Audio Benchmark protocol.

Usage:
    python baseline.py evaluate --input <audio_path> --output <result_path>
    python baseline.py batch --dataset <dataset_manifest> --output <results_dir>
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import warnings

# Optional dependencies - will warn if not available
try:
    import numpy as np
    HAS_NUMPY = True
except ImportError:
    HAS_NUMPY = False
    warnings.warn("numpy not available, some features disabled")

try:
    import librosa
    HAS_LIBROSA = True
except ImportError:
    HAS_LIBROSA = False
    warnings.warn("librosa not available, audio analysis disabled")


@dataclass
class TechnicalFeatures:
    """Technical audio features."""
    loudness_lufs: Optional[float] = None
    true_peak_db: Optional[float] = None
    dynamic_range_db: Optional[float] = None
    spectral_centroid_hz: Optional[float] = None
    spectral_rolloff_hz: Optional[float] = None
    zero_crossing_rate: Optional[float] = None
    rms_energy: Optional[float] = None

    def to_dict(self) -> Dict:
        return {k: v for k, v in asdict(self).items() if v is not None}


@dataclass
class MRSScore:
    """Moodify Reconstruction Score."""
    overall: Optional[float] = None
    fidelity: Optional[float] = None
    balance: Optional[float] = None
    clarity: Optional[float] = None
    version: str = "0.1.0"

    def to_dict(self) -> Dict:
        return {k: v for k, v in asdict(self).items() if v is not None}


@dataclass
class HumanRating:
    """Aggregated human evaluation scores."""
    mean_rating: Optional[float] = None
    std_dev: Optional[float] = None
    num_ratings: int = 0
    preference_rank: Optional[int] = None

    def to_dict(self) -> Dict:
        return {k: v for k, v in asdict(self).items() if v is not None}


@dataclass
class AudioSample:
    """Audio sample data structure."""
    id: str
    audio_path: str
    source: str
    genre: Optional[str] = None
    duration: Optional[float] = None
    sample_rate: Optional[int] = None
    channels: Optional[int] = None
    technical_features: Optional[TechnicalFeatures] = None
    mrs_score: Optional[MRSScore] = None
    human_rating: Optional[HumanRating] = None
    metadata: Optional[Dict] = None

    def to_dict(self) -> Dict:
        result = {
            "id": self.id,
            "audio_path": self.audio_path,
            "source": self.source,
        }
        if self.genre:
            result["genre"] = self.genre
        if self.duration is not None:
            result["duration"] = self.duration
        if self.sample_rate:
            result["sample_rate"] = self.sample_rate
        if self.channels:
            result["channels"] = self.channels
        if self.technical_features:
            result["technical_features"] = self.technical_features.to_dict()
        if self.mrs_score:
            result["mrs_score"] = self.mrs_score.to_dict()
        if self.human_rating:
            result["human_rating"] = self.human_rating.to_dict()
        if self.metadata:
            result["metadata"] = self.metadata
        return result


class AudioAnalyzer:
    """Analyze audio files and extract technical features."""

    def __init__(self):
        if not HAS_LIBROSA:
            raise RuntimeError("librosa required for audio analysis")

    def analyze(self, audio_path: Path) -> TechnicalFeatures:
        """Analyze audio file and return technical features."""
        # Load audio
        y, sr = librosa.load(str(audio_path), sr=None, mono=False)

        # Convert to mono for analysis if stereo
        if y.ndim > 1:
            y_mono = librosa.to_mono(y)
        else:
            y_mono = y

        features = TechnicalFeatures()

        # Compute features
        features.spectral_centroid_hz = float(np.mean(
            librosa.feature.spectral_centroid(y=y_mono, sr=sr)
        ))

        features.spectral_rolloff_hz = float(np.mean(
            librosa.feature.spectral_rolloff(y=y_mono, sr=sr)
        ))

        features.zero_crossing_rate = float(np.mean(
            librosa.feature.zero_crossing_rate(y_mono)
        ))

        features.rms_energy = float(np.mean(
            librosa.feature.rms(y=y_mono)
        ))

        # Duration
        features.duration = float(librosa.get_duration(y=y, sr=sr))

        return features

    def compute_loudness(self, audio_path: Path) -> Tuple[float, float]:
        """Compute loudness (LUFS) and true peak (dB)."""
        # Placeholder - would use pyloudnorm or ffmpeg
        warnings.warn("Loudness computation requires pyloudnorm")
        return -14.0, -1.0  # Placeholder values


class BaselineEvaluator:
    """Baseline evaluation following Moodify Benchmark protocol."""

    PROTOCOL_VERSION = "0.1.0"

    def __init__(self):
        self.analyzer = None
        if HAS_LIBROSA and HAS_NUMPY:
            self.analyzer = AudioAnalyzer()

    def evaluate_single(
        self,
        audio_path: Path,
        sample_id: Optional[str] = None,
        source: str = "unknown"
    ) -> AudioSample:
        """Evaluate a single audio file."""

        if sample_id is None:
            sample_id = audio_path.stem

        sample = AudioSample(
            id=sample_id,
            audio_path=str(audio_path),
            source=source
        )

        # Extract technical features if analyzer available
        if self.analyzer and audio_path.exists():
            try:
                features = self.analyzer.analyze(audio_path)
                sample.technical_features = features
                sample.duration = features.duration
            except Exception as e:
                warnings.warn(f"Failed to analyze {audio_path}: {e}")

        # Compute placeholder MRS score
        # In real implementation, this would call Moodify processing pipeline
        sample.mrs_score = MRSScore(
            overall=None,  # Would be computed
            version=self.PROTOCOL_VERSION
        )

        return sample

    def evaluate_batch(
        self,
        dataset_manifest: Path,
        output_dir: Path
    ) -> List[AudioSample]:
        """Evaluate a batch of audio files from dataset manifest."""

        # Load manifest
        with open(dataset_manifest) as f:
            manifest = json.load(f)

        samples = []
        dataset_root = dataset_manifest.parent

        for item in manifest.get("samples", []):
            audio_path = dataset_root / item["audio_path"]

            sample = self.evaluate_single(
                audio_path=audio_path,
                sample_id=item.get("id"),
                source=item.get("source", "unknown")
            )

            # Merge with existing metadata
            if "genre" in item:
                sample.genre = item["genre"]
            if "metadata" in item:
                sample.metadata = item["metadata"]

            samples.append(sample)

        # Save results
        output_dir.mkdir(parents=True, exist_ok=True)
        results_path = output_dir / "baseline_results.json"

        with open(results_path, "w") as f:
            json.dump(
                {
                    "protocol_version": self.PROTOCOL_VERSION,
                    "dataset_id": manifest.get("dataset_id"),
                    "num_samples": len(samples),
                    "samples": [s.to_dict() for s in samples]
                },
                f,
                indent=2
            )

        return samples

    def compute_benchmark_score(
        self,
        samples: List[AudioSample]
    ) -> Dict:
        """Compute aggregate benchmark scores."""

        if not samples:
            return {"error": "No samples provided"}

        scores = {
            "protocol_version": self.PROTOCOL_VERSION,
            "num_samples": len(samples),
            "technical": {},
            "mrs": {},
            "human": {}
        }

        # Technical features statistics
        tech_samples = [s for s in samples if s.technical_features]
        if tech_samples and HAS_NUMPY:
            for attr in ["spectral_centroid_hz", "spectral_rolloff_hz",
                        "zero_crossing_rate", "rms_energy"]:
                values = [
                    getattr(s.technical_features, attr)
                    for s in tech_samples
                    if getattr(s.technical_features, attr) is not None
                ]
                if values:
                    scores["technical"][attr] = {
                        "mean": float(np.mean(values)),
                        "std": float(np.std(values)),
                        "min": float(np.min(values)),
                        "max": float(np.max(values))
                    }

        # MRS scores
        mrs_samples = [s for s in samples if s.mrs_score and s.mrs_score.overall]
        if mrs_samples:
            scores["mrs"]["count"] = len(mrs_samples)

        # Human ratings
        human_samples = [s for s in samples if s.human_rating and s.human_rating.mean_rating]
        if human_samples:
            ratings = [s.human_rating.mean_rating for s in human_samples]
            scores["human"] = {
                "mean": float(np.mean(ratings)) if HAS_NUMPY else sum(ratings) / len(ratings),
                "count": len(human_samples)
            }

        return scores


def main():
    """Command-line interface."""
    parser = argparse.ArgumentParser(
        description="Moodify Audio Benchmark - Baseline Evaluation"
    )
    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # Single evaluation
    single_parser = subparsers.add_parser("evaluate", help="Evaluate single audio file")
    single_parser.add_argument("--input", "-i", required=True, help="Input audio path")
    single_parser.add_argument("--output", "-o", help="Output JSON path")
    single_parser.add_argument("--id", help="Sample ID")
    single_parser.add_argument("--source", default="unknown", help="Audio source")

    # Batch evaluation
    batch_parser = subparsers.add_parser("batch", help="Evaluate dataset")
    batch_parser.add_argument("--dataset", "-d", required=True, help="Dataset manifest path")
    batch_parser.add_argument("--output", "-o", required=True, help="Output directory")

    # Benchmark score
    score_parser = subparsers.add_parser("score", help="Compute benchmark score")
    score_parser.add_argument("--results", "-r", required=True, help="Results JSON path")
    score_parser.add_argument("--output", "-o", help="Output path")

    args = parser.parse_args()

    if args.command is None:
        parser.print_help()
        sys.exit(1)

    evaluator = BaselineEvaluator()

    if args.command == "evaluate":
        sample = evaluator.evaluate_single(
            audio_path=Path(args.input),
            sample_id=args.id,
            source=args.source
        )

        result = sample.to_dict()

        if args.output:
            with open(args.output, "w") as f:
                json.dump(result, f, indent=2)
            print(f"Result saved to {args.output}")
        else:
            print(json.dumps(result, indent=2))

    elif args.command == "batch":
        samples = evaluator.evaluate_batch(
            dataset_manifest=Path(args.dataset),
            output_dir=Path(args.output)
        )
        print(f"Evaluated {len(samples)} samples")
        print(f"Results saved to {Path(args.output) / 'baseline_results.json'}")

    elif args.command == "score":
        with open(args.results) as f:
            data = json.load(f)

        samples = [AudioSample(**s) for s in data.get("samples", [])]
        scores = evaluator.compute_benchmark_score(samples)

        if args.output:
            with open(args.output, "w") as f:
                json.dump(scores, f, indent=2)
        else:
            print(json.dumps(scores, indent=2))


if __name__ == "__main__":
    main()
