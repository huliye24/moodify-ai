"""Provider adapters — translate capability contracts into provider calls.

Provider names never leak above this layer (Law 5). Each adapter keeps
provider-specific knowledge: command construction, version probing, error
translation, known failure modes.
"""

from moodify.capability_registry.adapters.base import (
    AdapterResult,
    ControlledProcessAdapter,
    InvokeRequest,
    ProviderAdapter,
)
from moodify.capability_registry.adapters.musescore_adapter import MuseScoreAdapter
from moodify.capability_registry.adapters.ffmpeg_adapter import FfmpegAdapter, FfprobeAdapter
from moodify.capability_registry.adapters.sox_adapter import SoxAdapter
from moodify.capability_registry.adapters.rubberband_adapter import RubberBandAdapter
from moodify.capability_registry.adapters.audacity_adapter import AudacityAdapter
from moodify.capability_registry.adapters.basic_pitch_adapter import BasicPitchAdapter

__all__ = [
    "AdapterResult",
    "AudacityAdapter",
    "BasicPitchAdapter",
    "ControlledProcessAdapter",
    "FfmpegAdapter",
    "FfprobeAdapter",
    "InvokeRequest",
    "MuseScoreAdapter",
    "ProviderAdapter",
    "RubberBandAdapter",
    "SoxAdapter",
]


def all_adapters() -> list[ProviderAdapter]:
    return [
        MuseScoreAdapter(),
        FfmpegAdapter(),
        FfprobeAdapter(),
        SoxAdapter(),
        RubberBandAdapter(),
        AudacityAdapter(),
        BasicPitchAdapter(),
    ]
