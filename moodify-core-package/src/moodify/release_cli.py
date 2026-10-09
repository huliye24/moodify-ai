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
    analyze.add_argument("--format", choices=("json", "summary"), default="json",
                         help="summary prints a short human-readable digest")
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
    protocol = commands.add_parser(
        "protocol", help="validate or execute an MSP sound job (0.1 process / 0.2 analyze)")
    protocol.add_argument("action", choices=("validate", "process"))
    protocol.add_argument("job", help="JSON job file; relative paths resolve beside it")
    report_cmd = commands.add_parser(
        "report", help="re-render report.md/report.html from a persisted 0.2 report.json")
    report_cmd.add_argument("target", help="case_id (resolved under --cases-root) or path to report.json")
    report_cmd.add_argument("--cases-root", default="outputs/moodify_cases")
    commands.add_parser(
        "doctor", help="environment probe: python/core/dependencies/ffmpeg (stdout JSON)")
    demo = commands.add_parser(
        "demo",
        help="one-shot core moment: analyze audio, render the 0.2 report "
             "and open it in the Moodify report window")
    demo.add_argument("audio")
    demo.add_argument("--cases-root", default="outputs/moodify_cases")
    demo.add_argument("--browser", action="store_true",
                      help="open the HTML export in the system browser instead "
                           "of the Moodify window")
    demo.add_argument("--no-open", action="store_true",
                      help="render only; display nothing "
                           "(report paths stay in stdout JSON)")
    app_cmd = commands.add_parser(
        "app", help="open the Moodify desktop app: pick audio, analyze in place, "
                    "browse the permanent case archive")
    app_cmd.add_argument("cases_root", nargs="?", default=None,
                         help="archive root (default: ~/.moodify/cases)")
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
    compare = commands.add_parser(
        "compare",
        help="A/B listening comparison: prepare source-vs-render, record the human choice")
    compare_sub = compare.add_subparsers(dest="compare_action", required=True)
    compare_prepare = compare_sub.add_parser(
        "prepare",
        help="build/refresh the case's A/B comparison artifact (measured facts, no verdict)")
    compare_prepare.add_argument("case_dir", help="case directory (contains case.json)")
    compare_prepare.add_argument("--cases-root", default=None,
                                 help="require the case to live inside this root")
    compare_prepare.add_argument("--a", default=None,
                                 help="source audio (A) when the case has no recorded source path")
    compare_prepare.add_argument("--b", default=None,
                                 help="render (B) inside <case>/finishing; default = newest render")
    compare_prepare.add_argument("--json", action="store_true",
                                 help="machine output (stdout is one JSON object either way)")
    compare_choose = compare_sub.add_parser(
        "choose", help="append one human keep-A / keep-B decision to the case ledger")
    compare_choose.add_argument("case_dir")
    compare_choose.add_argument("--keep", required=True, choices=("A", "B"),
                                help="A = keep the source, B = keep the rendered artifact")
    compare_choose.add_argument("--role", required=True, choices=("creator", "listener", "pro"))
    compare_choose.add_argument("--notes", default=None)
    compare_choose.add_argument("--request-id", default=None,
                                help="idempotency key: re-sending the same request is refused, "
                                     "so an agent retry cannot record one decision twice")
    compare_choose.add_argument("--cases-root", default=None)
    compare_choose.add_argument("--json", action="store_true")
    compare_show = compare_sub.add_parser(
        "show", help="read the prepared comparison artifact and its freshness")
    compare_show.add_argument("case_dir")
    compare_show.add_argument("--cases-root", default=None)
    compare_show.add_argument("--json", action="store_true")
    tuning = commands.add_parser(
        "tuning",
        help="paired tier rendering for the Studio tuning stage "
             "(MIP-0002 Addendum A, EXPERIMENTAL)")
    tuning_sub = tuning.add_subparsers(dest="tuning_action", required=True)
    tuning_pair = tuning_sub.add_parser(
        "render-pair",
        help="render one complete A/B pair (conservative / full) into a pair directory")
    tuning_pair.add_argument("--mode", required=True, choices=("fast-stereo-only",),
                             help="FAST_STEREO_ONLY: whole-track pair, no stems and no MIDI")
    tuning_pair.add_argument("--source", required=True,
                             help="the case's own stereo master (never written to)")
    tuning_pair.add_argument("--output-dir", required=True,
                             help="final pair directory; must not exist yet")
    tuning_pair.add_argument("--pair-id", default=None,
                             help="pair id recorded in pair.json (default: the output directory name)")
    finishing_export.add_argument("--audio", required=True)
    finishing_export.add_argument("--output-dir", default="outputs")
    project_cmd = commands.add_parser(
        "project", help="Song Project tools (moodify.project/0.1)")
    project_sub = project_cmd.add_subparsers(dest="project_action", required=True)
    project_inspect = project_sub.add_parser(
        "inspect-legacy",
        help="read-only inspection of an existing case/project directory "
             "(Song Project / Core case / Studio case / legacy WSE); "
             "never writes")
    project_inspect.add_argument("target", help="case or project directory")
    project_inspect.add_argument(
        "--json", action="store_true",
        help="suppress the human digest on stderr; stdout is one JSON object either way")
    args = parser.parse_args(argv)
    if args.command == "analyze":
        result = analyze_to_case(Path(args.audio), Path(args.cases_root))
        if args.format == "summary":
            print(_summarize_analysis(result))
            return 0
    elif args.command == "report":
        from moodify.auditory.protocol_report import write_report_bundle

        target = Path(args.target)
        if target.suffix == ".json" and target.is_file():
            case_root = target.resolve().parent
        else:
            case_root = Path(args.cases_root).resolve() / args.target
        if not (case_root / "report.json").is_file():
            print(json.dumps({"status": "error",
                              "error": f"no report.json under {case_root}"},
                             ensure_ascii=False), file=sys.stderr)
            return 2
        write_report_bundle(case_root, rewrite_json=False)
        result = {
            "status": "rendered",
            "case_root": str(case_root),
            "reports": {"markdown": str(case_root / "report.md"),
                        "html": str(case_root / "report.html")},
        }
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
    elif args.command == "tuning":
        # MIP-0002 Addendum A: one call renders one complete pair, or nothing at all.
        from moodify.mix_graph.schema import MixGraphError
        from moodify.tuning import TuningError, render_pair

        try:
            result = render_pair(args.source, args.output_dir,
                                 pair_id=args.pair_id, mode=args.mode)
        except (TuningError, MixGraphError) as exc:
            print(json.dumps({"status": "error", "error": str(exc)}, ensure_ascii=False),
                  file=sys.stderr)
            return 2
    elif args.command == "compare":
        from moodify.ab_compare import (
            STATUS_EXIT,
            CompareError,
            NotReadyError,
            load_comparison,
            prepare_comparison,
            record_choice,
        )

        try:
            if args.compare_action == "prepare":
                result = prepare_comparison(
                    args.case_dir, cases_root=args.cases_root,
                    a_path=args.a, b_path=args.b)
                exit_code = STATUS_EXIT.get(result["status"], 2)
            elif args.compare_action == "choose":
                result = record_choice(
                    args.case_dir, keep=args.keep, role=args.role,
                    notes=args.notes, request_id=args.request_id,
                    cases_root=args.cases_root)
                exit_code = 0
            else:  # show
                result = load_comparison(args.case_dir, cases_root=args.cases_root)
                exit_code = STATUS_EXIT.get(result["status"], 2)
        except NotReadyError as exc:
            print(json.dumps(exc.payload(), ensure_ascii=False), file=sys.stderr)
            return exc.exit_code
        except CompareError as exc:
            print(json.dumps(exc.payload(), ensure_ascii=False), file=sys.stderr)
            return 2
        if not args.json:
            print(_summarize_compare(args.compare_action, result), file=sys.stderr)
        print(json.dumps(result, ensure_ascii=False, sort_keys=True))
        return exit_code
    elif args.command == "project":
        from moodify.project import ProjectError, inspect_case

        try:
            inspection = inspect_case(Path(args.target))
        except ProjectError as exc:
            print(json.dumps({"status": "error", "error": str(exc)},
                             ensure_ascii=False), file=sys.stderr)
            return 2
        if not args.json:
            print(_summarize_inspection(inspection.to_dict()), file=sys.stderr)
        print(json.dumps(inspection.to_dict(), ensure_ascii=False, sort_keys=True))
        # RECOGNIZED / INCOMPLETE are answers; CORRUPT / UNSUPPORTED are refusals.
        return 0 if inspection.status in ("RECOGNIZED", "INCOMPLETE") else 2
    elif args.command == "doctor":
        result = _doctor_report()
    elif args.command == "demo":
        from moodify.sound_protocol import (
            PROTOCOL_V02,
            ProtocolError,
            execute_job,
            validate_job,
        )

        try:
            job = validate_job(
                {"protocol": PROTOCOL_V02, "type": "analyze",
                 "source": args.audio, "output_dir": args.cases_root},
                Path.cwd(),
            )
            result = execute_job(job)
        except ProtocolError as exc:
            print(json.dumps({"status": "error", "error": str(exc)},
                             ensure_ascii=False), file=sys.stderr)
            return 2
        if not args.no_open:
            display = _display_report(Path(result["reports"]["json"]),
                                      Path(result["reports"]["html"]),
                                      prefer_browser=args.browser)
            if display is not None:
                result = {**result, "display": display}
    elif args.command == "app":
        from moodify.ui.app import DEFAULT_CASES_ROOT

        cases_root = (Path(args.cases_root).expanduser()
                      if args.cases_root else DEFAULT_CASES_ROOT)
        window = _spawn_ui_module("moodify.ui.app", str(cases_root))
        result = {"command": "app", "cases_root": str(cases_root),
                  "display": window}
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


