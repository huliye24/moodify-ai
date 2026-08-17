"""Golden reconstruction pipeline (MFY-CR-P06).

    Source -> freeze -> Era Diagnostic -> Objective plans -> render A/B/C
      -> hard gates -> Identity Guard -> technical ranking -> blind kit

Deterministic except where explicitly seeded; SOURCE always eligible.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

import soundfile as sf

from moodify.auditory.metrics import compute_metrics
from moodify.auditory.stereo import compute_stereo_metrics
from moodify.data_factory.intervention import execute_intervention
from moodify.data_factory.models import InterventionPlan
from moodify.era_diagnostic.contract import EraDiagnosticFinding
from moodify.era_diagnostic.engine import run_era_diagnostic
from moodify.identity_guard.guard import guard_candidate
from moodify.identity_guard.ranking import rank_candidates
from moodify.reconstruction.blind import make_blind_kit
from moodify.reconstruction.objective import RECONSTRUCTION_OBJECTIVE_POLICY_V1, plan_from_findings
from moodify.reconstruction.record import GoldenReconstructionRecord

PIPELINE_VERSION = "golden-pipeline-v0.1"
_HARD_GATES = RECONSTRUCTION_OBJECTIVE_POLICY_V1["hard_gates"]


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


@dataclass
class PipelineResult:
    source: dict
    diagnostics: list[EraDiagnosticFinding]
    plans: list[dict]
    candidates: dict[str, dict]          # candidate_id -> {path, sha256, metrics, gates}
    identity: dict[str, dict]            # candidate_id -> verdict dict
    ranking: list[dict]
    record: GoldenReconstructionRecord
    blind_kit: dict = field(default_factory=dict)


def _metrics_of(path: Path, sr: int = 48000) -> dict:
    audio, s = sf.read(str(path), dtype="float32")
    if audio.ndim == 1:
        audio = audio[:, None]
    probe = type("Probe", (), {"duration_seconds": audio.shape[0] / s,
                               "sample_rate": s, "sha256": "local", "format": "wav"})()
    metrics = compute_metrics(audio, s, probe)
    metrics.update(compute_stereo_metrics(audio))
    metrics["duration"] = {"value": round(audio.shape[0] / s, 3), "unit": "s",
                           "method": "soundfile", "status": "VALID", "warnings": []}
    metrics["sample_rate"] = {"value": s, "unit": "Hz", "method": "soundfile",
                              "status": "VALID", "warnings": []}
    metrics["channels"] = {"value": audio.shape[1], "unit": "ch", "method": "soundfile",
                           "status": "VALID", "warnings": []}
    return metrics


def check_hard_gates(source_metrics: dict, candidate_metrics: dict) -> list[str]:
    """Return list of failed hard gates (empty = passed)."""
    failures: list[str] = []
    s_clip = (source_metrics.get("clipping_sample_ratio") or {}).get("value") or 0.0
    c_clip = (candidate_metrics.get("clipping_sample_ratio") or {}).get("value") or 0.0
    if c_clip - s_clip > _HARD_GATES["max_new_clipping_ratio"]:
        failures.append("NO_NEW_CLIPPING")
    s_dur = (source_metrics.get("duration") or {}).get("value")
    c_dur = (candidate_metrics.get("duration") or {}).get("value")
    if s_dur is not None and c_dur is not None and abs(c_dur - s_dur) > _HARD_GATES["max_duration_delta_s"]:
        failures.append("DURATION_PRESERVED")
    s_ch = (source_metrics.get("channels") or {}).get("value")
    c_ch = (candidate_metrics.get("channels") or {}).get("value")
    if s_ch is not None and c_ch is not None and c_ch != s_ch:
        failures.append("CHANNELS_PRESERVED")
    s_lufs = (source_metrics.get("integrated_lufs") or {}).get("value")
    c_lufs = (candidate_metrics.get("integrated_lufs") or {}).get("value")
    if s_lufs is not None and c_lufs is not None and abs(c_lufs - s_lufs) > _HARD_GATES["max_loudness_delta_lufs"]:
        failures.append("LOUDNESS_WITHIN_BUDGET")
    return failures


def run_golden_pipeline(
    source_wav: Path,
    out_dir: Path,
    *,
    rights_status: str = "OWNED",
    source_alias: str = "source",
    era_hint: str | None = None,
    blind_seed: int = 20260817,
    created_at: str | None = None,
) -> PipelineResult:
    source_wav = Path(source_wav)
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    created_at = created_at or datetime.now(timezone.utc).isoformat(timespec="seconds")

    # ---- Source freeze ----
    source_sha = sha256_file(source_wav)
    source_metrics = _metrics_of(source_wav)
    source = {
        "alias": source_alias,
        "path": str(source_wav),
        "sha256": source_sha,
        "duration_s": (source_metrics.get("duration") or {}).get("value"),
        "sample_rate": (source_metrics.get("sample_rate") or {}).get("value"),
        "channels": (source_metrics.get("channels") or {}).get("value"),
        "rights_status": rights_status,
        "era_hint": era_hint,
    }
    (out_dir / "source_manifest.json").write_text(
        json.dumps(source, ensure_ascii=False, indent=2), encoding="utf-8")

    # ---- Stage 1: Era Diagnostic ----
    findings = run_era_diagnostic(source_metrics, production_case_id=source_alias,
                                  created_at=created_at)
    (out_dir / "era_diagnostic.v0.1.json").write_text(
        json.dumps([f.to_dict() for f in findings], ensure_ascii=False, indent=2),
        encoding="utf-8")

    # ---- Stage 2: Objective (A/B/C + SOURCE) ----
    plans = plan_from_findings(findings, source_sha256=source_sha)

    # ---- Stage 3: Render + hard gates ----
    candidates: dict[str, dict] = {"SOURCE": {
        "path": str(source_wav), "sha256": source_sha, "metrics": source_metrics,
        "gates": [], "plan_hash": "source", "intensity": 0.0,
    }}
    candidates_dir = out_dir / "candidates"
    for plan in plans:
        if plan["candidate_id"] == "SOURCE":
            continue
        cand_path = candidates_dir / f"{plan['candidate_id']}.wav"
        ip = InterventionPlan(
            case_id=source_alias, plan_id=plan["plan_hash"],
            candidate_label=plan["label"], candidate_id=plan["candidate_id"],
            strategy="era-objective", intensity=plan["intensity"],
            source_sha256=source_sha, scan_profile_id="MFY-WSE-SCAN-PROFILE-001",
            scan_profile_hash="f0ff177d", plan_generator_version=plan["plan_hash"],
            params=plan["params"],
        )
        result = execute_intervention(source_wav, cand_path, ip)
        cand_metrics = _metrics_of(cand_path)
        gates = check_hard_gates(source_metrics, cand_metrics)
        candidates[plan["candidate_id"]] = {
            "path": str(cand_path), "sha256": result.output_sha256,
            "metrics": cand_metrics, "gates": gates, "plan_hash": plan["plan_hash"],
            "intensity": plan["intensity"],
        }

    # ---- Stage 4: Identity Guard ----
    identity: dict[str, dict] = {}
    for cid, cand in candidates.items():
        if cid == "SOURCE":
            continue
        verdict = guard_candidate(source_metrics, cand["metrics"],
                                  candidate_id=cid, source_id="SOURCE")
        identity[cid] = verdict.to_dict()

    # ---- Stage 5: Technical ranking ----
    from moodify.identity_guard.guard import guard_candidate as _gc
    verdicts = []
    for cid, cand in candidates.items():
        if cid == "SOURCE":
            continue
        verdicts.append(_gc(source_metrics, cand["metrics"], candidate_id=cid, source_id="SOURCE"))
    objective_progress = {cid: candidates[cid]["intensity"] for cid in candidates if cid != "SOURCE"}
    ranking = [r.to_dict() for r in rank_candidates(
        verdicts, objective_progress=objective_progress, source_id="SOURCE")]
    # Technical top: the best auto-approvable (PASS) candidate; SOURCE wins when none exists.
    auto_eligible = [r for r in ranking if r["candidate_id"] != "SOURCE" and r["auto_approvable"]]
    technical_top = auto_eligible[0]["candidate_id"] if auto_eligible else "SOURCE"

    # ---- Blind kit ----
    candidate_wavs = {cid: Path(c["path"]) for cid, c in candidates.items() if cid != "SOURCE"}
    kit = make_blind_kit(source_wav, candidate_wavs, out_dir, seed=blind_seed)
    blind_kit = kit.to_dict()

    record = GoldenReconstructionRecord(
        record_id=f"GOLDEN-001-{source_alias}",
        source_hash=source_sha,
        rights_status=rights_status,
        diagnostic_version="era-diagnostic-v0.1",
        objective_version=RECONSTRUCTION_OBJECTIVE_POLICY_V1["version"],
        identity_guard_version="identity-guard-v0.1",
        candidate_id="TBD",
        plan_hash="TBD",
        engine_version=PIPELINE_VERSION,
        technical_result={"ranking": ranking, "technical_top": technical_top},
        human_result={},
        hardware_observations=[],
        created_at=created_at,
    )
    (out_dir / "golden_record.json").write_text(
        json.dumps(record.to_dict(), ensure_ascii=False, indent=2), encoding="utf-8")

    return PipelineResult(
        source=source, diagnostics=findings, plans=plans, candidates=candidates,
        identity=identity, ranking=ranking, record=record, blind_kit=blind_kit,
    )
