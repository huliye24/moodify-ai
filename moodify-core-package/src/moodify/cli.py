"""Legacy Auditory Intervention Laboratory CLI.

The canonical ``moodify`` command is ``moodify.cli_v2.main``. This module is
retained only for reproducibility of historical intervention cases.

Moodify CLI — AI music post-processing, one command.

Usage:
  moodify analyze <audio>              Spectrum analysis -> PNG + metrics
  moodify process <audio> --preset X   Process with v0.1.0 preset -> WAV
  moodify presets                      List v0.1.0 presets
  moodify serve                        Start API server
  moodify legacy-analyze <audio>       (Legacy) Old diagnosis engine
  moodify legacy-process <audio> <emotion> (Legacy) Old workflow engine
"""

import sys
import argparse
import time
from pathlib import Path

SUPPORTED_EXTENSIONS = {'.wav', '.mp3', '.flac', '.aiff', '.aif', '.m4a', '.ogg'}


def cmd_audacity(args):
    """Audacity macro runtime commands (DSK-MFY-AUDACITY-MACRO-RUNTIME-001)."""
    from moodify.adapters.audacity.runtime import (
        EXECUTION_COMPLETED,
        AudacityMacroRuntime,
    )

    with AudacityMacroRuntime() as runtime:
        if getattr(args, "audacity_command", None) == "macros":
            regs = runtime.list_available_macros()
            if getattr(args, "json", False):
                import json
                print(json.dumps(
                    [{"display_name": r.display_name, "scripting_id": r.scripting_id}
                     for r in regs],
                    ensure_ascii=False, indent=2,
                ))
            else:
                if not regs:
                    print("无已注册宏（检查 %APPDATA%\\audacity\\Macros）")
                for r in regs:
                    print(f"{r.display_name:<40} {r.scripting_id}")
            return 0

        if getattr(args, "audacity_command", None) == "macro":
            from pathlib import Path
            record = runtime.run_macro(
                input_path=Path(args.input),
                macro_name=args.macro,
                output_path=Path(args.output),
                case_id=args.case_id,
            )
            bundle = runtime.write_evidence(
                record, Path(args.evidence_dir)
            )
            print(EXECUTION_COMPLETED)
            print(f"case_id:     {record.case_id}")
            print(f"macro:       {record.macro_display_name} ({record.macro_scripting_id})")
            print(f"output:      {record.output_path}")
            print(f"output_sha:  {record.output_sha256}")
            print(f"evidence:    {bundle}")
            return 0

    print("ERROR: audacity 子命令：macros list | macro run")
    return 2


def cmd_legacy_analyze(args):
    """[legacy] 旧系统诊断分析"""
    from moodify.diagnosis.engine import DiagnosisEngine
    from moodify.diagnosis.defect_classifier import DefectClassifier
    from moodify.diagnosis.health_scorer import HealthScorer

    path = args.audio_path
    if not Path(path).exists():
        print(f"ERROR: File not found: {path}")
        return 1

    print(f"Analyzing: {path}")
    engine = DiagnosisEngine()
    t0 = time.time()
    ws = engine.diagnose_quick(path)
    elapsed = time.time() - t0

    classifier = DefectClassifier()
    defects = classifier.classify(ws)
    scorer = HealthScorer()
    whs = scorer.compute_whs(ws, defects)

    print(f"\n=== Diagnosis Report ({elapsed*1000:.0f}ms) ===")
    s, d, sp, layers, e = ws.Spectrum, ws.Dynamics, ws.Space, ws.Layers, ws.Emotion
    print("\n[Spectrum]")
    print(f"  S1_SubPresence:  {s.S1_SubPresence.value:+.1f} dB")
    print(f"  S2_BassWarmth:   {s.S2_BassWarmth.value:+.1f} dB")
    print(f"  S3_MidClarity:   {s.S3_MidClarity.value:.3f}")
    print(f"  S4_AirBand:      {s.S4_AirBand.value:+.1f} dB")
    print(f"  S5_SpectralTilt: {s.S5_SpectralTilt.value:+.1f} dB/oct")

    print("\n[Dynamics]")
    print(f"  D1_LRA:          {d.D1_LRA.value:.1f} LU")
    print(f"  D2_ChorusImpact: {d.D2_ChorusImpact.value:.1f} LU")
    print(f"  D3_MicroDynamics:{d.D3_MicroDynamics.value:.2f} LU")
    print(f"  D4_PLR:          {d.D4_PLR.value:.1f} dB")

    print("\n[Space]")
    print(f"  SP1_Correlation: {sp.SP1_Correlation.value:.3f}")
    print(f"  SP2_ForeBackSep: {sp.SP2_ForeBackSep.value:.1f} dB")
    print(f"  SP3_RT60Consist: {sp.SP3_RT60Consist.value:.3f} s")
    print(f"  SP4_WidthHealth: {sp.SP4_WidthHealth}")

    print("\n[Layers]")
    print(f"  L1_VocalSNR:     {layers.L1_VocalSNR.value:.1f} dB")
    print(f"  L2_BassClarity:  {layers.L2_BassClarity.value:.3f}")
    print(f"  L3_DrumDetect:   {layers.L3_DrumDetect.value:.3f}")

    print("\n[Health]")
    print(f"  WHS: {whs['WHS']:.1f} [{whs['level']}]")
    print(f"  Dim scores: {whs['dim_scores']}")

    if defects:
        print(f"\n[Defects] ({len(defects)} found)")
        for d in defects[:5]:
            print(f"  P{d.priority} S{d.severity} {d.defect_id}: {d.description_zh}")

    # JSON output mode
    if getattr(args, 'json', False):
        import json
        report = {
            "file": path,
            "elapsed_ms": round(elapsed * 1000),
            "spectrum": s.to_dict(),
            "dynamics": d.to_dict(),
            "space": sp.to_dict(),
            "layers": layers.to_dict(),
            "emotion": e.to_dict(),
            "whs": whs,
            "defects": [{"id": d.defect_id, "severity": d.severity,
                         "description": d.description_zh} for d in defects],
        }
        print("\n--- JSON ---")
        print(json.dumps(report, ensure_ascii=False, indent=2, default=str))

    return 0


