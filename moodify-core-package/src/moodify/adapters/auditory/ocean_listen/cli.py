from __future__ import annotations

from pathlib import Path
import argparse
import json
import sys
import uuid

from .config import OceanRunOptions, PINNED_OCEAN_COMMIT
from .mapper import map_report_file
from .provenance import capture_module_manifest, git_head
from .quality_gate import evaluate_report
from .runner import OceanRunner
from .vendor import vendor_snapshot


def _json_print(value: object) -> None:
    print(json.dumps(value, indent=2, ensure_ascii=False))


def _run_command(args: argparse.Namespace) -> int:
    options = OceanRunOptions(
        ocean_root=Path(args.ocean_root),
        output_root=Path(args.output_root),
        cache_root=Path(args.cache_root) if args.cache_root else None,
        python_executable=args.python,
        deep=args.deep,
        mode=args.mode,
        lyric=args.lyric,
        lyric_value=args.lyric_value,
        language=args.language,
        whisper_model=args.whisper_model,
        force=args.force,
        timeout_seconds=args.timeout,
        expected_commit=None if args.allow_unreviewed_commit else args.expected_commit,
    )
    result = OceanRunner(options).run(args.audio)
    _json_print(
        {
            "run_id": result["execution"]["run_id"],
            "run_dir": result["execution"]["run_dir"],
            "gate": result["quality_gate"]["verdict"],
            "manifest": result["manifest_path"],
        }
    )
    return 0


def _map_command(args: argparse.Namespace) -> int:
    root = Path(args.ocean_root) if args.ocean_root else None
    commit = git_head(root) if root else args.upstream_commit
    manifest = capture_module_manifest(root) if root else {}
    mapped = map_report_file(
        args.report,
        source_audio=args.source_audio,
        run_id=args.run_id or str(uuid.uuid4()),
        upstream_commit=commit,
        module_manifest=manifest,
        output_path=args.output,
        deep_expected=args.deep_expected,
    )
    _json_print(
        {
            "observation_id": mapped["observation_id"],
            "gate": mapped["quality_gate"]["verdict"],
            "output": str(Path(args.output).resolve()) if args.output else None,
        }
    )
    return 0


def _gate_command(args: argparse.Namespace) -> int:
    report = json.loads(Path(args.report).read_text(encoding="utf-8"))
    gate = evaluate_report(report, deep_expected=args.deep_expected)
    _json_print(gate.to_dict())
    return 2 if gate.verdict == "FAIL" else 0


def _vendor_command(args: argparse.Namespace) -> int:
    manifest = vendor_snapshot(args.ocean_root, args.destination)
    _json_print(
        {
            "destination": str(Path(args.destination).resolve()),
            "source_commit": manifest.get("source_commit"),
            "files": len(manifest.get("copied_paths", [])),
        }
    )
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="moodify-ocean",
        description="Isolated Ocean Listen sensor adapter for Moodify",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    run = sub.add_parser("run", help="execute Ocean and produce a Moodify evidence bundle")
    run.add_argument("audio")
    run.add_argument("--ocean-root", required=True)
    run.add_argument("--output-root", default="artifacts/ocean_bridge")
    run.add_argument("--cache-root")
    run.add_argument("--python", default=sys.executable)
    run.add_argument("--deep", action="store_true")
    run.add_argument(
        "--mode",
        choices=["auto", "music", "solo", "voice", "mixed"],
        default="auto",
    )
    run.add_argument(
        "--lyric",
        choices=["auto", "whisper", "sensevoice", "netease"],
    )
    run.add_argument("--lyric-value")
    run.add_argument("--language", default="auto")
    run.add_argument("--whisper-model", default="small")
    run.add_argument("--force", action="store_true")
    run.add_argument("--timeout", type=int, default=1800)
    run.add_argument("--expected-commit", default=PINNED_OCEAN_COMMIT)
    run.add_argument(
        "--allow-unreviewed-commit",
        action="store_true",
        help="disable commit pin enforcement; use only after a reviewed upstream diff",
    )
    run.set_defaults(func=_run_command)

    map_cmd = sub.add_parser("map", help="map an existing Ocean JSON report")
    map_cmd.add_argument("report")
    map_cmd.add_argument("--source-audio", required=True)
    map_cmd.add_argument("--output", required=True)
    map_cmd.add_argument("--run-id")
    map_cmd.add_argument("--ocean-root")
    map_cmd.add_argument("--upstream-commit")
    map_cmd.add_argument("--deep-expected", action="store_true")
    map_cmd.set_defaults(func=_map_command)

    gate = sub.add_parser("gate", help="quality-check an Ocean JSON report")
    gate.add_argument("report")
    gate.add_argument("--deep-expected", action="store_true")
    gate.set_defaults(func=_gate_command)

    vendor = sub.add_parser("vendor", help="create an immutable licensed source snapshot")
    vendor.add_argument("--ocean-root", required=True)
    vendor.add_argument("--destination", required=True)
    vendor.set_defaults(func=_vendor_command)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main())
