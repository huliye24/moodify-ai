"""Calibration Benchmark Builder.

Builds repeatable benchmark datasets comparing presets and craft chains
across genres and quality tiers. Uses existing local data only.
Part of ECHAIN-MOODIFY-MRS-EXTREME-017 / MHP-913.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class BenchmarkEntry:
    sample_id: str
    genre: str
    preset: str
    before_path: str
    after_path: str
    tier: str = "standard"  # quick, standard, deep, studio
    tags: list[str] = field(default_factory=list)
    notes: str = ""


@dataclass
class BenchmarkSet:
    set_id: str
    version: str
    description: str
    entries: list[BenchmarkEntry] = field(default_factory=list)
    generated_at: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)

    def summary(self) -> dict[str, Any]:
        genres = {}
        presets = {}
        tiers = {}
        for e in self.entries:
            genres[e.genre] = genres.get(e.genre, 0) + 1
            presets[e.preset] = presets.get(e.preset, 0) + 1
            tiers[e.tier] = tiers.get(e.tier, 0) + 1
        return {
            "set_id": self.set_id,
            "version": self.version,
            "total_entries": len(self.entries),
            "genres": genres,
            "presets": presets,
            "tiers": tiers,
        }

    def to_dict(self) -> dict[str, Any]:
        return {
            "set_id": self.set_id,
            "version": self.version,
            "description": self.description,
            "generated_at": self.generated_at,
            "metadata": self.metadata,
            "entries": [asdict(e) for e in self.entries],
        }

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "BenchmarkSet":
        entries = [BenchmarkEntry(**e) for e in d.get("entries", [])]
        return cls(
            set_id=d.get("set_id", ""),
            version=d.get("version", ""),
            description=d.get("description", ""),
            entries=entries,
            generated_at=d.get("generated_at", ""),
            metadata=d.get("metadata", {}),
        )


def create_benchmark_set(
    set_id: str,
    description: str,
    version: str = "1.0.0",
) -> BenchmarkSet:
    return BenchmarkSet(
        set_id=set_id,
        version=version,
        description=description,
        generated_at=_utc_now_iso(),
        metadata={"builder_version": "0.1.0"},
    )


def add_entry(
    bs: BenchmarkSet,
    sample_id: str,
    before_path: str,
    after_path: str,
    genre: str = "",
    preset: str = "",
    tier: str = "standard",
    tags: list[str] | None = None,
    notes: str = "",
) -> None:
    bs.entries.append(BenchmarkEntry(
        sample_id=sample_id,
        genre=genre,
        preset=preset,
        before_path=before_path,
        after_path=after_path,
        tier=tier,
        tags=tags or [],
        notes=notes,
    ))


def save_benchmark_set(bs: BenchmarkSet, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(bs.to_dict(), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def load_benchmark_set(path: Path) -> BenchmarkSet:
    d = json.loads(path.read_text(encoding="utf-8"))
    return BenchmarkSet.from_dict(d)


def filter_by_genre(bs: BenchmarkSet, genre: str) -> BenchmarkSet:
    filtered = BenchmarkSet(
        set_id=f"{bs.set_id}_{genre}",
        version=bs.version,
        description=f"{bs.description} (filtered: {genre})",
        generated_at=_utc_now_iso(),
        metadata=bs.metadata,
    )
    filtered.entries = [e for e in bs.entries if e.genre == genre]
    return filtered


def filter_by_preset(bs: BenchmarkSet, preset: str) -> BenchmarkSet:
    filtered = BenchmarkSet(
        set_id=f"{bs.set_id}_{preset}",
        version=bs.version,
        description=f"{bs.description} (filtered: {preset})",
        generated_at=_utc_now_iso(),
        metadata=bs.metadata,
    )
    filtered.entries = [e for e in bs.entries if e.preset == preset]
    return filtered


def filter_by_tier(bs: BenchmarkSet, tier: str) -> BenchmarkSet:
    filtered = BenchmarkSet(
        set_id=f"{bs.set_id}_{tier}",
        version=bs.version,
        description=f"{bs.description} (filtered: {tier})",
        generated_at=_utc_now_iso(),
        metadata=bs.metadata,
    )
    filtered.entries = [e for e in bs.entries if e.tier == tier]
    return filtered
