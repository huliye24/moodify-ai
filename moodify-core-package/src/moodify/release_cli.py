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
    local = commands.add_parser("local-analyze", help="run the cached CPU-first Phase-I hearing graph")
    local.add_argument("audio")
    local.add_argument("--cache-root", default=".moodify/cache")
    local.add_argument("--manifest", default=".moodify/runs/latest.json")
    cache = commands.add_parser("cache", help="inspect or clear the local derived-data cache")
    cache.add_argument("action", choices=("size", "clear-all", "clear-source"))
    cache.add_argument("--cache-root", default=".moodify/cache")
    cache.add_argument("--source-sha256")
    args = parser.parse_args(argv)
    if args.command == "analyze":
        result = analyze_to_case(Path(args.audio), Path(args.cases_root))
    elif args.command == "show":
        result = reopen_case(Path(args.cases_root), args.case_id)
    elif args.command == "local-analyze":
        from moodify.auditory.execution.pipeline import run_local_analysis

        outputs, diagnostics = run_local_analysis(
            Path(args.audio), Path(args.cache_root), Path(args.manifest),
        )
        result = {"report": outputs["report"], "execution": diagnostics.to_dict()}
    else:
        from moodify.auditory.execution.cache import LocalCache

        local_cache = LocalCache(Path(args.cache_root))
        if args.action == "size":
            result = {"cache_root": str(Path(args.cache_root)), "size_bytes": local_cache.size_bytes()}
        elif args.action == "clear-all":
            local_cache.clear_all()
            result = {"cleared": "all"}
        else:
            if not args.source_sha256:
                parser.error("cache clear-source requires --source-sha256")
            local_cache.clear_source(args.source_sha256)
            result = {"cleared_source": args.source_sha256}
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