_DOCTOR_PACKAGES = (
    "numpy", "scipy", "librosa", "soundfile", "pyloudnorm",
    "jsonschema", "pedalboard", "matplotlib",
)


def _display_report(report_json: Path, report_html: Path,
                    prefer_browser: bool = False) -> dict | None:
    """Surface the rendered report; returns machine-readable display data.

    The Moodify window (``moodify.ui``) is the product display surface and
    runs in a detached process so the CLI exits immediately — an agent
    calling this command must never wait on a human closing a window. The
    browser remains an export-viewing fallback.
    """
    if not prefer_browser:
        window = _spawn_report_window(report_json)
        if window is not None:
            return window
    try:
        import webbrowser

        webbrowser.open(report_html.resolve().as_uri())
        return {"mode": "browser"}
    except OSError:
        return None


def _spawn_ui_module(module: str, *args: str) -> dict | None:
    """Launch a ``moodify.ui`` module detached; the CLI must never wait on a
    human closing a window. Returns None when spawning is impossible."""
    import subprocess
    import sys

    kwargs: dict = {}
    if sys.platform == "win32":
        kwargs["creationflags"] = (getattr(subprocess, "DETACHED_PROCESS", 0)
                                   | getattr(subprocess, "CREATE_NEW_PROCESS_GROUP", 0))
    else:
        kwargs["start_new_session"] = True
    try:
        proc = subprocess.Popen(
            [sys.executable, "-m", module, *args],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, **kwargs)
    except OSError:
        return None
    return {"mode": "window", "pid": proc.pid}