def cmd_legacy_process(args):
    """[legacy] Process one audio file — WAV, MP3, FLAC all supported."""
    from moodify.orchestration.workflow_engine import WorkflowOrchestrator

    path = args.audio_path
    if not Path(path).exists():
        print(f"ERROR: File not found: {path}")
        return 1

    emotion = args.emotion
    output_dir = getattr(args, 'output_dir', 'outputs')
    platform = getattr(args, 'platform', 'spotify')

    print(f"Moodify: {Path(path).name}")
    print(f"  emotion: {emotion}  |  platform: {platform}")

    orch = WorkflowOrchestrator()
    t0 = time.perf_counter()
    result = orch.process(path, emotion, platform=platform, output_dir=output_dir)
    elapsed = time.perf_counter() - t0

    if not result.success:
        print(f"  FAILED after {elapsed:.0f}s")
        return 1

    eds_sign = '+' if result.eds > 0 else ''
    whs_delta = result.whs_after - result.whs_before
    whs_sign = '+' if whs_delta > 0 else ''

    print(f"  WHS: {result.whs_before:.0f} -> {result.whs_after:.0f} ({whs_sign}{whs_delta:.0f})")
    print(f"  EDS: {eds_sign}{result.eds:.0f}  |  risk: {result.risk_level}  |  {elapsed:.0f}s")
    print(f"  output: {result.output_path}")

    if getattr(args, 'json', False):
        import json as _json
        print(_json.dumps({
            "input": path, "emotion": emotion, "output": result.output_path,
            "whs_before": result.whs_before, "whs_after": result.whs_after,
            "eds": result.eds, "risk": result.risk_level, "elapsed_s": round(elapsed, 1),
        }, ensure_ascii=False))

    return 0 if result.success else 1


def cmd_batch(args):
    """Batch process all audio files in a directory."""
    from moodify.orchestration.workflow_engine import WorkflowOrchestrator
    from moodify.calibration.online import CalibrationState

    directory = args.directory
    emotion = args.emotion
    if not Path(directory).is_dir():
        print(f"ERROR: Directory not found: {directory}")
        return 1

    output_dir = getattr(args, 'output_dir', 'outputs')
    files = sorted(
        f for f in Path(directory).iterdir()
        if f.suffix.lower() in SUPPORTED_EXTENSIONS
    )

    if not files:
        print(f"No audio files found in: {directory}")
        return 1

    print(f"Moodify batch: {len(files)} files  |  emotion: {emotion}")
    print(f"  output: {output_dir}/\n")

    orch = WorkflowOrchestrator()
    ok, fail, eds_sum = 0, 0, 0.0
    t_start = time.perf_counter()

    for i, fp in enumerate(files, 1):
        try:
            result = orch.process(str(fp), emotion, output_dir=output_dir)
            if result.success:
                ok += 1
                eds_sum += result.eds
                eds_s = f'{result.eds:+.0f}'
                print(f"  [{i}/{len(files)}] {fp.name[:40]:40s} EDS={eds_s:>5s}  WHS {result.whs_before:.0f}->{result.whs_after:.0f}  ({result.total_elapsed_ms:.0f}ms)")
            else:
                fail += 1
                print(f"  [{i}/{len(files)}] {fp.name[:40]:40s} FAILED")
        except Exception as e:
            fail += 1
            print(f"  [{i}/{len(files)}] {fp.name[:40]:40s} ERROR: {e}")

    elapsed = time.perf_counter() - t_start
    avg_eds = eds_sum / max(ok, 1)
    print(f"\n  {ok} ok, {fail} failed  |  avg EDS: {avg_eds:+.0f}  |  {elapsed:.0f}s")

    # Show calibration D if available
    try:
        state = CalibrationState.load(output_dir)
        print(f"  calibration D: {state.d_value():.3f}  (n={state.total_n})")
    except Exception:
        pass

    return 0 if fail == 0 else 1


