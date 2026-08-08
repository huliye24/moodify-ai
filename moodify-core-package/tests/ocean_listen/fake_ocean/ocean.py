#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("audio")
    parser.add_argument("--mode")
    parser.add_argument("--output", required=True)
    parser.add_argument("--cache-dir", required=True)
    parser.add_argument("--deep", action="store_true")
    parser.add_argument("--lyric")
    parser.add_argument("--lyric-value")
    parser.add_argument("--language")
    parser.add_argument("--whisper-model")
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()

    report = {
        "name": Path(args.audio).stem,
        "sourcePath": str(Path(args.audio).resolve()),
        "duration": 1.0,
        "bpm": 100,
        "key": "C",
        "classification": {
            "type": "music",
            "confidence": 0.9,
            "reasoning": "fake process",
            "details": {},
        },
        "notes": [
            {
                "pitch": 60,
                "start": 0.0,
                "end": 0.5,
                "duration": 0.5,
                "velocity": 90,
                "dynamics": {"mean_rms": 0.1},
            }
        ],
        "total_notes": 1,
        "shallowVersion": 1,
    }
    if args.deep:
        report["deepVersion"] = 1
        report["stemTimeline"] = {"vocals": [[0.0, 1.0]]}
        report["stemNotes"] = {"vocals": report["notes"]}
        report["totalStemNotes"] = 1

    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report), encoding="utf-8")
    print("fake ocean complete")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
