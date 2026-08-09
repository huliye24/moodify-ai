"""JSON-first CLI for the Moodify 1.0 auditory release path."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from moodify.release import PRODUCT_VERSION, analyze_to_case, reopen_case


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="moodify", description="Moodify — The Ear of AI")
    parser.add_argument("--version", action="version", version=PRODUCT_VERSION)
    commands = parser.add_subparsers(dest="command", required=True)
    analyze = commands.add_parser("analyze")
    analyze.add_argument("audio")
    analyze.add_argument("--cases-root", default="outputs/moodify_cases")
    show = commands.add_parser("show")
    show.add_argument("case_id")
    show.add_argument("--cases-root", default="outputs/moodify_cases")
    args = parser.parse_args(argv)
    if args.command == "analyze":
        result = analyze_to_case(Path(args.audio), Path(args.cases_root))
    else:
        result = reopen_case(Path(args.cases_root), args.case_id)
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
