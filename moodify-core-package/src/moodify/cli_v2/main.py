"""Moodify AI-native CLI v2.

Stdout is reserved for one JSON command-result document. Diagnostics and
errors go to stderr. The module deliberately keeps rendering behind the
application boundary provided by the canonical project on disk.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import tempfile
from pathlib import Path
from typing import Any, Sequence
from uuid import uuid4

SCHEMA_VERSION = "1.0.0"
PROJECT_FILE = "project.json"


class CLIError(Exception):
    def __init__(self, code: str, message: str, exit_code: int = 2, payload: dict | None = None):
        super().__init__(message)
        self.code = code
        self.message = message
        self.exit_code = exit_code
        self.payload = payload


def _result(command: str, status: str = "ok", **fields: Any) -> dict[str, Any]:
    return {"schema_version": SCHEMA_VERSION, "command": command, "status": status, **fields}


def _emit(payload: dict[str, Any], *, error: bool = False) -> None:
    stream = sys.stderr if error else sys.stdout
    print(json.dumps(payload, ensure_ascii=False, sort_keys=True), file=stream)


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _safe_project_dir(raw: str, *, must_exist: bool) -> Path:
    path = Path(raw).expanduser().absolute()
    if path.exists() and path.is_symlink():
        raise CLIError("UNSAFE_PROJECT_PATH", "Project directory may not be a symlink or junction")
    if must_exist and (not path.is_dir() or not (path / PROJECT_FILE).is_file()):
        raise CLIError("PROJECT_NOT_FOUND", f"No Moodify project at {path}")
    return path


def _read_project(raw: str) -> tuple[Path, dict[str, Any]]:
    root = _safe_project_dir(raw, must_exist=True)
    try:
        data = json.loads((root / PROJECT_FILE).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise CLIError("PROJECT_INVALID", f"Cannot read project: {exc}") from exc
    required = {"schema_version", "project_id", "title", "assets", "plans", "runs"}
    missing = sorted(required - data.keys())
    if missing or data.get("schema_version") != SCHEMA_VERSION:
        raise CLIError("PROJECT_INVALID", f"Project schema invalid; missing={missing}")
    return root, data


def _atomic_write(path: Path, data: dict[str, Any]) -> None:
    fd, tmp_name = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as handle:
            json.dump(data, handle, ensure_ascii=False, indent=2, sort_keys=True)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(tmp_name, path)
    finally:
        if os.path.exists(tmp_name):
            os.unlink(tmp_name)


def _parse_intent(raw: str) -> dict[str, Any]:
    candidate = Path(raw)
    try:
        text = candidate.read_text(encoding="utf-8") if candidate.is_file() else raw
        value = json.loads(text)
    except (OSError, json.JSONDecodeError) as exc:
        raise CLIError("INTENT_INVALID", f"Intent must be a JSON object or JSON file: {exc}") from exc
    if not isinstance(value, dict):
        raise CLIError("INTENT_INVALID", "Intent must be a JSON object")
    return value


def cmd_version(_: argparse.Namespace) -> dict[str, Any]:
    from moodify import __version__
    return _result("version", product="moodify", version=__version__)


def cmd_capabilities(_: argparse.Namespace) -> dict[str, Any]:
    capabilities = {
        "canonical_project": {"status": "available", "backend": "core"},
        "cli_daw_native_minimal": {"status": "available", "backend": "native", "limits": ["single_source", "gain_only"]},
        "cli_daw_ffmpeg": {"status": "experimental", "backend": "ffmpeg"},
        "transcription": {"status": "available", "backend": "basic_pitch_onnx"},
        "stem_transcription": {"status": "available", "backend": "basic_pitch_onnx"},
        "score": {"status": "experimental", "backend": "external"},
        "spectral_evidence": {"status": "available", "backend": "science_package"},
        "reaper": {"status": "not_implemented", "backend": None},
        "audition": {"status": "human_handoff", "backend": None},
    }
    return _result("capabilities", capabilities=capabilities)


def cmd_project_init(args: argparse.Namespace) -> dict[str, Any]:
    root = _safe_project_dir(args.project_dir, must_exist=False)
    if root.exists():
        raise CLIError("OUTPUT_EXISTS", f"Project directory already exists: {root}")
    root.mkdir(parents=True)
    data = {
        "schema_version": SCHEMA_VERSION,
        "project_id": str(uuid4()),
        "title": args.title or root.name,
        "assets": [], "decisions": [], "plans": [], "runs": [],
        "revisions": [{"revision_id": "1", "description": "Initialized"}],
        "evidence": [], "metadata": {},
    }
    _atomic_write(root / PROJECT_FILE, data)
    return _result("project.init", "created", project_id=data["project_id"], project_dir=str(root))


def cmd_project_inspect(args: argparse.Namespace) -> dict[str, Any]:
    _, data = _read_project(args.project_dir)
    return _result("project.inspect", project_id=data["project_id"], project=data)


def cmd_asset_import(args: argparse.Namespace) -> dict[str, Any]:
    root, data = _read_project(args.project_dir)
    src = Path(args.input_path).expanduser().resolve(strict=True)
    if not src.is_file():
        raise CLIError("SOURCE_INVALID", f"Source is not a file: {src}")
    if args.copy_mode != "reference":
        raise CLIError("CAPABILITY_UNSUPPORTED", "Only read-only reference imports are implemented")
    sha = _sha256(src)
    existing = next((a for a in data["assets"] if a.get("sha256") == sha and a.get("path") == str(src)), None)
    if existing:
        asset = existing
        created = False
    else:
        asset = {"asset_id": str(uuid4()), "kind": "audio", "path": str(src), "sha256": sha, "role": "source", "metadata": {}}
        data["assets"].append(asset)
        _atomic_write(root / PROJECT_FILE, data)
        created = True
    return _result("asset.import", "created" if created else "unchanged", project_id=data["project_id"], asset=asset)


def cmd_plan_create(args: argparse.Namespace) -> dict[str, Any]:
    root, data = _read_project(args.project_dir)
    intent = _parse_intent(args.intent)
    if not data["assets"]:
        raise CLIError("ASSET_REQUIRED", "Import an audio asset before creating a plan")
    gain_db = float(intent.get("gain_db", 0.0))
    if not -24.0 <= gain_db <= 12.0:
        raise CLIError("PLAN_UNSAFE", "gain_db must be between -24 and +12 dB")
    plan = {
        "plan_id": str(uuid4()), "intent": intent,
        "steps": [{"type": "gain", "params": {"gain_db": gain_db}}],
        "dry_run": bool(args.dry_run), "warnings": [],
    }
    data["plans"].append(plan)
    _atomic_write(root / PROJECT_FILE, data)
    return _result("plan.create", "planned", project_id=data["project_id"], plan=plan)


LEGACY_CLASSIFICATION = {
    "production_controlled": False,
    "classification": "UNCONTROLLED_TOOL_EXECUTION",
    "formal_moodify_asset": False,
}


def _require_uncontrolled(args: argparse.Namespace) -> None:
    if not args.allow_uncontrolled:
        raise CLIError(
            "CONTROL_REQUIRED",
            "Legacy 'run' paths are uncontrolled and cannot produce a formal Moodify "
            "production asset. Use 'case execute'/'case verify' with a production case, "
            "or pass --allow-uncontrolled to explicitly accept an uncontrolled run.")


def cmd_run_execute(args: argparse.Namespace) -> dict[str, Any]:
    _require_uncontrolled(args)
    root, data = _read_project(args.project_dir)
    plan = next((p for p in data["plans"] if p["plan_id"] == args.plan_id), None)
    if plan is None:
        raise CLIError("PLAN_NOT_FOUND", f"Unknown plan: {args.plan_id}")
    if plan.get("dry_run"):
        raise CLIError("DRY_RUN_PLAN", "A dry-run plan cannot be executed; create an executable plan")
    if not data["assets"]:
        raise CLIError("ASSET_REQUIRED", "Project has no audio asset")
    output = Path(args.output_dir).expanduser().absolute()
    if output.exists():
        raise CLIError("OUTPUT_EXISTS", f"Output directory already exists: {output}")
    source = data["assets"][0]
    source_path = Path(source["path"])
    if not source_path.is_file() or _sha256(source_path) != source["sha256"]:
        raise CLIError("SOURCE_HASH_MISMATCH", "Source is missing or its SHA-256 changed", 4)

    from moodify.cli_daw.engine_native import native_render
    from moodify.cli_daw.project import CLIDAWProject, ProcessingNode, RenderSpec, SourceSpec, Track

    nodes = [ProcessingNode(node_id=f"step-{i+1}", type=s["type"], order=i, params=s.get("params", {})) for i, s in enumerate(plan["steps"])]
    daw_project = CLIDAWProject(
        project_id=data["project_id"], tracks=[Track(track_id="source", source=SourceSpec(path=str(source_path), hash=source["sha256"]))],
        processing={"source": nodes}, render=RenderSpec(sample_rate=44100, bit_depth=24),
    )
    evidence = native_render(daw_project, output)
    run_id = str(uuid4())
    run = {
        "run_id": run_id, "plan_id": plan["plan_id"],
        "status": "completed" if evidence.exit_code == 0 else "failed",
        "output_dir": str(output), "evidence_path": str(output / "render_evidence.json"),
        "source_hashes": {source["asset_id"]: source["sha256"]},
        "artifacts": ([{"kind": "audio", "path": evidence.output_path, "sha256": evidence.output_hash}] if evidence.exit_code == 0 else []),
        "errors": evidence.errors,
    }
    data["runs"].append(run)
    _atomic_write(root / PROJECT_FILE, data)
    if evidence.exit_code != 0:
        raise CLIError("RENDER_FAILED", "; ".join(evidence.errors) or "Native render failed", 4)
    return _result("run.execute", "completed", project_id=data["project_id"], run_id=run_id,
                   artifacts=run["artifacts"], evidence_path=run["evidence_path"],
                   **LEGACY_CLASSIFICATION)


def cmd_run_verify(args: argparse.Namespace) -> dict[str, Any]:
    _require_uncontrolled(args)
    root, data = _read_project(args.project_dir)
    run = next((r for r in data["runs"] if r["run_id"] == args.run_id), None)
    if run is None:
        raise CLIError("RUN_NOT_FOUND", f"Unknown run: {args.run_id}")
    from moodify.cli_daw.verify import verify_run
    report = verify_run(Path(run["output_dir"]))
    assets_by_id = {asset["asset_id"]: asset for asset in data["assets"]}
    source_ok = bool(run.get("source_hashes"))
    for asset_id, expected in run.get("source_hashes", {}).items():
        asset = assets_by_id.get(asset_id)
        source_path = Path(asset["path"]) if asset else None
        if asset is None or asset.get("sha256") != expected or not source_path.is_file() or _sha256(source_path) != expected:
            source_ok = False
            break
    if not report.passed or not source_ok:
        raise CLIError("VERIFICATION_FAILED", "; ".join(report.issues) or "Source hash mismatch", 5)
    return _result("run.verify", "verified", project_id=data["project_id"], run_id=run["run_id"],
                   checks={**report.checks, "source_hash_match": source_ok},
                   **LEGACY_CLASSIFICATION)


_RAW_AUDIO_SUFFIXES = {".wav", ".flac", ".aiff", ".aif", ".mp3", ".ogg", ".opus"}


def _case_store(root: Path):
    from moodify.app.production_control import ProductionCaseStore
    return ProductionCaseStore(root / "cases")


def _case_service(root: Path):
    from moodify.app.production_control import ProductionControlService
    from moodify.app.engines import NativeExecutionEngine
    return ProductionControlService(_case_store(root), NativeExecutionEngine())


def cmd_case_create(args: argparse.Namespace) -> dict[str, Any]:
    root, data = _read_project(args.project_dir)
    if not data["assets"]:
        raise CLIError("ASSET_REQUIRED", "Import an audio asset before creating a production case")
    if args.asset_id:
        asset = next((a for a in data["assets"] if a["asset_id"] == args.asset_id), None)
        if asset is None:
            raise CLIError("ASSET_NOT_FOUND", f"Unknown asset: {args.asset_id}")
    else:
        asset = data["assets"][0]
    source_path = Path(asset["path"])
    if not source_path.is_file() or _sha256(source_path) != asset["sha256"]:
        raise CLIError("SOURCE_HASH_MISMATCH", "Source is missing or its SHA-256 changed", 4)
    spec = _parse_intent(args.spec)
    case_id = f"MFY-CASE-{uuid4().hex[:12].upper()}"
    from moodify.app.production_control import ProductionCase
    case = ProductionCase(case_id=case_id)
    case.register_source(str(source_path))
    case.specify(
        spec.get("essence"), spec.get("must_preserve"), spec.get("must_avoid"),
        spec.get("desired_change"), args.owner,
        preservation_acknowledgement=spec.get("preservation_acknowledgement"))
    _case_store(root).save(case)
    return _result("case.create", "created", project_id=data["project_id"], case_id=case_id,
                   state=case.state.value, source_sha256=case.source_sha256,
                   one_point_spec_hash=case.one_point_spec_hash)


def cmd_case_analyze(args: argparse.Namespace) -> dict[str, Any]:
    root, _ = _read_project(args.project_dir)
    store = _case_store(root)
    case = store.load(args.case_id)
    from moodify.app.orchestrator import analyze_audio
    from moodify.app.production_control import default_plan
    analysis = analyze_audio(case.source_path)
    case.analyze({"peak_db": analysis.peak_db, "rms_db": analysis.rms_db,
                  "crest_factor": analysis.crest_factor,
                  "spectral_centroid_hz": analysis.spectral_centroid_hz,
                  "loudness_lufs": analysis.loudness_lufs, "duration_s": analysis.duration_s,
                  "sample_rate": analysis.sample_rate, "has_clipping": analysis.has_clipping,
                  "silence_ratio": analysis.silence_ratio, "warnings": analysis.warnings})
    intent = _parse_intent(args.intent) if getattr(args, "intent", None) else {}
    plan = default_plan(case.analysis, intent)
    case.set_plan(plan, engine_name="native")
    case.run_technical_gate()
    store.save(case)
    return _result("case.analyze", "planned", case_id=case.case_id, state=case.state.value,
                   plan_id=plan["plan_id"], plan_hash=case.plan_hash, steps=plan["steps"])


def cmd_case_approve(args: argparse.Namespace) -> dict[str, Any]:
    root, _ = _read_project(args.project_dir)
    store = _case_store(root)
    case = store.load(args.case_id)
    approval = case.approve(args.owner)
    store.save(case)
    return _result("case.approve", "approved", case_id=case.case_id, state=case.state.value,
                   approval_id=approval.approval_id, plan_hash=case.plan_hash,
                   plan_id=case.plan.get("plan_id", ""))


def cmd_case_status(args: argparse.Namespace) -> dict[str, Any]:
    root, _ = _read_project(args.project_dir)
    case = _case_store(root).load(args.case_id)
    return _result("case.status", "ok", case=case.to_dict())


def cmd_case_execute(args: argparse.Namespace) -> dict[str, Any]:
    root, _ = _read_project(args.project_dir)
    if Path(args.case_id).suffix.lower() in _RAW_AUDIO_SUFFIXES:
        raise CLIError("RAW_AUDIO_NOT_ACCEPTED",
                       "case execute requires a production case_id, not a raw audio path")
    service = _case_service(root)
    try:
        result = service.execute(args.case_id)
    except Exception as exc:
        from moodify.app.production_control import ControlError
        if isinstance(exc, ControlError) and exc.code == "ARTISTIC_APPROVAL_REQUIRED":
            payload = {"ok": False, "case_id": args.case_id,
                       "state": exc.state or "AWAITING_ARTISTIC_APPROVAL",
                       "error_code": "ARTISTIC_APPROVAL_REQUIRED",
                       "errors": [{"field": "artistic_approval",
                                   "message": "Execution requires approval bound to the current plan."}]}
            raise CLIError(exc.code, exc.message, exit_code=2, payload=payload) from exc
        if isinstance(exc, ControlError):
            raise CLIError(exc.code, exc.message) from exc
        raise CLIError("COMMAND_FAILED", str(exc)) from exc
    if not result["ok"]:
        raise CLIError("EXECUTION_FAILED",
                       "; ".join(result["errors"]) or "Engine execution failed",
                       exit_code=4, payload=result)
    return _result("case.execute", "executed", **result)


def cmd_case_verify(args: argparse.Namespace) -> dict[str, Any]:
    root, _ = _read_project(args.project_dir)
    service = _case_service(root)
    try:
        result = service.verify(args.case_id)
        case = service.store.load(args.case_id)
    except Exception as exc:
        from moodify.app.production_control import ControlError
        if isinstance(exc, ControlError):
            raise CLIError(exc.code, exc.message) from exc
        raise CLIError("COMMAND_FAILED", str(exc)) from exc
    doc = {"ok": result.status == "PASS", "case_id": result.case_id,
           "state": case.state.value, "verification_id": result.verification_id,
           "verification_status": result.status, "checks": {
               "output_exists": result.output_exists,
               "output_readable": result.output_readable,
               "source_unchanged": result.source_unchanged,
               "engine_identity_matches": result.engine_identity_matches,
               "plan_identity_matches": result.plan_identity_matches,
               "basic_audio_checks": result.basic_audio_checks}}
    if result.status != "PASS":
        raise CLIError("VERIFICATION_FAILED", f"Verification {result.status}", exit_code=5, payload=doc)
    return _result("case.verify", "verified", **doc)


def cmd_case_package(args: argparse.Namespace) -> dict[str, Any]:
    root, _ = _read_project(args.project_dir)
    service = _case_service(root)
    try:
        result = service.package(args.case_id)
    except Exception as exc:
        from moodify.app.production_control import ControlError
        if isinstance(exc, ControlError):
            raise CLIError(exc.code, exc.message, exit_code=5,
                           payload={"ok": False, "case_id": args.case_id,
                                    "error_code": exc.code,
                                    "errors": [{"field": exc.field, "message": exc.message}]}) from exc
        raise CLIError("COMMAND_FAILED", str(exc)) from exc
    return _result("case.package", "completed", **result)


def _case_evidence_root(root: Path, case_id: str) -> Path:
    """Auditory evidence lives under the authoritative case directory."""
    return root / "cases" / case_id


def cmd_case_scan(args: argparse.Namespace) -> dict[str, Any]:
    from moodify.auditory.profiles import get_profile
    from moodify.auditory.service import scan_audio

    root, _ = _read_project(args.project_dir)
    case_root = _case_evidence_root(root, args.case_id)
    stage = args.stage
    scan_dir = case_root / ("01_before_scan" if stage == "before" else "04_after_scan")

    profile = get_profile(getattr(args, "profile", "MFY-WSE-SCAN-PROFILE-001"))
    out = scan_audio(
        case_id=args.case_id,
        stage=stage,
        input_path=Path(args.input),
        scan_dir=scan_dir,
        profile=profile,
    )
    result_status = "AUDITORY_BEFORE_SCAN_COMPLETED" if stage == "before" else "AUDITORY_AFTER_SCAN_COMPLETED"
    return _result(
        "case.scan", "ok", result_status=result_status, case_id=args.case_id, stage=stage,
        scan_dir=str(scan_dir), profile_hash=out.profile_hash,
        metrics_count=len(out.metrics), timeline_rows=len(out.timeline),
    )


def cmd_case_candidate_register(args: argparse.Namespace) -> dict[str, Any]:
    from moodify.auditory.service import register_candidate

    root, _ = _read_project(args.project_dir)
    case_root = _case_evidence_root(root, args.case_id)
    reg_dir = case_root / "03_processing" / "candidates"
    candidate = register_candidate(
        case_id=args.case_id,
        candidate_id=args.candidate_id,
        source_case_id=args.case_id,
        candidate_path=Path(args.input),
        parent_source_sha256="",
        producing_application=args.application,
        producing_application_version=args.application_version,
        processing_operator=args.operator,
        processing_method=args.method,
        processing_notes=args.notes,
        registry_path=reg_dir,
    )
    return _result(
        "case.candidate.register", "ok", result_status="CANDIDATE_REGISTERED",
        case_id=args.case_id, candidate_id=candidate.candidate_id,
        candidate_sha256=candidate.candidate_sha256,
        registry_dir=str(reg_dir),
    )


def cmd_case_compare(args: argparse.Namespace) -> dict[str, Any]:
    from moodify.auditory.service import (
        compare_scans,
        load_candidate,
        load_scan_evidence,
        verify_candidate_audio,
    )
    from moodify.auditory.profiles import get_profile

    root, _ = _read_project(args.project_dir)
    case_root = _case_evidence_root(root, args.case_id)
    reg_dir = case_root / "03_processing" / "candidates"
    candidate = load_candidate(reg_dir, args.candidate_id)
    verify_candidate_audio(candidate)

    profile = get_profile("MFY-WSE-SCAN-PROFILE-001")
    before_dir = case_root / "01_before_scan"
    after_dir = case_root / "04_after_scan"
    before = load_scan_evidence(before_dir, profile)
    after = load_scan_evidence(after_dir, profile)

    plan = None
    if args.plan:
        plan_path = Path(args.plan)
        if not plan_path.is_file():
            raise CLIError("PLAN_NOT_FOUND", f"processing plan not found: {args.plan}")
        import json
        plan = json.loads(plan_path.read_text(encoding="utf-8"))

    comparison_dir = case_root / "05_comparison"
    result = compare_scans(
        before, after, plan, comparison_dir,
        case_id=args.case_id,
        candidate_id=args.candidate_id,
        source_sha256=candidate.parent_source_sha256 or before.metrics.get("source_sha256", {}).get("value", ""),
        candidate_sha256=candidate.candidate_sha256,
    )
    return _result(
        "case.compare", "ok", result_status="AUDITORY_COMPARISON_COMPLETED",
        case_id=args.case_id, candidate_id=args.candidate_id,
        technical_assessment=result["judgment"].technical_assessment,
        workflow_decision=result["judgment"].workflow_decision,
        comparison_dir=str(comparison_dir),
        report_path=str(result["report_path"]),
    )


def cmd_case_lyrics_align(args: argparse.Namespace) -> dict[str, Any]:
    from moodify.lyric_align.service import run_lyric_alignment

    root, _ = _read_project(args.project_dir)
    case_root = _case_evidence_root(root, args.case_id)
    audio = Path(args.audio)
    lyrics = Path(args.lyrics)
    if not audio.is_file():
        raise CLIError("AUDIO_NOT_FOUND", f"audio file not found: {args.audio}")
    if not lyrics.is_file():
        raise CLIError("LYRICS_NOT_FOUND", f"lyrics file not found: {args.lyrics}")
    translation = Path(args.translation) if args.translation else None
    if translation is not None and not translation.is_file():
        raise CLIError("TRANSLATION_NOT_FOUND", f"translation file not found: {args.translation}")

    manifest = run_lyric_alignment(
        case_id=args.case_id,
        case_root=case_root,
        audio_path=audio,
        lyrics_path=lyrics,
        translation_path=translation,
        language=args.language,
        backend_name=args.backend,
        separate_vocals=args.separate_vocals,
        device=args.device,
        granularity=args.granularity,
    )
    return _result(
        "case.lyrics-align", "ok", result_status="LYRIC_ALIGNMENT_COMPLETED",
        case_id=args.case_id,
        backend=manifest["backend"],
        alignment_status=manifest["status"],
        alignment_sha256=manifest["alignment_sha256"],
        rerun_delta_ms=manifest["rerun_delta_ms"],
        output_dir=str(case_root / "05_lyric_align"),
    )


def cmd_case_observations_add(args: argparse.Namespace) -> dict[str, Any]:
    import json as _json

    from moodify.learning.models import AuditoryObservation
    from moodify.learning.store import CaseLearningStore

    root, _ = _read_project(args.project_dir)
    store = CaseLearningStore(root / "cases" / args.case_id)
    obs = AuditoryObservation.from_dict(_json.loads(Path(args.file).read_text(encoding="utf-8")))
    obs.case_id = args.case_id
    path = store.save_observation(obs)
    return _result("case.observations.add", "ok", result_status="AUDITORY_OBSERVATION_RECORDED",
                   case_id=args.case_id, observation_id=obs.observation_id, path=str(path))


def cmd_case_intervention_register(args: argparse.Namespace) -> dict[str, Any]:
    import json as _json

    from moodify.learning.models import InterventionRecord
    from moodify.learning.store import CaseLearningStore

    root, _ = _read_project(args.project_dir)
    store = CaseLearningStore(root / "cases" / args.case_id)
    rec = InterventionRecord.from_dict(_json.loads(Path(args.file).read_text(encoding="utf-8")))
    rec.case_id = args.case_id
    rec.candidate_id = args.candidate_id
    path = store.save_intervention(rec)
    return _result("case.intervention.register", "ok", result_status="INTERVENTION_RECORDED",
                   case_id=args.case_id, intervention_id=rec.intervention_id, path=str(path))


def cmd_case_listening_evaluate(args: argparse.Namespace) -> dict[str, Any]:
    import json as _json

    from moodify.learning.models import HumanListeningEvaluation
    from moodify.learning.store import CaseLearningStore

    root, _ = _read_project(args.project_dir)
    store = CaseLearningStore(root / "cases" / args.case_id)
    ev = HumanListeningEvaluation.from_dict(_json.loads(Path(args.file).read_text(encoding="utf-8")))
    ev.case_id = args.case_id
    path = store.save_evaluation(ev)
    return _result("case.listening.evaluate", "ok", result_status="HUMAN_LISTENING_EVALUATION_RECORDED",
                   case_id=args.case_id, evaluation_id=ev.evaluation_id,
                   approval_status=ev.approval_status, path=str(path))


def cmd_case_learning_build(args: argparse.Namespace) -> dict[str, Any]:
    from moodify.learning.service import build_learning_record
    from moodify.learning.store import CaseLearningStore

    root, _ = _read_project(args.project_dir)
    store = CaseLearningStore(root / "cases" / args.case_id)
    record = build_learning_record(store, args.case_id)
    return _result("case.learning.build", "ok", result_status="LEARNING_RECORD_BUILT",
                   case_id=args.case_id, learning_record_id=record.learning_record_id,
                   learning_status=record.learning_status,
                   eligibility=record.training_eligibility)


def cmd_case_learning_review(args: argparse.Namespace) -> dict[str, Any]:
    import json as _json

    from moodify.learning.models import RightsMetadata
    from moodify.learning.service import review_learning_record
    from moodify.learning.store import CaseLearningStore

    root, _ = _read_project(args.project_dir)
    store = CaseLearningStore(root / "cases" / args.case_id)
    rights = RightsMetadata.from_dict(_json.loads(Path(args.rights).read_text(encoding="utf-8")))
    record = review_learning_record(store, args.case_id, rights, eligibility=args.eligibility)
    return _result("case.learning.review", "ok", result_status="LEARNING_RECORD_REVIEWED",
                   case_id=args.case_id, eligibility=record.training_eligibility,
                   review_status=record.review_status)


def cmd_case_learning_commit(args: argparse.Namespace) -> dict[str, Any]:
    from moodify.learning.service import commit_learning_record
    from moodify.learning.store import CaseLearningStore

    root, _ = _read_project(args.project_dir)
    store = CaseLearningStore(root / "cases" / args.case_id)
    record = commit_learning_record(store, args.case_id, args.by)
    status = ("LEARNING_RECORD_COMMITTED" if record.learning_status == "COMMITTED"
              else "LEARNING_RECORD_EXCLUDED")
    return _result("case.learning.commit", "ok", result_status=status,
                   case_id=args.case_id, learning_status=record.learning_status,
                   eligibility=record.training_eligibility,
                   exclusion_reasons=record.exclusion_reasons)


def cmd_learning_dataset_export(args: argparse.Namespace) -> dict[str, Any]:

    from moodify.learning.exports import export_learning_records, validate_export_bundle
    from moodify.learning.store import CaseLearningStore

    root, _ = _read_project(args.project_dir)
    records = []
    cases_dir = root / "cases"
    if cases_dir.is_dir():
        for case_dir in sorted(cases_dir.iterdir()):
            if not case_dir.is_dir():
                continue
            store = CaseLearningStore(case_dir)
            rec = store.load_learning_record()
            if rec is not None:
                records.append(rec)
    manifest = export_learning_records(records, Path(args.output), args.dataset_id)
    problems = validate_export_bundle(Path(args.output), args.dataset_id)
    if problems:
        raise CLIError("EXPORT_VERIFICATION_FAILED", "; ".join(problems))
    return _result("learning.dataset.export", "ok", result_status="DATASET_EXPORT_COMPLETED",
                   dataset_id=args.dataset_id, included=manifest["included_count"],
                   excluded=manifest["excluded_count"],
                   manifest_path=str(Path(args.output) / f"{args.dataset_id}_manifest.json"))


def cmd_architecture_inventory(args: argparse.Namespace) -> dict[str, Any]:
    from moodify.auditory.inventory import build_inventory
    from moodify.auditory.inventory import render_markdown as _render_md
    from pathlib import Path as _P

    package_dir = _P(__file__).resolve().parent.parent
    inv = build_inventory(package_dir)
    if args.format == "json":
        return _result("architecture.inventory", "ok", result_status="INVENTORY_COMPLETED",
                       counts=inv["counts"], capabilities=inv["capabilities"])
    print(_render_md(inv))
    return _result("architecture.inventory", "ok", result_status="INVENTORY_COMPLETED",
                   counts=inv["counts"])


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="moodify", description="Moodify AI-native CLI")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("version")
    sub.add_parser("capabilities")
    project = sub.add_parser("project").add_subparsers(dest="project_command", required=True)
    init = project.add_parser("init"); init.add_argument("project_dir"); init.add_argument("--title")
    project.add_parser("inspect").add_argument("project_dir")
    asset = sub.add_parser("asset").add_subparsers(dest="asset_command", required=True)
    imp = asset.add_parser("import"); imp.add_argument("project_dir"); imp.add_argument("input_path"); imp.add_argument("--copy-mode", default="reference")
    plan = sub.add_parser("plan").add_subparsers(dest="plan_command", required=True)
    create = plan.add_parser("create"); create.add_argument("project_dir"); create.add_argument("--intent", default="{}"); create.add_argument("--dry-run", action="store_true")
    run = sub.add_parser("run").add_subparsers(dest="run_command", required=True)
    execute = run.add_parser("execute"); execute.add_argument("project_dir"); execute.add_argument("--plan-id", required=True); execute.add_argument("--output-dir", required=True); execute.add_argument("--allow-uncontrolled", action="store_true")
    verify = run.add_parser("verify"); verify.add_argument("project_dir"); verify.add_argument("--run-id", required=True); verify.add_argument("--allow-uncontrolled", action="store_true")
    case = sub.add_parser("case").add_subparsers(dest="case_command", required=True)
    create = case.add_parser("create"); create.add_argument("project_dir"); create.add_argument("--spec", required=True); create.add_argument("--owner", required=True); create.add_argument("--asset-id")
    analyze = case.add_parser("analyze"); analyze.add_argument("project_dir"); analyze.add_argument("case_id"); analyze.add_argument("--intent", default=None)
    approve = case.add_parser("approve"); approve.add_argument("project_dir"); approve.add_argument("case_id"); approve.add_argument("--owner", required=True)
    status = case.add_parser("status"); status.add_argument("project_dir"); status.add_argument("case_id")
    cexecute = case.add_parser("execute"); cexecute.add_argument("project_dir"); cexecute.add_argument("case_id")
    cverify = case.add_parser("verify"); cverify.add_argument("project_dir"); cverify.add_argument("case_id")
    cpackage = case.add_parser("package"); cpackage.add_argument("project_dir"); cpackage.add_argument("case_id")
    cscan = case.add_parser("scan")
    cscan.add_argument("project_dir"); cscan.add_argument("case_id")
    cscan.add_argument("--stage", required=True, choices=["before", "after"])
    cscan.add_argument("--input", required=True, help="音频文件路径")
    cscan.add_argument("--candidate-id", default=None, help="after 阶段必填")
    cscan.add_argument("--profile", default="MFY-WSE-SCAN-PROFILE-001")
    ccand = case.add_parser("candidate").add_subparsers(dest="candidate_command", required=True)
    creg = ccand.add_parser("register")
    creg.add_argument("project_dir"); creg.add_argument("case_id")
    creg.add_argument("--candidate-id", required=True)
    creg.add_argument("--input", required=True)
    creg.add_argument("--application", default="Audacity")
    creg.add_argument("--application-version", default=None)
    creg.add_argument("--operator", default="")
    creg.add_argument("--method", default="EXTERNAL_GUI_PROCESSING")
    creg.add_argument("--notes", default="")
    ccomp = case.add_parser("compare")
    ccomp.add_argument("project_dir"); ccomp.add_argument("case_id")
    ccomp.add_argument("--candidate-id", required=True)
    ccomp.add_argument("--plan", default=None, help="processing_plan.json 路径")
    cla = case.add_parser("lyrics-align")
    cla.add_argument("project_dir"); cla.add_argument("case_id")
    cla.add_argument("--audio", required=True, help="最终音频文件路径（时间权威）")
    cla.add_argument("--lyrics", required=True, help="权威歌词文本文件路径（文字权威）")
    cla.add_argument("--language", required=True, help="歌词语言代码（fr/zh/en 等）")
    cla.add_argument("--translation", default=None, help="可选翻译歌词文件路径（行数须与歌词一致）")
    cla.add_argument("--backend", default="heuristic", choices=["heuristic", "whisperx"])
    cla.add_argument("--separate-vocals", default="auto", choices=["never", "auto", "always"])
    cla.add_argument("--device", default="cpu")
    cla.add_argument("--granularity", default=None, choices=["line", "word"], help="请求粒度（默认行+词均输出）")

    # learning-domain commands (AIR-001)
    cobs = case.add_parser("observations").add_subparsers(dest="observations_command", required=True)
    p_obs_add = cobs.add_parser("add")
    p_obs_add.add_argument("project_dir"); p_obs_add.add_argument("case_id")
    p_obs_add.add_argument("--file", required=True, help="observation.json 路径")
    cinterv = case.add_parser("intervention").add_subparsers(dest="intervention_command", required=True)
    p_int_reg = cinterv.add_parser("register")
    p_int_reg.add_argument("project_dir"); p_int_reg.add_argument("case_id")
    p_int_reg.add_argument("--candidate-id", required=True)
    p_int_reg.add_argument("--file", required=True, help="intervention_record.json 路径")
    clist = case.add_parser("listening").add_subparsers(dest="listening_command", required=True)
    p_ev = clist.add_parser("evaluate")
    p_ev.add_argument("project_dir"); p_ev.add_argument("case_id")
    p_ev.add_argument("--file", required=True, help="human_listening_evaluation.json 路径")
    clearn = case.add_parser("learning").add_subparsers(dest="learning_command", required=True)
    p_build = clearn.add_parser("build")
    p_build.add_argument("project_dir"); p_build.add_argument("case_id")
    p_review = clearn.add_parser("review")
    p_review.add_argument("project_dir"); p_review.add_argument("case_id")
    p_review.add_argument("--rights", required=True, help="rights_review.json 路径")
    p_review.add_argument("--eligibility", default=None,
                          choices=["ELIGIBLE", "INELIGIBLE", "PENDING_REVIEW",
                                   "RESTRICTED_INTERNAL_RESEARCH", "UNKNOWN"])
    p_commit = clearn.add_parser("commit")
    p_commit.add_argument("project_dir"); p_commit.add_argument("case_id")
    p_commit.add_argument("--by", required=True, help="committer id")

    # learning dataset export + architecture inventory (top-level)
    p_learning = sub.add_parser("learning").add_subparsers(dest="learning_command", required=True)
    p_ds = p_learning.add_parser("dataset").add_subparsers(dest="dataset_command", required=True)
    p_exp = p_ds.add_parser("export")
    p_exp.add_argument("--dataset-id", required=True)
    p_exp.add_argument("--project-dir", required=True)
    p_exp.add_argument("--output", required=True)
    p_inv = sub.add_parser("architecture").add_subparsers(dest="architecture_command", required=True)
    p_inv_list = p_inv.add_parser("inventory")
    p_inv_list.add_argument("--format", default="md", choices=["md", "json"])
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    # Machine-readable output is UTF-8 on Windows as well as POSIX, including
    # when stdout/stderr are redirected by an agent or batch runner.
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if reconfigure is not None:
            reconfigure(encoding="utf-8")
    args = build_parser().parse_args(argv)
    key = args.command
    if key in {"project", "asset", "plan", "run", "case"}:
        key = f"{key}.{getattr(args, key + '_command')}"
    if key in {"case.candidate", "case.observations", "case.intervention", "case.listening", "case.learning"}:
        sub_cmd = key.split(".")[-1] + "_command"
        key = f"{key}.{getattr(args, sub_cmd)}"
    if key == "learning.dataset":
        key = f"{key}.{getattr(args, 'dataset_command')}"
    if key == "architecture":
        key = f"{key}.{getattr(args, 'architecture_command')}"
    handlers = {
        "version": cmd_version, "capabilities": cmd_capabilities,
        "project.init": cmd_project_init, "project.inspect": cmd_project_inspect,
        "asset.import": cmd_asset_import, "plan.create": cmd_plan_create,
        "run.execute": cmd_run_execute, "run.verify": cmd_run_verify,
        "case.create": cmd_case_create, "case.analyze": cmd_case_analyze,
        "case.approve": cmd_case_approve, "case.status": cmd_case_status,
        "case.execute": cmd_case_execute, "case.verify": cmd_case_verify,
        "case.package": cmd_case_package,
        "case.scan": cmd_case_scan,
        "case.candidate.register": cmd_case_candidate_register,
        "case.compare": cmd_case_compare,
        "case.lyrics-align": cmd_case_lyrics_align,
        "case.observations.add": cmd_case_observations_add,
        "case.intervention.register": cmd_case_intervention_register,
        "case.listening.evaluate": cmd_case_listening_evaluate,
        "case.learning.build": cmd_case_learning_build,
        "case.learning.review": cmd_case_learning_review,
        "case.learning.commit": cmd_case_learning_commit,
        "learning.dataset.export": cmd_learning_dataset_export,
        "architecture.inventory": cmd_architecture_inventory,
    }
    try:
        payload = handlers[key](args)
    except CLIError as exc:
        doc = exc.payload or _result(key, "error", errors=[{"code": exc.code, "message": exc.message}])
        _emit(doc, error=True)
        return exc.exit_code
    except Exception as exc:
        from moodify.app.production_control import ControlError
        if isinstance(exc, ControlError):
            _emit(_result(key, "error", errors=[{"code": exc.code, "message": exc.message, "field": exc.field}]),
                  error=True)
            return 2
        raise
    except (OSError, ValueError) as exc:
        _emit(_result(key, "error", errors=[{"code": "COMMAND_FAILED", "message": str(exc)}]), error=True)
        return 3
    _emit(payload)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