def cmd_emotions(args):
    """列出可用情绪"""
    from moodify.knowledge.emotion_targets import EMOTION_TARGETS_V2
    from moodify.knowledge.craft_chains import CRAFT_CHAINS_15PARAMS

    print(f"\nAvailable emotions ({len(EMOTION_TARGETS_V2)}):\n")
    print(f"  {'Code':4s} {'Chinese':8s} {'English':25s} {'Primary':15s} {'Reverb'}")
    print(f"  {'-'*4} {'-'*8} {'-'*25} {'-'*15} {'-'*20}")
    for key, t in EMOTION_TARGETS_V2.items():
        code = t['code']
        chain_info = ""
        if code in CRAFT_CHAINS_15PARAMS:
            chain_info = "[craft chain ready]"
        print(f"  {code:4s} {t['name_cn']:8s} {t['name_en']:25s} "
              f"{t['primary']:15s} {t['reverb_style']:20s} {chain_info}")
    return 0


def cmd_crafts(args):
    """列出工艺卡"""
    from moodify.knowledge.craft_chain_match import generate_craft_cards_from_data

    cards = generate_craft_cards_from_data()
    print(f"\nCraft cards ({len(cards)}):\n")
    for c in cards:
        params = c.get_recommended_params()
        risk_count = len(c.risk_warnings)
        print(f"  {c.craft_card_id}  {c.name_zh:10s}  {c.name_en:25s}  "
              f"params={len(params)}  risks={risk_count}")

    if getattr(args, 'verbose', False):
        print("\n--- Detail ---")
        for c in cards:
            print(f"\n  [{c.craft_card_id}] {c.name_zh}")
            for k, v in c.get_recommended_params().items():
                print(f"    {k}: {v}")
            if c.risk_warnings:
                print("    Warnings:")
                for w in c.risk_warnings[:3]:
                    print(f"      - {w}")
    return 0


def cmd_serve(args):
    """启动 FastAPI 服务"""
    import uvicorn

    host = getattr(args, 'host', '0.0.0.0')
    port = getattr(args, 'port', 8000)

    print(f"Starting Moodify API server on http://{host}:{port}")
    print(f"Docs: http://{host}:{port}/docs")
    uvicorn.run(
        "moodify.api.main:app",
        host=host,
        port=port,
        reload=False,
        log_level="info",
    )
    return 0


def cmd_evaluate_run(args):
    """批量 AI 评测 — 驱动数据飞轮"""
    from moodify.evaluation.batch import cmd_evaluate_run as _run
    return _run(args)


def cmd_evaluate_status(args):
    """查看当前 D 值和校准状态"""
    from moodify.evaluation.batch import cmd_evaluate_status as _status
    return _status(args)


def cmd_evaluate_single(args):
    """对单个文件运行 AI 评测"""
    from moodify.evaluation.batch import cmd_evaluate_single as _single
    return _single(args)


# ═══════════════════════════════════════════════════════════
#  v0.1.0 handlers (new mainline)
# ═══════════════════════════════════════════════════════════

def cmd_v01_analyze(args):
    """v0.1.0: Analyze audio → spectrum PNG + metrics."""
    from moodify.v01_analyzer import analyze
    import json

    path = args.audio_path
    if not Path(path).exists():
        print(f"ERROR: File not found: {path}")
        return 1

    print(f"Moodify v0.1.0 — analyze: {path}")
    metrics = analyze(path, args.output_dir)

    stem = Path(path).stem
    print(f"  Duration:  {metrics.duration_s:.1f}s  |  {metrics.sample_rate}Hz  |  "
          f"{metrics.channels}ch")
    print(f"  Peak:      {metrics.peak_db:+.1f} dB")
    print(f"  Crest:     {metrics.crest_factor:.2f}")
    print(f"  Dyn Range: {metrics.dynamic_range_db:.1f} dB")
    print(f"  Corr L/R:  {metrics.correlation_lr:.3f}")
    print(f"  Spectrum:  sub={metrics.rms_sub:+.1f}  bass={metrics.rms_bass:+.1f}  "
          f"low-mid={metrics.rms_low_mid:+.1f}  mid={metrics.rms_mid:+.1f}  "
          f"presence={metrics.rms_presence:+.1f}  air={metrics.rms_air:+.1f}")
    print(f"  Output:    {args.output_dir}/{stem}_spectrum.png")

    if args.json:
        print(json.dumps(metrics.to_dict(), ensure_ascii=False, indent=2))
    return 0


