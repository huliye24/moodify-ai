"""DecisionOrchestrator: analyze → plan → dry-run → execute → verify."""
from __future__ import annotations
import hashlib
import json
import time
from dataclasses import dataclass, field
from pathlib import Path
import numpy as np
import librosa

@dataclass
class AnalysisReport:
    duration_s: float = 0; sample_rate: int = 0; peak_db: float = 0; rms_db: float = 0
    crest_factor: float = 0; spectral_centroid_hz: float = 0; loudness_lufs: float | None = None
    has_clipping: bool = False; silence_ratio: float = 0; warnings: list[str] = field(default_factory=list)

@dataclass
class TreatmentPlan:
    plan_id: str; steps: list[dict] = field(default_factory=list)
    dry_run: bool = True; estimated_s: float = 0; warnings: list[str] = field(default_factory=list)
    source_hash: str = ""; analysis: dict = field(default_factory=dict)

def analyze_audio(path: str) -> AnalysisReport:
    y, sr = librosa.load(path, sr=None, mono=True)
    r = AnalysisReport(duration_s=round(float(len(y))/sr,3), sample_rate=sr)
    peak = float(np.max(np.abs(y))); r.peak_db = round(20*np.log10(max(peak,1e-12)),2)
    rms = float(np.sqrt(np.mean(y.astype(np.float64)**2))); r.rms_db = round(20*np.log10(max(rms,1e-12)),2)
    r.crest_factor = round(r.peak_db - r.rms_db, 2)
    S = np.abs(librosa.stft(y, n_fft=2048)); freqs = librosa.fft_frequencies(sr=sr, n_fft=2048)
    r.spectral_centroid_hz = round(float(np.sum(freqs * S.sum(axis=1)) / max(S.sum(), 1e-12)), 1)
    r.has_clipping = peak > 0.999
    silence = float(np.sum(np.abs(y) < 1e-6) / len(y)); r.silence_ratio = round(silence, 4)
    try:
        import pyloudnorm as pn; meter = pn.Meter(sr)
        r.loudness_lufs = round(float(meter.integrated_loudness(y)), 1)
    except Exception: r.warnings.append("LUFS unavailable")
    return r

def generate_plan(spec: dict, analysis: AnalysisReport, intent: dict = None) -> TreatmentPlan:
    steps = []
    intent = intent or {}
    target_peak = intent.get("target_peak_db", -1.0)
    if analysis.peak_db < target_peak:
        steps.append({"type":"gain","params":{"gain_db":round(target_peak-analysis.peak_db,1)},"reason":f"Normalize to {target_peak}dB peak"})
    if analysis.crest_factor > 15: steps.append({"type":"compand","params":{"attack":0.1,"decay":0.3,"threshold":"-60,-60,-12","ratio":2},"reason":"Reduce excessive crest factor"})
    if intent.get("target","") == "warm": steps.append({"type":"gain","params":{"gain_db":1.5},"reason":"Intent: warmth boost"})
    plan_id = hashlib.sha256(json.dumps(steps,sort_keys=True).encode()).hexdigest()[:12]
    source_path = spec.get("source","")
    sha = hashlib.sha256(Path(source_path).read_bytes()).hexdigest() if Path(source_path).exists() and source_path else ""
    return TreatmentPlan(plan_id=plan_id, steps=steps, dry_run=True,
        estimated_s=round(analysis.duration_s*1.5,1), source_hash=sha,
        analysis={"peak_db":analysis.peak_db,"rms_db":analysis.rms_db,"crest":analysis.crest_factor,"centroid_hz":analysis.spectral_centroid_hz,"lufs":analysis.loudness_lufs})

def execute_plan(plan: TreatmentPlan, source: str, output_dir: Path) -> dict:
    """[INTERNAL/LEGACY] Uncontrolled SoX execution.

    Do not use for formal production. This path has no ProductionCase, no
    approval gate, no execution envelope, and no verification. It cannot
    produce a formal Moodify production asset; results are always classified
    ``UNCONTROLLED_TOOL_EXECUTION``. Use ``ProductionControlService.execute``
    for formal production.
    """
    from moodify.cli_daw.adapters.sox import SoXAdapter
    adapter = SoXAdapter()
    p = adapter.probe()
    if p["status"] != "available":
        return {"production_controlled": False,
                "classification": "UNCONTROLLED_TOOL_EXECUTION",
                "formal_moodify_asset": False,
                "status":"UNCONTROLLED_FAILED",
                "error":f"SoX {p['status']}: {p.get('error','')}"}

    output_dir.mkdir(parents=True, exist_ok=True)
    current_input = source
    results = []
    t0 = time.perf_counter()

    for i, step in enumerate(plan.steps):
        out_name = f"step_{i}_{step['type']}.wav"
        params = {"input": current_input, "output": out_name}
        params.update(step.get("params", {}))
        ev = adapter.execute(step["type"], params, output_dir)
        results.append({"step":i,"type":step["type"],"exit":ev.exit_code,"elapsed":ev.elapsed_s,"output":ev.output_path,"error":ev.stderr[:200] if ev.exit_code!=0 else ""})
        if ev.exit_code == 0 and Path(ev.output_path).exists():
            current_input = ev.output_path

    elapsed = round(time.perf_counter()-t0, 3)
    success = all(r["exit"]==0 for r in results)
    final_output = str(output_dir / f"step_{len(plan.steps)-1}_{plan.steps[-1]['type']}.wav") if plan.steps else source
    sha = hashlib.sha256(Path(final_output).read_bytes()).hexdigest() if Path(final_output).exists() else ""
    return {"production_controlled": False,
            "classification": "UNCONTROLLED_TOOL_EXECUTION",
            "formal_moodify_asset": False,
            "status":"UNCONTROLLED_OK" if success else "UNCONTROLLED_PARTIAL",
            "output":final_output,"output_hash":sha,"elapsed_s":elapsed,"steps_executed":len(results),"steps":results}
