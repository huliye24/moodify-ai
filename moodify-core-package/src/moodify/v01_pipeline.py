"""v01_pipeline.py — Moodify v0.1.0 main processing pipeline.

Import → Analyze → Diagnose → Process → Export

This is the ONLY orchestration file the v0.1.0 mainline touches.
The v1.x WorkflowOrchestrator (938 lines) is preserved for future use.
"""

import json
import os
import time
from pathlib import Path

from moodify.audio_io import load_audio
from moodify.processing.pedalboard_chain import MoodifyDSPChain
from moodify.v01_types import AudioMetrics, DiagnosisReport, ProcessResult
from moodify.v01_analyzer import analyze
from moodify.v01_diagnostics import diagnose
from moodify.v01_exporter import export
from moodify.v01_presets import get_preset, list_presets


def process_audio(input_path: str,
                  preset: str = "clean_master",
                  output_dir: str = "outputs") -> ProcessResult:
    """Run the complete v0.1.0 pipeline on one audio file.

    Args:
        input_path: path to WAV/MP3/FLAC file
        preset: key from v01_presets.PRESETS ("warm_vocal"|"clean_master"|"wide_space")
        output_dir: output directory

    Returns:
        ProcessResult with metrics, diagnosis, and output path
    """
    t0 = time.perf_counter()

    # Validate
    if not os.path.exists(input_path):
        return ProcessResult(input_path=input_path, success=False,
                            error=f"File not found: {input_path}")

    preset_info = get_preset(preset)
    if preset_info is None:
        valid = ", ".join(list_presets())
        return ProcessResult(input_path=input_path, success=False,
                            error=f"Unknown preset '{preset}'. Valid: {valid}")

    try:
        # Phase 1: Analyze
        metrics = analyze(input_path, output_dir)

        # Phase 2: Diagnose
        report = diagnose(metrics)

        # Phase 3: Process
        audio, sr = load_audio(input_path, always_2d=False)
        chain = MoodifyDSPChain(preset_info["params"])
        processed = chain.process(audio, sr)

        # Phase 4: Export
        output_path = export(processed, sr, input_path, preset, output_dir)

        elapsed = time.perf_counter() - t0

        # Save report alongside output
        _save_report(report, output_path, preset, elapsed)

        return ProcessResult(
            input_path=input_path,
            output_path=output_path,
            preset=preset,
            metrics_before=metrics,
            diagnosis=report,
            success=True,
        )

    except Exception as e:
        return ProcessResult(
            input_path=input_path,
            preset=preset,
            success=False,
            error=str(e),
        )


def _save_report(report: DiagnosisReport, output_path: str,
                 preset: str, elapsed_s: float) -> None:
    """Write JSON diagnosis report next to the output file."""
    report_path = output_path.replace(".wav", "_report.json")
    data = {
        "preset": preset,
        "elapsed_s": round(elapsed_s, 1),
        **report.to_dict(),
    }
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
