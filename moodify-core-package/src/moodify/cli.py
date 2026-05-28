"""
Moodify CLI — 命令行接口
=========================
Usage:
  moodify analyze <audio_path>              # 诊断分析
  moodify process <audio_path> <emotion>    # 一键处理
  moodify batch <dir> <emotion>             # 批量处理
  moodify emotions                          # 列出可用情绪
  moodify crafts                            # 列出工艺卡
  moodify serve                             # 启动 API 服务
"""

import sys
import os
import argparse
import time
from pathlib import Path


def cmd_analyze(args):
    """诊断分析命令"""
    from moodify.diagnosis import DiagnosisEngine, DefectClassifier, HealthScorer

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
    print(f"  S1_SubPresence:  {s.S1_SubPresence:+.1f} dB")
    print(f"  S2_BassWarmth:   {s.S2_BassWarmth:+.1f} dB")
    print(f"  S3_MidClarity:   {s.S3_MidClarity:.3f}")
    print(f"  S4_AirBand:      {s.S4_AirBand:+.1f} dB")
    print(f"  S5_SpectralTilt: {s.S5_SpectralTilt:+.1f} dB/oct")

    print(f"\n[Dynamics]")
    print(f"  D1_LRA:          {d.D1_LRA:.1f} LU")
    print(f"  D2_ChorusImpact: {d.D2_ChorusImpact:.1f} LU")
    print(f"  D3_MicroDynamics:{d.D3_MicroDynamics:.2f} LU")
    print(f"  D4_PLR:          {d.D4_PLR:.1f} dB")

    print(f"\n[Space]")
    print(f"  SP1_Correlation: {sp.SP1_Correlation:.3f}")
    print(f"  SP2_ForeBackSep: {sp.SP2_ForeBackSep:.1f} dB")
    print(f"  SP3_RT60Consist: {sp.SP3_RT60Consist:.3f} s")
    print(f"  SP4_WidthHealth: {sp.SP4_WidthHealth}")

    print(f"\n[Layers]")
    print(f"  L1_VocalSNR:     {l.L1_VocalSNR:.1f} dB")
    print(f"  L2_BassClarity:  {l.L2_BassClarity:.3f}")
    print(f"  L3_DrumDetect:   {l.L3_DrumDetect:.3f}")

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
        print(json.dumps(report, ensure_ascii=False, indent=2))

    return 0


def cmd_process(args):
    """一键处理命令"""
    from moodify.orchestration import WorkflowOrchestrator

    path = args.audio_path
    emotion = args.emotion
    if not Path(path).exists():
        print(f"ERROR: File not found: {path}")
        return 1

    output_dir = getattr(args, 'output_dir', 'outputs')
    print(f"Processing: {path}")
    print(f"Emotion: {emotion}")
    print(f"Platform: {getattr(args, 'platform', 'spotify')}")

    orch = WorkflowOrchestrator()
    result = orch.process(
        input_path=path,
        emotion_target=emotion,
        platform=getattr(args, 'platform', 'spotify'),
        mode=getattr(args, 'mode', 'auto'),
        output_dir=output_dir,
    )

    print(f"\n=== Processing Report ===")
    print(f"Process ID: {result.process_id}")
    print(f"Success: {result.success}")
    for p in result.phases:
        icon = ">" if p.status.value == "completed" else (
            "-" if p.status.value == "skipped" else "!")
        print(f"  {icon} P{p.phase} {p.name}: {p.status.value} ({p.elapsed_ms:.0f}ms)")
        if getattr(args, 'verbose', False) and p.warnings:
            for w in p.warnings:
                print(f"     {w}")
    print(f"WHS: {result.whs_before:.0f} -> {result.whs_after:.0f}  "
          f"EDS: {result.eds:.0f}  Risk: {result.total_risk:.2f} [{result.risk_level}]")
    print(f"Output: {result.output_path}")
    return 0 if result.success else 1


def cmd_batch(args):
    """批量处理命令"""
    from moodify.orchestration import WorkflowOrchestrator

    directory = args.directory
    emotion = args.emotion
    if not Path(directory).is_dir():
        print(f"ERROR: Directory not found: {directory}")
        return 1

    output_dir = getattr(args, 'output_dir', 'outputs')
    extensions = {'.wav', '.mp3', '.flac', '.ogg'}
    files = sorted(
        f for f in Path(directory).iterdir()
        if f.suffix.lower() in extensions
    )

    if not files:
        print(f"No audio files found in: {directory}")
        return 1

    print(f"Batch processing {len(files)} files with emotion: {emotion}")
    print(f"Output dir: {output_dir}\n")

    orch = WorkflowOrchestrator()
    success_count = 0

    for i, filepath in enumerate(files, 1):
        print(f"[{i}/{len(files)}] {filepath.name} ... ", end="", flush=True)
        try:
            result = orch.process(
                input_path=str(filepath),
                emotion_target=emotion,
                platform=getattr(args, 'platform', 'spotify'),
                mode='auto',
                output_dir=output_dir,
            )
            if result.success:
                print(f"OK ({result.total_elapsed_ms:.0f}ms)")
                success_count += 1
            else:
                print("FAILED")
        except Exception as e:
            print(f"ERROR: {e}")

    print(f"\nBatch complete: {success_count}/{len(files)} succeeded")
    return 0 if success_count == len(files) else 1


def cmd_emotions(args):
    """列出可用情绪"""
    from moodify.knowledge import EMOTION_TARGETS_V2, CRAFT_CHAINS_15PARAMS

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
    from moodify.knowledge import generate_craft_cards_from_data

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
    }
    return handlers[args.command](args)


if __name__ == "__main__":
    sys.exit(main())
