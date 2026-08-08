"""CLIDAWProject — strict schema, CLI-first, no GUI dependency."""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class SourceSpec:
    path: str
    hash: str = ""


@dataclass
class Clip:
    clip_id: str
    source_offset_s: float = 0.0
    position_s: float = 0.0
    duration_s: float = 0.0
    fade_in_s: float = 0.0
    fade_out_s: float = 0.0
    gain_db: float = 0.0
    pan: float = 0.0
    mute: bool = False
    solo: bool = False


@dataclass
class Track:
    track_id: str
    name: str = ""
    source: SourceSpec = field(default_factory=SourceSpec)
    clips: list[Clip] = field(default_factory=list)
    gain_db: float = 0.0
    pan: float = 0.0
    mute: bool = False
    solo: bool = False


@dataclass
class ProcessingNode:
    node_id: str
    type: str  # gain, eq, compressor, limiter, fade_in, fade_out, resample, mix
    order: int = 0
    params: dict = field(default_factory=dict)


@dataclass
class Bus:
    bus_id: str
    name: str = ""
    sends: list[dict] = field(default_factory=list)  # [{track_id, gain_db}]


@dataclass
class MasterSpec:
    processing: list[ProcessingNode] = field(default_factory=list)


@dataclass
class RenderSpec:
    sample_rate: int = 44100
    bit_depth: int = 24
    format: str = "wav"


@dataclass
class CLIDAWProject:
    schema_version: str = "1.0.0"
    project_id: str = ""
    sample_rate: int = 44100
    tempo: float | None = None
    tracks: list[Track] = field(default_factory=list)
    buses: list[Bus] = field(default_factory=list)
    master: MasterSpec = field(default_factory=MasterSpec)
    processing: dict[str, list[ProcessingNode]] = field(default_factory=dict)
    render: RenderSpec = field(default_factory=RenderSpec)

    def validate(self) -> None:
        track_ids = {t.track_id for t in self.tracks}
        clip_ids = {c.clip_id for t in self.tracks for c in t.clips}
        if len(clip_ids) != sum(len(t.clips) for t in self.tracks):
            raise ValueError("Duplicate clip_id in project")
        if len(track_ids) != len(self.tracks):
            raise ValueError("Duplicate track_id in project")
        for t in self.tracks:
            if not t.source.path:
                raise ValueError(f"Track {t.track_id} has no source.path")
        for bus in self.buses:
            for send in bus.sends:
                if send.get("track_id") not in track_ids:
                    raise ValueError(f"Bus {bus.bus_id} send references unknown track {send.get('track_id')}")
        for node in self.master.processing:
            if node.type not in ("gain", "eq", "compressor", "limiter"):
                raise ValueError(f"Unsupported master processing type: {node.type}")
