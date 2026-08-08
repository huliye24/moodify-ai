"""CLI handlers for the score engine (moodify score ...)."""

from __future__ import annotations

import json
from pathlib import Path

from moodify.score_engine.midi_ingest import MidiParseError, ingest_midi
from moodify.score_engine.musescore_backend import list_backends
from moodify.score_engine.roundtrip import build_roundtrip_report
from moodify.score_engine.serialization import dumps, with_assigned_id


def cmd_score_import_midi(args) -> int:
    source = Path(args.midi)
    if not source.exists():
        print(f"ERROR: File not found: {source}")
        return 1
    out = Path(args.output)
    if out.exists():
        print(f"ERROR: refusing to overwrite: {out}")
        return 2
    try:
        score = with_assigned_id(ingest_midi(source))
    except (MidiParseError, FileNotFoundError, ValueError) as exc:
        print(f"ERROR: {exc}")
        return 2
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(dumps(score), encoding="utf-8")
    print(f"Imported {source.name} -> {out}")
    print(f"  score_id: {score.score_id}  parts: {len(score.parts)}")
    return 0


def cmd_score_export(args) -> int:
    from moodify.score_engine.serialization import loads

    score_path = Path(args.score)
    if not score_path.exists():
        print(f"ERROR: Score file not found: {score_path}")
        return 1
    try:
        score = loads(score_path.read_text(encoding="utf-8"))
    except ValueError as exc:
        print(f"ERROR: invalid score: {exc}")
        return 2

    out_dir = Path(args.output_dir).resolve()
    if out_dir.exists() and any(out_dir.iterdir()):
        print(f"ERROR: output directory not empty: {out_dir}")
        return 2

    from moodify.score_engine.musescore_backend import MuseScoreBackend

    backend = MuseScoreBackend()
    if not backend.available():
        print("ERROR: MuseScore backend unavailable (set MUSESCORE_BIN or install MuseScore)")
        return 3
    result = backend.export(score, out_dir)
    print(f"Export: status={result.status} backend=musescore version={backend.version()}")
    for artifact in result.artifacts:
        print(f"  artifact: {artifact}")
    if result.errors:
        for error in result.errors:
            print(f"  ERROR: {error}")
    if result.status != "success":
        return 1

    # round-trip verification on the exported MusicXML (written by backend export)
    musicxml = next(out_dir.glob("*.musicxml"), None)
    if musicxml is None:
        print("WARNING: no MusicXML artifact for round-trip check")
        return 0
    report_target = out_dir / "roundtrip_report.json"
    report = build_roundtrip_report(score, musicxml, "", report_target)
    print(f"Round-trip: verdict={report['verdict']}")
    for w in report["stages"][2]["warnings"]:
        print(f"  warning: {w.get('field')}")
    if report["verdict"] == "FAIL":
        print("ERROR: round-trip FAIL — critical fields not preserved")
        return 1
    return 0


def cmd_score_backends(args) -> int:
    infos = list_backends()
    print("\nMoodify Score backends:")
    for info in infos:
        state = "available" if info.available else ("capability-bit only" if not info.implemented else "UNAVAILABLE")
        version = f" v{info.version}" if info.version else ""
        print(f"  {info.backend_id:12s} {state:20s} {info.license_label}{version}")
    if args.json:
        print(json.dumps([i.to_dict() for i in infos], ensure_ascii=False, indent=2))
    return 0
