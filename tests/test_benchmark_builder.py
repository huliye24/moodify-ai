"""Tests for benchmark_builder — calibration benchmark dataset manager."""
import json
import tempfile
from pathlib import Path

from moodify_runtime.benchmark_builder import (
    BenchmarkSet,
    BenchmarkEntry,
    create_benchmark_set,
    add_entry,
    save_benchmark_set,
    load_benchmark_set,
    filter_by_genre,
    filter_by_preset,
    filter_by_tier,
)


class TestBenchmarkSet:
    def test_create_empty(self):
        bs = create_benchmark_set("calibration_v1", "Initial calibration set")
        assert bs.set_id == "calibration_v1"
        assert bs.version == "1.0.0"
        assert bs.entries == []
        assert bs.generated_at != ""

    def test_add_entry(self):
        bs = create_benchmark_set("test_set", "Test")
        add_entry(bs, "S1", "/tmp/before.wav", "/tmp/after.wav",
                  genre="piano", preset="warm", tier="standard")
        assert len(bs.entries) == 1
        assert bs.entries[0].genre == "piano"
        assert bs.entries[0].preset == "warm"

    def test_summary(self):
        bs = create_benchmark_set("test_set", "Test")
        add_entry(bs, "S1", "/a.wav", "/b.wav", genre="piano", preset="warm")
        add_entry(bs, "S2", "/c.wav", "/d.wav", genre="vocal", preset="clean")
        add_entry(bs, "S3", "/e.wav", "/f.wav", genre="piano", preset="wide")
        s = bs.summary()
        assert s["total_entries"] == 3
        assert s["genres"]["piano"] == 2
        assert s["genres"]["vocal"] == 1
        assert s["presets"]["warm"] == 1

    def test_save_and_load(self):
        d = tempfile.mkdtemp()
        p = Path(d) / "benchmark.json"
        bs = create_benchmark_set("test", "Desc")
        add_entry(bs, "S1", "/a.wav", "/b.wav")
        save_benchmark_set(bs, p)
        loaded = load_benchmark_set(p)
        assert loaded.set_id == "test"
        assert len(loaded.entries) == 1

    def test_filter_by_genre(self):
        bs = create_benchmark_set("test", "Desc")
        add_entry(bs, "S1", "/a.wav", "/b.wav", genre="piano")
        add_entry(bs, "S2", "/c.wav", "/d.wav", genre="vocal")
        filtered = filter_by_genre(bs, "piano")
        assert len(filtered.entries) == 1
        assert filtered.entries[0].genre == "piano"

    def test_filter_by_preset(self):
        bs = create_benchmark_set("test", "Desc")
        add_entry(bs, "S1", "/a.wav", "/b.wav", preset="warm")
        add_entry(bs, "S2", "/c.wav", "/d.wav", preset="clean")
        filtered = filter_by_preset(bs, "warm")
        assert len(filtered.entries) == 1

    def test_filter_by_tier(self):
        bs = create_benchmark_set("test", "Desc")
        add_entry(bs, "S1", "/a.wav", "/b.wav", tier="quick")
        add_entry(bs, "S2", "/c.wav", "/d.wav", tier="deep")
        filtered = filter_by_tier(bs, "deep")
        assert len(filtered.entries) == 1