def cmd_v01_process(args):
    """v0.1.0: Full pipeline — scan → analyze → process → report → deliver."""
    from moodify.v01_pipeline import process_audio, list_presets

    path = args.audio_path
    preset = args.preset
    if not Path(path).exists():
        print(f"ERROR: File not found: {path}")
        return 1
    valid_presets = ["auto", *list_presets()]
    if preset not in valid_presets:
        print(f"ERROR: Unknown preset '{preset}'. Valid: {', '.join(valid_presets)}")
        return 1

    print(f"Moodify v0.1.0 — process: {Path(path).name}")
    print(f"  preset: {preset}  |  output: {args.output_dir}/")

    result = process_audio(path, preset, args.output_dir)

    if not result.success:
        print(f"  FAILED: {result.error}")
        return 1

    rep = result.diagnosis
    if result.requested_preset == "auto":
        print(f"  Selected: {result.preset}")
    print(f"  Health:   {rep.overall_health}  ({len(rep.strengths)} strengths, "
          f"{len(rep.issues)} issues)")
    if rep.issues:
        for issue in rep.issues:
            print(f"    ! {issue}")
    if rep.suggested_presets:
        print(f"  Suggested: {', '.join(rep.suggested_presets)}")
    if result.quality_gate.warnings:
        print("  Quality:  review")
        for warning in result.quality_gate.warnings:
            print(f"    ! {warning}")
    else:
        print("  Quality:  pass")
    print(f"  Output:    {result.output_path}")
    print(f"  Report:    {result.report_path}")

    if args.json:
        import json
        print(json.dumps({
            "input": path, "requested_preset": preset, "preset": result.preset,
            "output": result.output_path,
            "report": result.report_path,
            "health": rep.overall_health,
            "quality_gate": result.quality_gate.to_dict(),
            "issues": rep.issues, "strengths": rep.strengths,
            "metrics": rep.metrics.to_dict(),
            "metrics_after": result.metrics_after.to_dict(),
            "delivery": result.delivery.to_dict(),
        }, ensure_ascii=False, indent=2))
    return 0


def cmd_v01_presets(args):
    """v0.1.0: List available presets."""
    from moodify.v01_presets import PRESETS

    print(f"\nMoodify v0.1.0 presets ({len(PRESETS)}):\n")
    for key, info in PRESETS.items():
        print(f"  {key:15s}  {info['name_zh']:8s}  {info['description']}")
    return 0


def cmd_transcribe_stems(args):
    """[v0.2] Transcribe isolated stems with per-stem profiles."""
    import json
    from pathlib import Path as P

    from moodify.transcription_pipeline.stems import StemManifest
    from moodify.transcription_pipeline.runner import transcribe_stems

    out_dir = P(args.output_dir).resolve()
    if out_dir.exists() and list(out_dir.iterdir()):
        print(f"ERROR: Output directory is not empty: {out_dir}")
        return 2

    pairs = []
    for stem_arg in args.stems:
        if "=" not in stem_arg:
            print(f"ERROR: Stem must be kind=path format: {stem_arg}")
            return 2
        kind_str, path_str = stem_arg.split("=", 1)
        pairs.append((kind_str.strip(), path_str.strip()))

    if not pairs:
        print("ERROR: At least one --stem is required.")
        return 2

    try:
        manifest = StemManifest.from_cli_pairs(pairs)
        manifest.validate()
    except (ValueError, FileNotFoundError) as exc:
        print(f"ERROR: {exc}")
        return 2

    overrides = {}
    if args.onset_threshold is not None:
        overrides["onset_threshold"] = args.onset_threshold
    if args.frame_threshold is not None:
        overrides["frame_threshold"] = args.frame_threshold
    if args.minimum_note_length is not None:
        overrides["minimum_note_length_ms"] = args.minimum_note_length
    if args.tempo is not None:
        overrides["midi_tempo"] = args.tempo

    try:
        result = transcribe_stems(manifest, out_dir, config_overrides=overrides or None)
    except (FileExistsError, ValueError, OSError) as exc:
        print(f"ERROR: {exc}")
        return 2

    if args.json:
        print(json.dumps(result.to_dict(), ensure_ascii=False, indent=2))
    else:
        print(f"\nMoodify stem transcription v0.2 — status: {result.status}")
        print(f"  output: {out_dir}")
        print(f"  elapsed: {result.total_elapsed_seconds:.2f}s")
        for s in result.stems:
            flag = "[OK]" if s.status == "success" else f"[{s.status.upper()}]"
            print(f"  {flag} {s.stem_kind}: {s.note_count} notes"
                  f"{' | ' + s.error if s.error else ''}")

    return 0 if result.status == "success" else (0 if result.status == "partial_success" else 1)