def _spawn_report_window(report_json: Path) -> dict | None:
    return _spawn_ui_module("moodify.ui.report_window", str(report_json))


def _doctor_report() -> dict:
    """Layer D (D-ENG-2): first-contact environment probe.

    stdout-JSON discipline: the diagnostic itself always succeeds (exit 0);
    whether the environment is usable is carried by ``ready`` so agents can
    branch on data instead of parsing exit codes.
    """
    import importlib
    import importlib.metadata
    import platform

    from moodify.auditory.decode import FfmpegNotFound, _which_ffmpeg, ffmpeg_version
    from moodify.auditory.judgment import JUDGMENT_RULES_VERSION

    packages: dict[str, dict] = {}
    for name in _DOCTOR_PACKAGES:
        try:
            importlib.import_module(name)
        except Exception as exc:  # a broken dep must not crash the probe
            packages[name] = {"importable": False,
                              "error": f"{type(exc).__name__}: {exc}"}
            continue
        try:
            version: str | None = importlib.metadata.version(name)
        except Exception:
            version = None
        packages[name] = {"importable": True, "version": version}

    try:
        # resolve exactly like the runtime does (PATH + Windows winget links)
        ffmpeg_path = _which_ffmpeg()
        ffmpeg_report = {"found": True, "path": ffmpeg_path,
                         "version": ffmpeg_version()}
    except FfmpegNotFound:
        ffmpeg_report = {"found": False, "path": None, "version": None}

    deps_ok = all(entry["importable"] for entry in packages.values())
    ready = ffmpeg_report["found"] and deps_ok
    return {
        "status": "ok",
        "ready": ready,
        "python": platform.python_version(),
        "core_version": PRODUCT_VERSION,
        "judgment_rules_version": JUDGMENT_RULES_VERSION,
        "ffmpeg": ffmpeg_report,
        "packages": packages,
        **({} if ready else {"hint": "install ffmpeg and ensure it is on PATH; "
                                     "re-run `moodify doctor` to verify"}),
    }


