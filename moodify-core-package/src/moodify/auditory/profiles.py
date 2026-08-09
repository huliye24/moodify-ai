"""Immutable scan profiles (DSK-MFY-AUDITORY-SCAN-001).

A profile is frozen by design: before and after scans must use the exact
same profile, identified by profile ID + canonical serialization + SHA-256.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass

from moodify.auditory.errors import ScanProfileNotFound, ScanProfileMismatch


@dataclass(frozen=True)
class ScanProfile:
    profile_id: str
    schema_version: str
    analysis_sample_rate: int
    audio_decode_format: str
    preserve_original_channels: bool
    spectrogram: dict
    frequency_views: tuple[str, ...]
    numerical_stft: dict
    timeline_window_seconds: float
    timeline_hop_seconds: float

    def canonical(self) -> str:
        return json.dumps(
            {
                "profile_id": self.profile_id,
                "schema_version": self.schema_version,
                "analysis_sample_rate": self.analysis_sample_rate,
                "audio_decode_format": self.audio_decode_format,
                "preserve_original_channels": self.preserve_original_channels,
                "spectrogram": self.spectrogram,
                "frequency_views": list(self.frequency_views),
                "numerical_stft": self.numerical_stft,
                "timeline_window_seconds": self.timeline_window_seconds,
                "timeline_hop_seconds": self.timeline_hop_seconds,
            },
            sort_keys=True,
            separators=(",", ":"),
        )

    def hash(self) -> str:
        return hashlib.sha256(self.canonical().encode("utf-8")).hexdigest()


MFY_WSE_SCAN_PROFILE_001 = ScanProfile(
    profile_id="MFY-WSE-SCAN-PROFILE-001",
    schema_version="1.0",
    analysis_sample_rate=48000,
    audio_decode_format="float32",
    preserve_original_channels=True,
    spectrogram={
        "width": 1600,
        "height": 760,
        "channel_mode": "combined",
        "amplitude_scale": "log",
        "color_map": "viridis",
        "window_function": "hann",
        "legend": True,
        "dynamic_range_db": 120,
        "upper_limit_dbfs": 0,
    },
    frequency_views=("linear", "logarithmic"),
    numerical_stft={
        "fft_size": 8192,
        "hop_length": 2048,
        "window_function": "hann",
        "center": True,
    },
    timeline_window_seconds=1.0,
    timeline_hop_seconds=0.5,
)

_PROFILES: dict[str, ScanProfile] = {
    MFY_WSE_SCAN_PROFILE_001.profile_id: MFY_WSE_SCAN_PROFILE_001,
}


def get_profile(profile_id: str) -> ScanProfile:
    profile = _PROFILES.get(profile_id)
    if profile is None:
        raise ScanProfileNotFound(f"scan profile not found: {profile_id}")
    return profile


def assert_profile_match(expected: ScanProfile, actual: ScanProfile) -> None:
    if expected.profile_id != actual.profile_id or expected.hash() != actual.hash():
        raise ScanProfileMismatch(
            "before/after scans must use the identical immutable scan profile"
        )
