from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any
import json
import sys

PINNED_OCEAN_REPOSITORY = "https://github.com/ennisaaaaaaaa-stack/ocean-listen.git"
PINNED_OCEAN_COMMIT = "928dfba62a2c074ccb0154f7ddd42743e4ce9e75"


@dataclass(frozen=True)
class OceanRunOptions:
    ocean_root: Path
    output_root: Path
    cache_root: Path | None = None
    python_executable: str = sys.executable
    deep: bool = False
    mode: str = "auto"
    lyric: str | None = None
    lyric_value: str | None = None
    language: str = "auto"
    whisper_model: str = "small"
    force: bool = False
    timeout_seconds: int = 1800
    expected_commit: str | None = PINNED_OCEAN_COMMIT
    extra_env: dict[str, str] = field(default_factory=dict)
    analysis_profile: str = "shallow"
    lyrics_mode: str = "disabled"
    allow_unreviewed_commit: bool = False

    def validate(self) -> None:
        if self.mode not in {"auto", "music", "solo", "voice", "mixed"}:
            raise ValueError(f"Unsupported Ocean mode: {self.mode}")
        if self.lyric not in {None, "auto", "whisper", "sensevoice", "netease"}:
            raise ValueError(f"Unsupported lyric mode: {self.lyric}")
        if self.analysis_profile not in {"shallow", "deep"}:
            raise ValueError(f"Unsupported analysis profile: {self.analysis_profile}")
        if self.lyrics_mode not in {"disabled", "auto", "whisper", "sensevoice", "netease"}:
            raise ValueError(f"Unsupported lyrics mode: {self.lyrics_mode}")
        if self.timeout_seconds < 1:
            raise ValueError("timeout_seconds must be positive")

    @classmethod
    def from_json(cls, path: str | Path, **overrides: Any) -> "OceanRunOptions":
        data = json.loads(Path(path).read_text(encoding="utf-8"))
        data.update({k: v for k, v in overrides.items() if v is not None})
        for field_name in ("ocean_root", "output_root", "cache_root"):
            if data.get(field_name) is not None:
                data[field_name] = Path(data[field_name])
        return cls(**data)