def cmd_transcribe(args):
    """Convert an audio recording to MIDI."""
    import json
    from moodify.transcription import TranscriptionConfig, TranscriptionError, transcribe_audio

    source = Path(args.audio_path)
    output = Path(args.output) if args.output else Path(args.output_dir) / f"{source.stem}.mid"
    config = TranscriptionConfig(
        onset_threshold=args.onset_threshold, frame_threshold=args.frame_threshold,
        minimum_note_length_ms=args.minimum_note_length,
        minimum_frequency_hz=args.minimum_frequency, maximum_frequency_hz=args.maximum_frequency,
        multiple_pitch_bends=args.multiple_pitch_bends,
        melodia_trick=not args.no_melodia_trick, midi_tempo=args.tempo,
    )
    try:
        result = transcribe_audio(source, output, config=config)
    except (FileNotFoundError, ValueError, TranscriptionError) as exc:
        print(f"ERROR: {exc}")
        return 1
    if args.json:
        print(json.dumps(result.to_dict(), ensure_ascii=False, indent=2))
    else:
        print(f"Moodify transcription: {source.name}")
        print(f"  backend: {result.backend}")
        print(f"  notes:   {result.note_count}")
        print(f"  elapsed: {result.elapsed_seconds:.2f}s")
        print(f"  output:  {result.output_midi}")
    return 0


def _cmd_daw(args) -> int:
    import json
    from pathlib import Path as P

    if args.daw_command == "engines":
        print("  native   available  (Pedalboard DSP)")
        print("  ffmpeg   available  (subprocess render)")
        print("  reaper   exporter_only (NOT_IMPLEMENTED)")
        print("  ardour   exporter_only (NOT_IMPLEMENTED)")
        print("  audacity exporter_only (NOT_IMPLEMENTED)")
        print("  audition human_handoff (GUI only)")
        return 0

    if args.daw_command == "validate":
        data = json.loads(P(args.project).read_text(encoding="utf-8"))
        from moodify.cli_daw.project import CLIDAWProject, Track, SourceSpec, ProcessingNode, MasterSpec
        project = CLIDAWProject(
            project_id=data.get("project_id", ""),
            sample_rate=data.get("sample_rate", 44100),
            tracks=[Track(
                track_id=t["track_id"], name=t.get("name", ""),
                source=SourceSpec(**t.get("source", {})),
                gain_db=t.get("gain_db", 0), pan=t.get("pan", 0),
            ) for t in data.get("tracks", [])],
            master=MasterSpec(processing=[
                ProcessingNode(**n) for n in data.get("master", {}).get("processing", [])
            ]),
        )
        project.validate()
        print(f"Project valid: {project.project_id} ({len(project.tracks)} tracks)")
        return 0

    if args.daw_command == "plan":
        data = json.loads(P(args.project).read_text(encoding="utf-8"))
        out = P(args.output_dir)
        if out.exists() and list(out.iterdir()):
            print(f"ERROR: Output directory not empty: {out}")
            return 2
        out.mkdir(parents=True, exist_ok=True)
        plan = {"project_id": data.get("project_id"), "tracks": len(data.get("tracks", [])),
                "engine": "native", "render_spec": data.get("render", {})}
        (out / "render_plan.json").write_text(json.dumps(plan, indent=2))
        print(f"Plan written: {out / 'render_plan.json'}")
        return 0

    if args.daw_command == "render":
        if not getattr(args, "allow_uncontrolled", False):
            print("ERROR: daw render is UNCONTROLLED_TOOL_EXECUTION; it cannot produce a formal "
                  "Moodify production asset. Use 'case create/execute/verify/package' for formal "
                  "production, or pass --allow-uncontrolled to explicitly accept an uncontrolled render.")
            return 2
        data = json.loads(P(args.project).read_text(encoding="utf-8"))
        out = P(args.output_dir)
        if out.exists() and list(out.iterdir()):
            print(f"ERROR: Output directory not empty: {out}")
            return 2
        from moodify.cli_daw.project import CLIDAWProject, Track, SourceSpec, RenderSpec

        project = CLIDAWProject(
            project_id=data.get("project_id", ""),
            sample_rate=data.get("sample_rate", 44100),
            render=RenderSpec(**data.get("render", {})),
            tracks=[Track(track_id=t["track_id"], name=t.get("name", ""),
                          source=SourceSpec(**t.get("source", {}))) for t in data.get("tracks", [])],
        )
        project.validate()
        engine_name = args.engine
        if engine_name == "native":
            from moodify.cli_daw.engine_native import native_render
            ev = native_render(project, out)
        else:
            from moodify.cli_daw.engine_ffmpeg import ffmpeg_render
            ev = ffmpeg_render(project, out)
        print("Render: engine=%s exit=%s elapsed=%ss classification=UNCONTROLLED_TOOL_EXECUTION"
              % (engine_name, ev.exit_code, ev.elapsed_seconds))
        print("production_controlled=false formal_moodify_asset=false")
        if ev.errors:
            for e in ev.errors:
                print(f"  ERROR: {e}")
        return ev.exit_code if ev.exit_code == 0 else 1

    if args.daw_command == "verify":
        from moodify.cli_daw.verify import verify_run
        report = verify_run(P(args.run_dir))
        print(f"Verify: passed={report.passed} issues={len(report.issues)}")
        for i in report.issues:
            print(f"  ISSUE: {i}")
        return 0 if report.passed else 1

    return 0


