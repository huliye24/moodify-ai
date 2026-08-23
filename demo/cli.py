"""Moodify CLI — `moodify analyze <audio file>`.

Usage:
    moodify analyze song.mp3
    moodify analyze song.mp3 --output demo/output
    python -m demo.cli analyze song.mp3     (no install needed)

Outputs:
    - terminal summary
    - report.json  (unified Intelligence Report schema)
    - report.md    (human-readable full report)
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

# Allow running both as `python -m demo.cli` and `python demo/cli.py`.
_REPO_ROOT = Path(__file__).resolve().parents[1]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="moodify",
        description="Moodify Intelligence Platform CLI",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    analyze = sub.add_parser(
        "analyze",
        help="Analyze one audio file and generate a Moodify Intelligence Report",
    )
    analyze.add_argument("input", help="path to audio file (wav / mp3 / flac)")
    analyze.add_argument(
        "-o", "--output",
        default=None,
        help="output directory (default: <repo>/demo/output/<file stem>)",
    )

    args = parser.parse_args(argv)

    if args.command == "analyze":
        return _run_analyze(args.input, args.output)
    parser.error(f"unknown command: {args.command}")
    return 2


def _run_analyze(input_path: str, output_dir: str | None) -> int:
    path = Path(input_path)
    if not path.is_file():
        print(f"error: file not found: {path}", file=sys.stderr)
        return 1

    # Imported lazily so `moodify --help` works without the audio stack.
    from demo.analyzer.pipeline import run_analysis
    from demo.report.generator import render_terminal, write_json, write_markdown

    print(f"Moodify Intelligence Engine — analyzing {path.name} ...")
    report = run_analysis(path)

    if output_dir is None:
        out = _REPO_ROOT / "demo" / "output" / path.stem
    else:
        out = Path(output_dir)

    json_path = write_json(report, out)
    md_path = write_markdown(report, out)

    print()
    print(render_terminal(report))
    print(f"  report.json : {json_path}")
    print(f"  report.md   : {md_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
