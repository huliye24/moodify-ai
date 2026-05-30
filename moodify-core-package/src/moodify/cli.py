"""
Moodify CLI — AI music post-processing, one command.

Usage:
  moodify process <audio> <emotion>    Process one file (WAV/MP3/FLAC)
  moodify batch <dir> <emotion>        Process all audio files in a directory
  moodify analyze <audio>              Diagnose only, no processing
  moodify emotions                     List 8 emotion targets
  moodify serve                        Start API server
"""

import sys, os, argparse, time
from pathlib import Path

SUPPORTED_EXTENSIONS = {'.wav', '.mp3', '.flac', '.aiff', '.aif', '.m4a', '.ogg'}


def cmd_analyze(args):
    """诊断分析命令"""
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
    s, d, sp, l, e = ws.Spectrum, ws.Dynamics, ws.Space, ws.Layers, ws.Emotion
    print(f"\n[Spectrum]")
    print(f"  S1_SubPresence:  {s.S1_SubPresence.value:+.1f} dB")
    print(f"  S2_BassWarmth:   {s.S2_BassWarmth.value:+.1f} dB")
    print(f"  S3_MidClarity:   {s.S3_MidClarity.value:.3f}")
    print(f"  S4_AirBand:      {s.S4_AirBand.value:+.1f} dB")
    print(f"  S5_SpectralTilt: {s.S5_SpectralTilt.value:+.1f} dB/oct")

    print(f"\n[Dynamics]")
    print(f"  D1_LRA:          {d.D1_LRA.value:.1f} LU")
    print(f"  D2_ChorusImpact: {d.D2_ChorusImpact.value:.1f} LU")
    print(f"  D3_MicroDynamics:{d.D3_MicroDynamics.value:.2f} LU")
    print(f"  D4_PLR:          {d.D4_PLR.value:.1f} dB")

    print(f"\n[Space]")
    print(f"  SP1_Correlation: {sp.SP1_Correlation.value:.3f}")
    print(f"  SP2_ForeBackSep: {sp.SP2_ForeBackSep.value:.1f} dB")
    print(f"  SP3_RT60Consist: {sp.SP3_RT60Consist.value:.3f} s")
    print(f"  SP4_WidthHealth: {sp.SP4_WidthHealth}")

    print(f"\n[Layers]")
    print(f"  L1_VocalSNR:     {l.L1_VocalSNR.value:.1f} dB")
    print(f"  L2_BassClarity:  {l.L2_BassClarity.value:.3f}")
    print(f"  L3_DrumDetect:   {l.L3_DrumDetect.value:.3f}")

    print(f"\n[Health]")
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
            "layers": l.to_dict(),
            "emotion": e.to_dict(),
            "whs": whs,
            "defects": [{"id": d.defect_id, "severity": d.severity,
                         "description": d.description_zh} for d in defects],
        }
        print("\n--- JSON ---")
        print(json.dumps(report, ensure_ascii=False, indent=2, default=str))

    return 0


def cmd_process(args):
    """Process one audio file — WAV, MP3, FLAC all supported."""
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
                ok += 1; eds_sum += result.eds
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
            chain_info = f"[craft chain ready]"
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


def main():
    parser = argparse.ArgumentParser(
        description="Moodify Core Engine — AI 音乐情绪波场显影器",
    )
    sub = parser.add_subparsers(dest="command")

    # analyze
    p_analyze = sub.add_parser("analyze", help="诊断分析音频文件")
    p_analyze.add_argument("audio_path", help="音频文件路径")
    p_analyze.add_argument("--json", action="store_true", help="JSON 格式输出")

    # process
    p_process = sub.add_parser("process", help="一键处理音频")
    p_process.add_argument("audio_path", help="音频文件路径")
    p_process.add_argument("emotion", help="目标情绪 (温柔觉醒/神圣空灵/...)")
    p_process.add_argument("--platform", default="spotify",
                           choices=["spotify", "youtube", "apple_music"])
    p_process.add_argument("--output-dir", default="outputs", help="输出目录")
    p_process.add_argument("--mode", default="auto", choices=["auto", "expert"])
    p_process.add_argument("--verbose", action="store_true")

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

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        return 0

    handlers = {
        "analyze": cmd_analyze,
        "process": cmd_process,
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