def main():
    # AI-native CLI v2 commands share the official Moodify entry point while
    # legacy commands remain available below during the strangler migration.
    if len(sys.argv) > 1 and sys.argv[1] in {
        "version", "capabilities", "project", "asset", "plan", "run", "case",
        "learning", "architecture",
    }:
        from moodify.cli_v2.main import main as cli_v2_main
        return cli_v2_main(sys.argv[1:])
    parser = argparse.ArgumentParser(
        description="Moodify v0.1.0 — AI 音乐二次处理与情绪声波工程系统",
    )
    sub = parser.add_subparsers(dest="command")

    # analyze (v0.1.0 mainline)
    p_analyze = sub.add_parser("analyze", help="频谱分析音频文件 [v0.1.0]")
    p_analyze.add_argument("audio_path", help="音频文件路径")
    p_analyze.add_argument("--output-dir", default="outputs", help="输出目录")
    p_analyze.add_argument("--json", action="store_true", help="JSON 格式输出")

    # process (v0.1.0 mainline)
    p_process = sub.add_parser("process", help="一键处理音频 [v0.1.0]")
    p_process.add_argument("audio_path", help="音频文件路径")
    p_process.add_argument("--preset", default="clean_master",
                           choices=["auto", "warm_vocal", "clean_master", "wide_space"],
                           help="处理预设；auto 会根据扫描报告选择")
    p_process.add_argument("--output-dir", default="outputs", help="输出目录")
    p_process.add_argument("--json", action="store_true", help="JSON 格式输出")

    # batch
    p_batch = sub.add_parser("batch", help="批量处理目录中的音频文件")
    p_batch.add_argument("directory", help="音频文件目录")
    p_batch.add_argument("emotion", help="目标情绪")
    p_batch.add_argument("--platform", default="spotify",
                         choices=["spotify", "youtube", "apple_music"])
    p_batch.add_argument("--output-dir", default="outputs", help="输出目录")

    # emotions
    sub.add_parser("emotions", help="列出可用情绪")

    # crafts
    p_crafts = sub.add_parser("crafts", help="列出工艺卡")
    p_crafts.add_argument("--verbose", action="store_true")

    # serve
    p_serve = sub.add_parser("serve", help="启动 API 服务")
    p_serve.add_argument("--host", default="0.0.0.0")
    p_serve.add_argument("--port", type=int, default=8000)

    # Audacity macro runtime (DSK-MFY-AUDACITY-MACRO-RUNTIME-001)
    p_audacity = sub.add_parser("audacity", help="Audacity 精修宏执行引擎")
    p_audacity_sub = p_audacity.add_subparsers(dest="audacity_command")
    p_audacity_macros = p_audacity_sub.add_parser("macros", help="宏注册表操作")
    p_audacity_macros_sub = p_audacity_macros.add_subparsers(dest="macros_command")
    p_macros_list = p_audacity_macros_sub.add_parser("list", help="列出已注册宏")
    p_macros_list.add_argument("--json", action="store_true", help="JSON 格式输出")
    p_audacity_run = p_audacity_sub.add_parser("macro", help="执行单个宏")
    p_audacity_run_sub = p_audacity_run.add_subparsers(dest="macro_command")
    p_run = p_audacity_run_sub.add_parser("run", help="运行宏并生成 evidence")
    p_run.add_argument("--input", required=True, help="输入音频路径")
    p_run.add_argument("--macro", required=True, help="宏名，如 MFY_REFINE_BALANCED_V001")
    p_run.add_argument("--output", required=True, help="输出音频路径")
    p_run.add_argument("--case-id", default=None, help="case_id（默认自动生成）")
    p_run.add_argument("--evidence-dir", default="outputs/audacity_evidence", help="evidence 输出目录")
    p_run.add_argument("--macro-dir", default=None, help="宏文件目录（用于 evidence 哈希）")

    # ── v0.1.0 commands (new mainline) ──
    p_v01_analyze = sub.add_parser("v01-analyze", help="[v0.1.0] 频谱分析 → PNG + JSON")
    p_v01_analyze.add_argument("audio_path", help="音频文件路径")
    p_v01_analyze.add_argument("--output-dir", default="outputs", help="输出目录")
    p_v01_analyze.add_argument("--json", action="store_true", help="JSON 格式输出")

    p_v01_process = sub.add_parser("v01-process", help="[v0.1.0] 一键处理 → WAV")
    p_v01_process.add_argument("audio_path", help="音频文件路径")
    p_v01_process.add_argument("--preset", default="clean_master",
                               choices=["auto", "warm_vocal", "clean_master", "wide_space"],
                               help="处理预设；auto 会根据扫描报告选择")
    p_v01_process.add_argument("--output-dir", default="outputs", help="输出目录")
    p_v01_process.add_argument("--json", action="store_true", help="JSON 格式输出")

    sub.add_parser("presets", help="列出可用预设 [v0.1.0]")
    sub.add_parser("v01-presets", help="[v0.1.0] 列出可用预设")

    # ── legacy commands (v1.x, kept for backward compat) ──
    # legacy-analyze: 旧系统诊断分析
    p_transcribe = sub.add_parser("transcribe", help="Convert audio to MIDI")
    p_transcribe.add_argument("audio_path", help="Input audio file")
    p_transcribe.add_argument("--output", help="Exact .mid output path")
    p_transcribe.add_argument("--output-dir", default="outputs/midi")
    p_transcribe.add_argument("--onset-threshold", type=float, default=0.5)
    p_transcribe.add_argument("--frame-threshold", type=float, default=0.3)
    p_transcribe.add_argument("--minimum-note-length", type=float, default=127.7, help="Milliseconds")
    p_transcribe.add_argument("--minimum-frequency", type=float)
    p_transcribe.add_argument("--maximum-frequency", type=float)
    p_transcribe.add_argument("--multiple-pitch-bends", action="store_true")
    p_transcribe.add_argument("--no-melodia-trick", action="store_true")
    p_transcribe.add_argument("--tempo", type=float, default=120.0)
    p_transcribe.add_argument("--json", action="store_true")

    p_legacy_analyze = sub.add_parser("legacy-analyze", help="[legacy] 旧系统诊断分析")
    p_legacy_analyze.add_argument("audio_path", help="音频文件路径")
    p_legacy_analyze.add_argument("--json", action="store_true", help="JSON 格式输出")

    # legacy-process: 旧系统一键处理
    p_legacy_process = sub.add_parser("legacy-process", help="[legacy] 旧系统一键处理")
    p_legacy_process.add_argument("audio_path", help="音频文件路径")
    p_legacy_process.add_argument("emotion", help="目标情绪")
    p_legacy_process.add_argument("--platform", default="spotify",
                                   choices=["spotify", "youtube", "apple_music"])
    p_legacy_process.add_argument("--output-dir", default="outputs", help="输出目录")
    p_legacy_process.add_argument("--mode", default="auto", choices=["auto", "expert"])
    p_legacy_process.add_argument("--verbose", action="store_true")

    # ── evaluate commands ──
    # evaluate-run: 批量 AI 评测
    p_eval_run = sub.add_parser("evaluate-run", help="批量 AI 评测（驱动数据飞轮）")
    p_eval_run.add_argument("assets_dir", help="音乐资产目录")
    p_eval_run.add_argument("--output-dir", default="outputs", help="输出目录")
    p_eval_run.add_argument("--emotions", default=None, help="逗号分隔的情绪代码，如 GA,DR,HL")
    p_eval_run.add_argument("--top-k", type=int, default=3, help="每个情绪取 top-k 个候选版本")
    p_eval_run.add_argument("--dry-run", action="store_true", help="只打印计划，不执行")
    p_eval_run.add_argument("--force", action="store_true", help="重新评测已有记录")

    # evaluate-single: 单文件 AI 评测
    p_eval_single = sub.add_parser("evaluate-single", help="对单个文件运行 AI 评测")
    p_eval_single.add_argument("audio_path", help="音频文件路径")
    p_eval_single.add_argument("emotion", help="目标情绪")
    p_eval_single.add_argument("--output-dir", default="outputs", help="输出目录")

    # evaluate-status: 查看 D 值状态
    p_eval_status = sub.add_parser("evaluate-status", help="查看 D 值和校准状态")
    p_eval_status.add_argument("--output-dir", default="outputs", help="输出目录")

    # ── transcribe-stems (v0.2 stem-aware) ──
    p_ts = sub.add_parser("transcribe-stems", help="[v0.2] Transcribe isolated stems to MIDI")
    p_ts.add_argument("--stem", action="append", dest="stems", default=[],
                      help="Stem as kind=path (e.g. --stem vocals=vocals.wav)")
    p_ts.add_argument("--output-dir", required=True, help="Output directory (must be new or empty)")
    p_ts.add_argument("--onset-threshold", type=float)
    p_ts.add_argument("--frame-threshold", type=float)
    p_ts.add_argument("--minimum-note-length", type=float)
    p_ts.add_argument("--tempo", type=float, default=120.0)
    p_ts.add_argument("--json", action="store_true")

    # ── capability registry commands (DSK-MFY-CAPABILITY-ACCRETION-017) ──
    # note: "capabilities" is taken by cli_v2 (static list); registry uses "capability"
    p_capabilities = sub.add_parser("capability", help="Capability registry: probe, regenerate, list")
    capabilities_sub = p_capabilities.add_subparsers(dest="capabilities_command")
    p_cap_probe = capabilities_sub.add_parser("probe", help="Detect installed tools and capabilities (read-only)")
    p_cap_probe.add_argument("--json", action="store_true")
    capabilities_sub.add_parser("regenerate", help="Regenerate registry from current environment facts")
    p_cap_list = capabilities_sub.add_parser("list", help="List registered capabilities and providers")
    p_cap_list.add_argument("--json", action="store_true")
    from moodify.capability_registry.adapters.cli import register_adapter_subparsers

    register_adapter_subparsers(capabilities_sub)
    from moodify.capability_registry.execution.cli import register_execution_subparsers

    register_execution_subparsers(capabilities_sub)
    from moodify.capability_registry.validation.cli import register_validation_subparsers

    register_validation_subparsers(capabilities_sub)
    from moodify.capability_registry.knowledge.cli import register_knowledge_subparsers

    register_knowledge_subparsers(capabilities_sub)

    # ── score engine commands (DSK-MFY-SCORE-ENGINE-009) ──
    p_score = sub.add_parser("score", help="Score engine: import MIDI, export, backends")
    score_sub = p_score.add_subparsers(dest="score_command")
    p_score_import = score_sub.add_parser("import-midi", help="Import MIDI into canonical MoodifyScore JSON")
    p_score_import.add_argument("midi", help="Source .mid file (read-only)")
    p_score_import.add_argument("--output", required=True, help="Canonical JSON output path (must not exist)")
    p_score_export = score_sub.add_parser("export", help="Export score to MusicXML/PDF/SVG via backend")
    p_score_export.add_argument("score", help="Canonical MoodifyScore JSON")
    p_score_export.add_argument("--output-dir", required=True, help="New/empty output directory")
    p_score_backends = score_sub.add_parser("backends", help="List backend capabilities and availability")
    p_score_backends.add_argument("--json", action="store_true")

    # ── CLI DAW commands (DSK-MFY-DAW-BACKENDS-014 v2) ──
    p_daw = sub.add_parser("daw", help="CLI-first DAW engine (no GUI)")
    daw_sub = p_daw.add_subparsers(dest="daw_command")
    daw_sub.add_parser("engines", help="List available engines")
    p_validate = daw_sub.add_parser("validate", help="Validate project schema")
    p_validate.add_argument("--project", required=True)
    p_plan = daw_sub.add_parser("plan", help="Generate render plan")
    p_plan.add_argument("--project", required=True)
    p_plan.add_argument("--output-dir", required=True)
    p_render = daw_sub.add_parser("render", help="Render project")
    p_render.add_argument("--project", required=True)
    p_render.add_argument("--engine", default="native", choices=["native", "ffmpeg"])
    p_render.add_argument("--output-dir", required=True)
    p_render.add_argument("--allow-uncontrolled", action="store_true",
                          help="explicitly accept an uncontrolled render (no production case)")
    p_verify = daw_sub.add_parser("verify", help="Verify render output")
    p_verify.add_argument("run_dir")

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        return 0

    if hasattr(args, "daw_command") and args.command == "daw":
        return _cmd_daw(args)
    if args.command == "score":
        from moodify.score_engine.cli import (
            cmd_score_backends,
            cmd_score_export,
            cmd_score_import_midi,
        )

        dispatch = {
            "import-midi": cmd_score_import_midi,
            "export": cmd_score_export,
            "backends": cmd_score_backends,
        }
        handler = dispatch.get(getattr(args, "score_command", None))
        if handler is None:
            print("ERROR: score command required: import-midi | export | backends")
            return 2
        return handler(args)
    if args.command == "capability":
        from moodify.capability_registry.cli import cmd_capabilities

        return cmd_capabilities(args)
    if args.command == "audacity":
        return cmd_audacity(args)

    handlers = {
        # v0.1.0 mainline
        "analyze": cmd_v01_analyze,
        "process": cmd_v01_process,
        "presets": cmd_v01_presets,
        "v01-analyze": cmd_v01_analyze,
        "v01-process": cmd_v01_process,
        "v01-presets": cmd_v01_presets,
        "transcribe": cmd_transcribe,
        "transcribe-stems": cmd_transcribe_stems,
        # legacy
        "legacy-analyze": cmd_legacy_analyze,
        "legacy-process": cmd_legacy_process,
        "batch": cmd_batch,
        "emotions": cmd_emotions,
        "crafts": cmd_crafts,
        "serve": cmd_serve,
        "evaluate-run": cmd_evaluate_run,
        "evaluate-single": cmd_evaluate_single,
        "evaluate-status": cmd_evaluate_status,
    }
    return handlers[args.command](args)


if __name__ == "__main__":
    sys.exit(main())
