"""JSON-first CLI for the Moodify 1.0 auditory release path."""

from __future__ import annotations

import argparse
import json
import sys
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
    protocol = commands.add_parser("protocol", help="validate or execute an MSP/0.1 sound job")
    protocol.add_argument("action", choices=("validate", "process"))
    protocol.add_argument("job", help="JSON job file; relative paths resolve beside it")
    finishing = commands.add_parser(
        "finishing", help="mix graph finishing sessions (moodify.mix_graph/0.1, EXPERIMENTAL)")
    finishing_sub = finishing.add_subparsers(dest="finishing_action", required=True)
    finishing_new = finishing_sub.add_parser("new", help="derive a starter mix graph from a preset")
    finishing_new.add_argument("--preset", default="clean_master",
                               choices=("warm_vocal", "clean_master", "wide_space"))
    finishing_new.add_argument("--source", required=True, help="audio file the graph targets")
    finishing_new.add_argument("--out", help="write graph JSON here (default: print)")
    finishing_render = finishing_sub.add_parser("render", help="render, verify and export a session")
    finishing_render.add_argument("graph", help="mix graph JSON file")
    finishing_render.add_argument("--output-dir", default="outputs")
    finishing_render.add_argument("--dry-run", action="store_true",
                                  help="render and verify but write no files")
    finishing_verify = finishing_sub.add_parser(
        "verify", help="measure before/after evidence for two audio files")
    finishing_verify.add_argument("--source", required=True)
    finishing_verify.add_argument("--output", required=True)
    finishing_verify.add_argument("--max-peak-dbfs", type=float, default=None,
                                  help="optional peak gate applied to the output measurement")
    finishing_export = finishing_sub.add_parser(
        "export", help="delivery encode: 16-bit PCM with a -1 dBFS ceiling")
    finishing_export.add_argument("--audio", required=True)
    finishing_export.add_argument("--output-dir", default="outputs")
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
    elif args.command == "protocol":
        from moodify.sound_protocol import ProtocolError, execute_job, load_job

        try:
            job = load_job(Path(args.job))
            result = {"status": "valid", **job} if args.action == "validate" else execute_job(job)
        except ProtocolError as exc:
            print(json.dumps({"status": "error", "error": str(exc)}, ensure_ascii=False), file=sys.stderr)
            return 2
    elif args.command == "finishing":
        from moodify.audio_io import load_audio
        from moodify.mix_graph import (
            MixGraphError,
            export_delivery,
            graph_from_preset,
            load_graph,
            run_session,
            save_graph,
            verify_before_after,
        )
        from moodify.mix_graph.verify import peak_gate

        try:
            if args.finishing_action == "new":
                if args.out:
                    # Paths inside a graph file resolve relative to the file
                    # itself (same convention as MSP jobs), so store the source
                    # relative to the graph's directory when possible.
                    out_path = Path(args.out).resolve()
                    source_path = Path(args.source).resolve()
                    try:
                        source_repr = source_path.relative_to(out_path.parent).as_posix()
                    except ValueError:
                        source_repr = str(source_path)
                    graph = graph_from_preset(args.preset, source_repr)
                    written = save_graph(graph, out_path)
                    result = {"status": "created", "graph": str(written),
                              "graph_digest_sha256": graph.digest()}
                else:
                    graph = graph_from_preset(args.preset, args.source)
                    result = {"status": "created", "graph_digest_sha256": graph.digest(),
                              "graph": graph.to_dict()}
            elif args.finishing_action == "render":
                result = run_session(load_graph(Path(args.graph)),
                                     Path(args.output_dir), args.dry_run)
            elif args.finishing_action == "verify":
                source_audio, sr = load_audio(args.source, always_2d=True)
                output_audio, sr_out = load_audio(args.output, always_2d=True)
                if sr != sr_out:
                    raise MixGraphError(f"sample rate mismatch: {sr} vs {sr_out}")
                result = verify_before_after(source_audio, output_audio, sr)
                result["source"] = str(Path(args.source).resolve())
                result["output_path"] = str(Path(args.output).resolve())
                if args.max_peak_dbfs is not None:
                    result["peak_gate"] = peak_gate(result["after"], args.max_peak_dbfs)
            else:  # export
                result = export_delivery(args.audio, args.output_dir)
        except MixGraphError as exc:
            print(json.dumps({"status": "error", "error": str(exc)}, ensure_ascii=False),
                  file=sys.stderr)
            return 2
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