def _summarize_compare(action: str, result: dict) -> str:
    """Short human digest (stderr only) for `moodify compare …`.

    stdout stays exactly one JSON object whether or not ``--json`` is given;
    this line is the human convenience the flag suppresses.
    """
    if action == "choose":
        return (f"已记录：保留 {result['keep']}（{result['kept']}）· 角色 {result['role']}"
                f" · 第 {result['count']} 条 · {result['choices_path']}")
    lines = [f"compare {action} — 状态 {result.get('status')}"]
    if action == "show":
        artifact = result.get("artifact") or {}
        freshness = result.get("freshness") or {}
        lines.append(f"case: {artifact.get('case_id', '?')}")
        lines.append(f"账本条数: {freshness.get('choice_count', 0)}"
                     f" · A 未变: {freshness.get('a_matches_artifact')}"
                     f" · B 未变: {freshness.get('b_matches_artifact')}")
        for reason in artifact.get("reasons", []):
            lines.append(f"  [{reason.get('code')}] {reason.get('message')}")
        return "\n".join(lines)
    a_block = result.get("a") or {}
    b_block = result.get("b") or {}
    loudness = result.get("loudness") or {}
    lines.append(f"A: {a_block.get('name', '（未定位）')}")
    lines.append(f"B: {b_block.get('name', '（未渲染）')}")
    lines.append(f"响度: A={loudness.get('a_integrated_lufs')} LUFS"
                 f" B={loudness.get('b_integrated_lufs')} LUFS"
                 f" Δ={loudness.get('delta_lu')} LU"
                 f" → {loudness.get('matching_status')}（无匹配代理）")
    for reason in result.get("reasons", []):
        lines.append(f"  [{reason.get('code')}] {reason.get('message')}")
    if result.get("status") == "READY":
        lines.append("下一步: moodify compare choose <case-dir> --keep A|B --role creator|listener|pro")
    return "\n".join(lines)


def _summarize_inspection(result: dict) -> str:
    """Short human digest (stderr only) for `moodify project inspect-legacy`.

    stdout stays exactly one JSON object whether or not ``--json`` is given;
    this is the human convenience the flag suppresses — same discipline as
    `moodify compare`.
    """
    lines = [f"project inspect-legacy — {result['status']}（{result['layout']}）"]
    if result.get("case_id"):
        lines.append(f"case: {result['case_id']}"
                     + (f" · {result['name']}" if result.get("name") else ""))
    source = result.get("source")
    if source:
        recorded = source.get("recorded_sha256")
        lines.append(
            f"source: {source.get('origin')} · "
            f"记录哈希 {(recorded or '无')[:19]} · 验证 {source.get('verified')}")
    filled = {k: len(v) for k, v in result["sections"].items() if v}
    if filled:
        lines.append("sections: " + "  ".join(f"{k}={n}" for k, n in filled.items()))
    for problem in result["problems"]:
        lines.append(f"  [{problem['severity']}] {problem['code']} — {problem['message']}")
    for unknown in result["unknowns"]:
        lines.append(f"  [unknown] {unknown}")
    if result["ignored_file_count"]:
        lines.append(f"额外未归类文件: {result['ignored_file_count']} 个（不影响识别）")
    return "\n".join(lines)


def _summarize_analysis(result: dict) -> str:
    """Short human-readable digest for `moodify analyze --format summary`."""
    case = result.get("case", {})
    report = result.get("report", {})
    sections = report.get("sections", {})
    lines = [
        f"Moodify 听觉分析 — {report.get('source_name', '?')}",
        f"case: {case.get('case_id', '?')}  状态: {report.get('overall_status', '?')}",
    ]
    if sections:
        lines.append("分区: " + "  ".join(f"{name}={status}" for name, status in sections.items()))
    findings = report.get("findings", [])
    if findings:
        lines.append("发现:")
        for finding in findings:
            lines.append(f"  [{finding.get('severity', '?')}] {finding.get('code', '?')} — "
                         f"{finding.get('message', '')}")
    else:
        lines.append("发现: 无（未触发阈值）")
    lines.append(f"说明: {report.get('summary', '')}")
    lines.append("边界: 本结果只覆盖 L1 技术测量；不含听感、音乐或商业判断。")
    return "\n".join(lines)


if __name__ == "__main__":
    raise SystemExit(main())
