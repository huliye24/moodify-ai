from __future__ import annotations

import html
import json
import logging
from pathlib import Path
from typing import Any, cast
from uuid import UUID

logger = logging.getLogger(__name__)

import numpy as np
import pyarrow as pa
import pyarrow.parquet as pq

from .hashing import sha256_bytes, sha256_file
from .metrics import (
    MetricOutput,
    band_fractions,
    left_right_correlation,
    level_metrics,
    loudness_metrics,
    spectral_metrics,
)
from .schemas import (
    CommandResult,
    EnvironmentInfo,
    EvidencePacket,
    GateResult,
    GateStatus,
    HumanApproval,
    LyricsEvidence,
    LyricsRights,
    LyricsSection,
    LyricsSourceFacts,
    LyricsStructuralObservations,
    MoodifyRule,
    OnePointResult,
    OnePointSpec,
    OnePointStatus,
    PPEFinalStatus,
    ProductionCase,
    RepeatedLine,
    RuleState,
    RunManifest,
    ValidationResult,
)
from .serialization import canonical_json, read_model, write_yaml
from .store import LedgerStore


def validate_case(case: ProductionCase) -> ValidationResult:
    errors: list[str] = []
    warnings: list[str] = []
    for asset in case.assets:
        path = Path(asset.local_path)
        if not path.exists():
            warnings.append(f"asset unavailable locally: {asset.local_path}")
        elif sha256_file(path) != asset.sha256:
            errors.append(f"asset hash mismatch: {asset.local_path}")
    kinds = {asset.kind.value for asset in case.assets}
    for kind in ("stem", "midi", "score", "lyrics"):
        if kind not in kinds:
            warnings.append(f"no {kind} asset recorded; absence is explicit")
    return ValidationResult(subject_type="case", subject_id=str(case.case_id), valid=not errors,
                            checks={"asset_identities": not errors, "source_identity": bool(case.source_asset_ids),
                                    "output_identity": bool(case.output_asset_ids)},
                            warnings=tuple(warnings), errors=tuple(errors))


def write_metric_parquet(path: Path, output: MetricOutput) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    rows = [{"metric": name, "value": value, "unit": output.units.get(name), "warning": "; ".join(output.warnings) or None}
            for name, value in sorted(output.values.items())]
    pq.write_table(pa.Table.from_pylist(rows), path, compression="zstd")


def load_audio(path: Path) -> tuple[np.ndarray[Any, np.dtype[np.float64]], int]:
    try:
        import soundfile as sf  # type: ignore[import-not-found]
    except ImportError as exc:
        raise RuntimeError("Audio measurement requires the 'audio' extra: pip install -e '.[audio]'") from exc
    data, rate = sf.read(path, always_2d=False, dtype="float64")
    return np.asarray(data, dtype=np.float64), int(rate)


def measure_all(samples: np.ndarray[Any, np.dtype[np.float64]], sample_rate: int) -> dict[str, MetricOutput]:
    return {"levels": level_metrics(samples), "loudness": loudness_metrics(samples, sample_rate),
            "spectral": spectral_metrics(samples, sample_rate), "bands": band_fractions(samples, sample_rate),
            "stereo": left_right_correlation(samples)}


def compile_evidence(store: LedgerStore, case_id: UUID) -> EvidencePacket:
    case = store.get_case(case_id)
    measurements = store.measurements(case_id)
    warnings = list(validate_case(case).warnings)
    if not measurements:
        warnings.append("no measurements recorded; measurement values remain absent")
    return EvidencePacket(case_id=case_id, case_digest=sha256_bytes(canonical_json(case).encode()),
                          measurement_ids=tuple(item.measurement_id for item in measurements),
                          observation_ids=tuple(item.observation_id for item in case.human_observations),
                          warnings=tuple(warnings))


TRANSITIONS: dict[RuleState, set[RuleState]] = {
    RuleState.PROPOSED: {RuleState.EXPERIMENTAL, RuleState.DEPRECATED},
    RuleState.EXPERIMENTAL: {RuleState.VALIDATED, RuleState.DEPRECATED},
    RuleState.VALIDATED: {RuleState.PRODUCTION, RuleState.DEPRECATED},
    RuleState.PRODUCTION: {RuleState.DEPRECATED}, RuleState.DEPRECATED: set(),
}


def promote_rule(store: LedgerStore, path: Path, target: RuleState) -> MoodifyRule:
    rule = read_model(path, MoodifyRule)
    if target not in TRANSITIONS[rule.state]:
        raise ValueError(f"Invalid rule transition: {rule.state.value} -> {target.value}")
    approval = store.approval(rule.rule_id, rule.version)
    if approval is None:
        raise PermissionError("Rule promotion requires an explicit human approval record")
    promoted = rule.model_copy(update={"state": target})
    write_yaml(path, promoted)
    return promoted


def _write_rule_file(path: Path, rule: MoodifyRule) -> None:
    """Write a rule to a file. Inject point for failure tests."""
    write_yaml(path, rule)


def _replace_file(src: Path, dst: Path) -> None:
    """Atomically replace dst with src. Inject point for failure tests."""
    import os
    os.replace(src, dst)


PROMOTION_MARKER_SUFFIX = ".promoting"


def _read_promotion_marker(marker_path: Path) -> dict[str, str] | None:
    import json as _json
    if not marker_path.exists():
        return None
    try:
        return cast(dict[str, str], _json.loads(marker_path.read_text(encoding="utf-8")))
    except Exception:  # noqa: BLE001
        return None


def _write_promotion_marker(marker_path: Path, rule_path: str, temp_path: str,
                            target: str, approval_id: str) -> None:
    import json as _json
    from datetime import UTC, datetime
    marker_path.write_text(_json.dumps({
        "rule_path": rule_path, "temp_path": temp_path, "target": target,
        "approval_id": approval_id, "started_at": datetime.now(UTC).isoformat(),
    }), encoding="utf-8")


def _cleanup_promotion_marker(marker_path: Path) -> None:
    try:
        marker_path.unlink(missing_ok=True)
    except OSError as exc:
        # Marker cleanup failure is non-fatal, but must stay visible so the
        # next promotion attempt can detect the stale marker.
        logger.warning("promotion marker cleanup failed: %s: %s", marker_path, exc)


def promote_rule_atomic(store: LedgerStore, path: Path, target: RuleState,
                        approval_record: HumanApproval) -> MoodifyRule:
    """Promote a rule with atomic file replace and transaction marker.

    Protocol:
    0. Detect and recover from any stale .promoting marker.
    1. Validate all preconditions (no side effects yet).
    2. Write promoted rule to a temp file.
    3. Write a .promoting marker.
    4. Add approval record to DB.
    5. Atomically replace the rule file (os.replace).
    6. Clean up the .promoting marker and temp file.

    If a stale .promoting marker exists, attempt recovery:
    If the temp file still exists and the approval is in DB, complete the rename.
    Otherwise, clean up the stale marker.

    Any failure before step 4 leaves zero DB side effects (temp + marker cleaned).
    A failure at step 5 leaves the approval in DB and a marker for retry-recovery.
    """
    import os
    import tempfile


    # ── Step 0: check for stale marker ──
    marker_path = path.with_suffix(path.suffix + PROMOTION_MARKER_SUFFIX)
    stale = _read_promotion_marker(marker_path)
    if stale is not None:
        stale_temp = Path(stale.get("temp_path", ""))
        stale_rule_path = stale.get("rule_path", "")
        stale_rule_id = stale.get("rule_id", "")
        stale_rule_version = stale.get("rule_version", "")
        marker_matches_request = (
            stale_rule_path
            and Path(stale_rule_path).resolve() == path.resolve()
            and stale.get("target") == target.value
            and stale.get("approval_id") == str(approval_record.approval_id)
            and stale_rule_id == approval_record.rule_id
            and stale_rule_version == approval_record.rule_version
        )
        if not marker_matches_request:
            raise RuntimeError(
                f"Stale promotion marker does not match this request: {marker_path}. "
                "Manual review is required; no recovery files were removed."
            )

        approval_in_db = store.approval(stale_rule_id, stale_rule_version)
        if approval_in_db is not None:
            if approval_in_db.approval_id != approval_record.approval_id:
                raise RuntimeError(
                    "A different approval exists for the pending promotion. "
                    "Manual review is required; no recovery files were removed."
                )
            if not stale_temp.exists():
                raise RuntimeError(
                    f"Pending promotion approval exists but recovery file is missing: {stale_temp}. "
                    "Manual repair is required."
                )
            try:
                _replace_file(stale_temp, path)
            except OSError as exc:
                raise RuntimeError(
                    f"Pending promotion could not be recovered. Temp file {stale_temp} and "
                    f"marker {marker_path} were preserved."
                ) from exc
            _cleanup_promotion_marker(marker_path)
            stale_temp.unlink(missing_ok=True)
            recovered = read_model(path, MoodifyRule)
            if recovered.state is not target:
                raise RuntimeError("Recovered rule state does not match the requested target.")
            return recovered

        # No database write occurred, so abandoning the prepared temp file is safe.
        stale_temp.unlink(missing_ok=True)
        _cleanup_promotion_marker(marker_path)

    # ── Step 1: validate preconditions ──
    rule = read_model(path, MoodifyRule)
    if target not in TRANSITIONS[rule.state]:
        raise ValueError(f"Invalid rule transition: {rule.state.value} -> {target.value}")
    # Verify the provided approval matches
    if (approval_record.rule_id, approval_record.rule_version) != (rule.rule_id, rule.version):
        raise ValueError(
            f"Approval ({approval_record.rule_id}@{approval_record.rule_version}) "
            f"does not match rule ({rule.rule_id}@{rule.version})."
        )

    # ── Step 2: write to temp file ──
    promoted = rule.model_copy(update={"state": target})
    tmp_fd, tmp_name = tempfile.mkstemp(
        suffix=".yaml", prefix="promoting_", dir=path.parent,
    )
    os.close(tmp_fd)
    temp_path = Path(tmp_name)
    try:
        _write_rule_file(temp_path, promoted)
    except Exception:
        temp_path.unlink(missing_ok=True)
        raise

    # ── Step 3: write marker ──
    try:
        marker_data = {
            "rule_path": str(path.resolve()), "temp_path": str(temp_path.resolve()),
            "target": target.value, "approval_id": str(approval_record.approval_id),
            "rule_id": rule.rule_id, "rule_version": rule.version,
        }
        import json as _json
        from datetime import UTC, datetime
        marker_data["started_at"] = datetime.now(UTC).isoformat()
        marker_path.write_text(_json.dumps(marker_data), encoding="utf-8")
    except Exception:
        temp_path.unlink(missing_ok=True)
        raise

    # ── Step 4: add approval to DB ──
    try:
        store.add_approval(approval_record)
    except Exception:
        temp_path.unlink(missing_ok=True)
        _cleanup_promotion_marker(marker_path)
        raise

    # ── Step 5: atomically replace the rule file ──
    try:
        _replace_file(temp_path, path)
    except Exception:  # noqa: BLE001
        raise RuntimeError(
            f"Rule file replace failed. Approval is in DB, temp file at {temp_path}, "
            f"marker at {marker_path}. Re-run the promotion to complete recovery."
        )

    # ── Step 6: cleanup ──
    _cleanup_promotion_marker(marker_path)
    temp_path.unlink(missing_ok=True)
    return promoted


def validate_rule(store: LedgerStore, rule: MoodifyRule) -> ValidationResult:
    approval = store.approval(rule.rule_id, rule.version)
    needs_approval = rule.state in {RuleState.VALIDATED, RuleState.PRODUCTION}
    approval_present = approval is not None
    check_passed = not needs_approval or approval_present
    errors: tuple[str, ...] = ()
    if needs_approval and not approval_present:
        errors = (f"rule in {rule.state.value} state lacks human approval",)
    if not needs_approval and approval_present:
        pass  # approval present but not required — not an error, but notable
    return ValidationResult(
        subject_type="rule", subject_id=f"{rule.rule_id}@{rule.version}", valid=not errors,
        checks={"approval_required": needs_approval, "approval_present": approval_present,
                "approval_gate_satisfied": check_passed},
        errors=errors,
        approval_id=None if approval is None else approval.approval_id,
    )


def regression(store: LedgerStore, case_id: UUID, replay_case_path: Path) -> ValidationResult:
    archived = store.get_case(case_id)
    replay = read_model(replay_case_path, ProductionCase)
    checks = {"same_case_id": archived.case_id == replay.case_id,
              "same_sources": archived.source_asset_ids == replay.source_asset_ids,
              "same_outputs": archived.output_asset_ids == replay.output_asset_ids,
              "same_canonical_record": canonical_json(archived) == canonical_json(replay)}
    return ValidationResult(subject_type="regression", subject_id=str(case_id), valid=all(checks.values()), checks=checks)


def build_report(store: LedgerStore, case_id: UUID, output: Path) -> tuple[Path, Path]:
    case, measurements = store.get_case(case_id), store.measurements(case_id)
    validation = validate_case(case)
    lines = [f"# Case: {case.title}", "", f"- Case ID: `{case.case_id}`", f"- Moodify version: `{case.moodify_version}`",
             f"- Golden case: `{str(case.golden).lower()}`", f"- Created: `{case.created_at.isoformat()}`", "", "## Assets", ""]
    lines += [f"- **{a.role}** ({a.kind.value}): `{a.local_path}` — `{a.sha256}`" for a in case.assets]
    lines += ["", "## Processing stages", ""] + [f"- {s.ordinal}. **{s.name}** — {s.software} {s.software_version}; parameters `{json.dumps(s.parameters, sort_keys=True)}`" for s in case.processing_stages]
    lines += ["", "## Measurements", ""]
    if measurements:
        lines += [f"- **{m.adapter}**: `{json.dumps(m.values, sort_keys=True)}`" for m in measurements]
    else:
        lines.append("- No measurements recorded. Values are absent, not inferred.")
    lines += ["", "## Human observations", ""] + ([f"- {o.observer}: {o.text}" for o in case.human_observations] or ["- None recorded."])
    lines += ["", "## Failures, rollbacks, and limitations", ""] + ([f"- **{e.event_type}**: {e.description}" for e in case.events] or ["- No events recorded."])
    lines += [f"- Limitation: {item}" for item in case.limitations]
    lines += ["", "## Validation warnings", ""] + ([f"- {w}" for w in validation.warnings] or ["- None."])
    markdown = "\n".join(lines) + "\n"
    md_path = output.with_suffix(".md")
    html_path = output.with_suffix(".html")
    md_path.parent.mkdir(parents=True, exist_ok=True)
    md_path.write_text(markdown, encoding="utf-8")
    html_body = "\n".join(f"<p>{html.escape(line)}</p>" if line else "" for line in lines)
    html_path.write_text(f"<!doctype html><html><head><meta charset='utf-8'><title>{html.escape(case.title)}</title><style>body{{font:16px system-ui;max-width:900px;margin:3rem auto;line-height:1.5}}code{{background:#eee;padding:.1rem .25rem}}</style></head><body>{html_body}</body></html>", encoding="utf-8")
    return md_path, html_path


# ── PPE Gates & Unified Runner (DSK-MFY-PPE-HARDENING-005) ──────────────


def evaluate_gates(
    case: ProductionCase,
    validation: ValidationResult,
    evidence: EvidencePacket,
    report_md: Path | None = None,
    report_html: Path | None = None,
) -> list[GateResult]:
    assets_exist = all(Path(a.local_path).exists() for a in case.assets)
    assets_match = len(validation.errors) == 0
    has_measurements = len(evidence.measurement_ids) > 0
    has_candidates = len(case.processing_stages) > 1 or len(case.output_asset_ids) > 1
    # Synthetic demo case: no promotion, no human approval needed
    has_approval_request = False

    gates: list[GateResult] = []

    gates.append(GateResult(
        gate_id="input_complete",
        status=GateStatus.PASS if assets_exist else GateStatus.FAIL,
        blocking=True,
        reason_code="all_inputs_present" if assets_exist else "input_file_missing",
        message="All declared assets are present on disk." if assets_exist
        else "One or more declared assets are missing from disk.",
    ))

    gates.append(GateResult(
        gate_id="identity_consistent",
        status=GateStatus.PASS if assets_match else GateStatus.FAIL,
        blocking=True,
        reason_code="hashes_match" if assets_match else "hash_mismatch",
        message="All asset SHA-256 hashes match the ledger." if assets_match
        else "One or more asset hash mismatches detected.",
        evidence_paths=tuple(validation.errors) if not assets_match else (),
    ))

    gates.append(GateResult(
        gate_id="measurement_available",
        status=GateStatus.WARN if not has_measurements else GateStatus.PASS,
        blocking=False,
        reason_code="no_measurements_recorded" if not has_measurements else "measurements_present",
        message="No measurement records; values remain absent." if not has_measurements
        else "Measurements are recorded.",
    ))

    gates.append(GateResult(
        gate_id="candidates_comparable",
        status=GateStatus.WARN if not has_candidates else GateStatus.PASS,
        blocking=False,
        reason_code="single_output" if not has_candidates else "candidates_present",
        message="No candidate comparison is possible with a single output." if not has_candidates
        else "Multiple candidates are available for comparison.",
    ))

    gates.append(GateResult(
        gate_id="human_approved",
        status=GateStatus.WARN if not has_approval_request else GateStatus.PASS,
        blocking=False,
        reason_code="not_applicable" if not has_approval_request else "approval_present",
        message="No rule promotion was requested; human approval is not applicable."
        if not has_approval_request
        else "Human approval is present.",
    ))

    report_ok = report_md is not None and report_md.exists() and report_html is not None and report_html.exists()
    gates.append(GateResult(
        gate_id="report_complete",
        status=GateStatus.PASS if report_ok else GateStatus.FAIL,
        blocking=True,
        reason_code="report_generated" if report_ok else "report_missing",
        message="Reports generated successfully." if report_ok
        else "Report artifacts are missing.",
    ))

    return gates


def determine_final_status(gates: list[GateResult]) -> PPEFinalStatus:
    if not gates:
        return PPEFinalStatus.FAIL
    has_blocking_fail = any(g.status == GateStatus.FAIL and g.blocking for g in gates)
    if has_blocking_fail:
        return PPEFinalStatus.FAIL
    has_warnings = any(g.status == GateStatus.WARN for g in gates)
    return PPEFinalStatus.PASS_WITH_WARNINGS if has_warnings else PPEFinalStatus.PASS


def _collect_environment() -> EnvironmentInfo:
    import platform
    import sys

    packages: dict[str, str] = {}
    import_map = {
        "duckdb": "duckdb", "numpy": "numpy", "pyarrow": "pyarrow",
        "pydantic": "pydantic", "PyYAML": "yaml", "typer": "typer",
    }
    for display_name, import_name in import_map.items():
        try:
            mod = __import__(import_name)
            packages[display_name] = getattr(mod, "__version__", "unknown")
        except Exception:  # noqa: BLE001
            packages[display_name] = "absent"
    return EnvironmentInfo(
        python_version=sys.version,
        python_executable=sys.executable,
        platform=platform.platform(),
        packages=packages,
    )


def ppe_run(case_path: Path, output_dir: Path) -> RunManifest:
    """Execute the full PPE baseline pipeline in a single run."""
    from datetime import UTC, datetime

    output_dir.mkdir(parents=True, exist_ok=True)  # existence checked in CLI

    started_at = datetime.now(UTC)
    env = _collect_environment()
    commands: list[CommandResult] = []
    case_id: UUID | None = None
    case: ProductionCase | None = None
    evidence_path: Path | None = None
    report_md: Path | None = None
    report_html: Path | None = None

    # --- Step 1: case create ---
    cmd_start = datetime.now(UTC)
    try:
        ledger_root = output_dir / "ledger"
        case = read_model(case_path, ProductionCase)
        db = LedgerStore(ledger_root)
        db.create_case(case)
        case_id = case.case_id
        commands.append(CommandResult(
            action="case_create", started_at=cmd_start, exit_code=0,
            status=GateStatus.PASS,
        ))
    except Exception as exc:  # noqa: BLE001
        commands.append(CommandResult(
            action="case_create", started_at=cmd_start, exit_code=1,
            status=GateStatus.FAIL, error_code="CASE_CREATE_FAILED",
            error_message=str(exc),
        ))
        return _build_manifest(
            output_dir, case_path, started_at, env, commands, [], case_id,
            None, None, None,
        )

    # --- Step 2: case validate ---
    cmd_start = datetime.now(UTC)
    try:
        validation = validate_case(case)
        db.add_validation(validation)
        if validation.valid:
            commands.append(CommandResult(
                action="case_validate", started_at=cmd_start, exit_code=0,
                status=GateStatus.PASS,
            ))
        else:
            commands.append(CommandResult(
                action="case_validate", started_at=cmd_start, exit_code=1,
                status=GateStatus.FAIL, error_code="VALIDATION_FAILED",
                error_message="; ".join(validation.errors),
            ))
            gates = evaluate_gates(case, validation, EvidencePacket(
                case_id=case.case_id, case_digest="0" * 64,
            ))
            return _build_manifest(
                output_dir, case_path, started_at, env, commands, gates, case_id,
                None, None, None, str(case.case_id),
            )
    except Exception as exc:  # noqa: BLE001
        commands.append(CommandResult(
            action="case_validate", started_at=cmd_start, exit_code=1,
            status=GateStatus.FAIL, error_code="VALIDATE_ERROR", error_message=str(exc),
        ))
        empty_evidence = EvidencePacket(case_id=case.case_id, case_digest="0" * 64)
        gates = evaluate_gates(case, ValidationResult(
            subject_type="case", subject_id=str(case.case_id), valid=False,
            checks={}, errors=(str(exc),),
        ), empty_evidence)
        return _build_manifest(
            output_dir, case_path, started_at, env, commands, gates, case_id,
            None, None, None, str(case.case_id),
        )

    # --- Step 3: assets hash ---
    cmd_start = datetime.now(UTC)
    try:
        for asset in case.assets:
            path = Path(asset.local_path)
            if path.exists():
                computed = sha256_file(path)
                if computed != asset.sha256:
                    raise ValueError(f"Hash mismatch for {asset.local_path}")
        commands.append(CommandResult(
            action="assets_hash", started_at=cmd_start, exit_code=0,
            status=GateStatus.PASS,
        ))
    except Exception as exc:  # noqa: BLE001
        commands.append(CommandResult(
            action="assets_hash", started_at=cmd_start, exit_code=1,
            status=GateStatus.FAIL, error_code="HASH_ERROR", error_message=str(exc),
        ))

    # --- Step 4: evidence compile ---
    cmd_start = datetime.now(UTC)
    try:
        evidence = compile_evidence(db, case.case_id)
        evidence_path = output_dir / "evidence.yaml"
        write_yaml(evidence_path, evidence)
        commands.append(CommandResult(
            action="evidence_compile", started_at=cmd_start, exit_code=0,
            status=GateStatus.PASS, artifact_paths=(str(evidence_path),),
        ))
    except Exception as exc:  # noqa: BLE001
        commands.append(CommandResult(
            action="evidence_compile", started_at=cmd_start, exit_code=1,
            status=GateStatus.FAIL, error_code="EVIDENCE_ERROR",
            error_message=str(exc),
        ))
        evidence = EvidencePacket(case_id=case.case_id, case_digest="0" * 64,
                                  warnings=(f"evidence compile failed: {exc}",))

    # --- Step 5: build reports ---
    cmd_start = datetime.now(UTC)
    try:
        report_dir = output_dir / "reports"
        report_base = report_dir / "case"
        report_md, report_html = build_report(db, case.case_id, report_base)
        commands.append(CommandResult(
            action="report_build", started_at=cmd_start, exit_code=0,
            status=GateStatus.PASS,
            artifact_paths=(str(report_md), str(report_html)),
        ))
    except Exception as exc:  # noqa: BLE001
        commands.append(CommandResult(
            action="report_build", started_at=cmd_start, exit_code=1,
            status=GateStatus.FAIL, error_code="REPORT_ERROR",
            error_message=str(exc),
        ))

    # --- Gate evaluation ---
    gates = evaluate_gates(case, validation, evidence, report_md, report_html)

    return _build_manifest(
        output_dir, case_path, started_at, env, commands, gates,
        case.case_id,
        str(evidence_path) if evidence_path else None,
        str(report_md) if report_md else None,
        str(report_html) if report_html else None,
        evidence.case_digest,
    )


def _build_manifest(
    run_dir: Path,
    case_path: Path,
    started_at: Any,
    env: EnvironmentInfo,
    commands: list[CommandResult],
    gates: list[GateResult],
    case_id: UUID | None = None,
    evidence_path: str | None = None,
    report_md_path: str | None = None,
    report_html_path: str | None = None,
    case_digest: str | None = None,
) -> RunManifest:
    from datetime import UTC, datetime

    final = determine_final_status(gates)
    manifest = RunManifest(
        task_id="DSK-MFY-PPE-HARDENING-005",
        case_path=str(case_path.resolve()),
        run_dir=str(run_dir.resolve()),
        started_at=started_at,
        ended_at=datetime.now(UTC),
        final_status=final,
        environment=env,
        commands=tuple(commands),
        gates=tuple(gates),
        case_id=case_id,
        evidence_path=evidence_path,
        report_md_path=report_md_path,
        report_html_path=report_html_path,
        case_digest=case_digest,
    )
    return manifest


def write_ppe_artifacts(manifest: RunManifest, output_dir: Path) -> RunManifest:
    """Persist run artifacts and return a manifest containing their SHA-256 identities."""
    import json as _json

    # environment.json
    (output_dir / "environment.json").write_text(
        manifest.environment.model_dump_json(indent=2), encoding="utf-8",
    )

    # command_results.jsonl
    with (output_dir / "command_results.jsonl").open("w", encoding="utf-8") as fh:
        for cmd in manifest.commands:
            fh.write(cmd.model_dump_json() + "\n")

    # gate_results.json
    gates_payload = [_json.loads(g.model_dump_json()) for g in manifest.gates]
    (output_dir / "gate_results.json").write_text(
        _json.dumps(gates_payload, indent=2), encoding="utf-8",
    )

    # FINAL_STATUS.txt
    (output_dir / "FINAL_STATUS.txt").write_text(
        f"{manifest.final_status.value}\n", encoding="utf-8",
    )

    # Hash every material artifact that exists before the manifest. The manifest
    # intentionally cannot contain its own digest; its consumers validate the
    # complete referenced set below and may hash the manifest externally.
    relative_artifacts = (
        "environment.json",
        "command_results.jsonl",
        "gate_results.json",
        "FINAL_STATUS.txt",
        "evidence.yaml",
        "ledger/ledger.duckdb",
        "reports/case.md",
        "reports/case.html",
        "spec.yaml",
        "case.yaml",
    )
    artifact_hashes = {
        rel: sha256_file(output_dir / rel)
        for rel in relative_artifacts
        if (output_dir / rel).is_file()
    }
    finalized = manifest.model_copy(update={"artifact_hashes": artifact_hashes})
    (output_dir / "run_manifest.json").write_text(
        finalized.model_dump_json(indent=2), encoding="utf-8",
    )
    return finalized


# ── One-Point Refine (DSK-MFY-ONE-POINT-006) ────────────────────────────


# Keywords that trigger conflict detection between desired_change and must_preserve/must_avoid
# This is a crude surface check — it does not claim semantic understanding.
# When triggered, the spec is BLOCKED and the human_owner must resolve.
_CONFLICT_PAIRS = (
    ("loudness", "dynamic"),
    ("bright", "dark"),
    ("wide", "mono"),
    ("compressed", "transient"),
    ("saturated", "clean"),
    ("spatial", "close"),
    ("reverb", "dry"),
    ("eq", "natural"),
)


def detect_conflicts(spec: OnePointSpec) -> list[str]:
    """Detect potential conflicts between desired_change and must_preserve/must_avoid.

    Returns a list of conflict descriptions. Empty list = no conflicts detected.
    """
    conflicts: list[str] = []
    desired_lower = spec.desired_change.lower()
    preserve_lower = " ".join(spec.must_preserve).lower()
    avoid_lower = " ".join(spec.must_avoid).lower()

    # A requested property that is explicitly forbidden is always a conflict.
    # Token matching is deliberately conservative and does not claim semantic
    # understanding; the human owner resolves every flagged case.
    desired_tokens = {token for token in desired_lower.replace("-", " ").split() if len(token) >= 4}
    avoid_tokens = {token for token in avoid_lower.replace("-", " ").split() if len(token) >= 4}
    for token in sorted(desired_tokens & avoid_tokens):
        conflicts.append(
            f"desired_change and must_avoid both mention '{token}' — human review is required"
        )

    for a, b in _CONFLICT_PAIRS:
        a_in_desire = a in desired_lower
        b_in_desire = b in desired_lower
        a_in_preserve = a in preserve_lower
        b_in_preserve = b in preserve_lower
        a_in_avoid = a in avoid_lower
        b_in_avoid = b in avoid_lower

        if a_in_desire and b_in_preserve:
            conflicts.append(
                f"desired_change mentions '{a}' but must_preserve includes '{b}' — "
                "these may conflict"
            )
        if b_in_desire and a_in_preserve:
            conflicts.append(
                f"desired_change mentions '{b}' but must_preserve includes '{a}' — "
                "these may conflict"
            )
        if a_in_desire and b_in_avoid:
            conflicts.append(
                f"desired_change mentions '{a}' but must_avoid requires avoiding '{b}'"
            )
        if b_in_desire and a_in_avoid:
            conflicts.append(
                f"desired_change mentions '{b}' but must_avoid requires avoiding '{a}'"
            )

    return conflicts


def _build_refine_summary(spec: OnePointSpec, result: OnePointResult) -> str:
    """Build the default reading surface — no internal acronyms, no scores."""
    lines = [
        f"# {spec.essence}",
        "",
        "## Essence",
        result.essence,
        "",
        "## Protect",
        "The following must not be diminished:",
    ]
    for item in spec.must_preserve:
        lines.append(f"- {item}")

    lines.append("- It must also avoid:")
    for item in spec.must_avoid:
        lines.append(f"  - {item}")

    lines += [
        "",
        "## Allow",
        result.allow,
    ]

    lines += [
        "",
        "## Action",
        result.action,
    ]

    lines += [
        "",
        "## Entrust",
        result.entrust,
        "",
        f"**Status:** {result.status.value}",
        f"**Owner:** {result.owner}",
        "",
        "---",
        f"Full technical evidence is indexed at `{result.evidence_path}`.",
    ]

    return "\n".join(lines) + "\n"


def _build_refine_html(summary_md: str, title: str) -> str:
    """Build minimal, accessible HTML from summary markdown."""
    import html as _html

    escaped_title = _html.escape(title)
    lines = summary_md.split("\n")
    body_lines: list[str] = []
    in_list = False
    for line in lines:
        stripped = line.strip()
        is_list_item = stripped.startswith("- ")
        if in_list and not is_list_item:
            body_lines.append("</ul>")
            in_list = False
        if not stripped:
            body_lines.append("")
        elif stripped.startswith("# "):
            body_lines.append(f"<h1>{_html.escape(stripped[2:])}</h1>")
        elif stripped.startswith("## "):
            body_lines.append(f"<h2>{_html.escape(stripped[3:])}</h2>")
        elif is_list_item:
            if not in_list:
                body_lines.append("<ul>")
                in_list = True
            body_lines.append(f"<li>{_html.escape(stripped[2:])}</li>")
        elif stripped == "---":
            body_lines.append("<hr>")
        else:
            body_lines.append(f"<p>{_html.escape(stripped)}</p>")

    if in_list:
        body_lines.append("</ul>")

    body = "\n".join(body_lines)
    return (
        "<!doctype html><html lang='en'><head><meta charset='utf-8'>"
        f"<title>{escaped_title}</title>"
        "<style>"
        "body{font:16px/1.6 system-ui,sans-serif;max-width:640px;margin:3rem auto;"
        "padding:0 1rem;color:#1a1a1a;background:#fafafa}"
        "h1{font-size:1.5rem;margin-top:2rem}h2{font-size:1.1rem;margin-top:2rem}"
        "li{margin:.25rem 0}hr{border:0;border-top:1px solid #ddd;margin:2rem 0}"
        "</style></head><body>"
        f"{body}</body></html>"
    )


# ── Lyrics Intent Evidence (DSK-MFY-LYRICS-INTENT-007) ──────────────────


LYRICS_MAX_BYTES = 1_048_576  # 1 MB
LYRICS_ALLOWED_ROOT = Path(__file__).resolve().parents[3]
SECTION_LABEL_RE = __import__("re").compile(
    r"^\s*\[?(Verse|Chorus|Bridge|Pre-Chorus|Intro|Outro|Interlude|Hook|Refrain)"
    r"\s*\d*\]?\s*:?\s*$",
    __import__("re").IGNORECASE | __import__("re").MULTILINE,
)


def _validate_lyrics_path(path_str: str) -> Path:
    """Validate a lyrics file path for safety. Raises ValueError on rejection."""

    raw = Path(path_str)
    if ".." in raw.parts:
        raise ValueError(f"Path traversal rejected: {path_str}")
    candidate = raw if raw.is_absolute() else Path.cwd() / raw
    if candidate.is_symlink() or (
        hasattr(candidate, "is_junction") and candidate.is_junction()
    ):
        raise ValueError(f"Symlink/junction rejected: {path_str}")
    resolved = candidate.resolve()
    allowed_root = LYRICS_ALLOWED_ROOT.resolve()
    if not resolved.is_relative_to(allowed_root):
        raise ValueError("Lyrics path resolves outside the authorized workspace")
    if not resolved.is_file():
        raise ValueError(f"Not a regular file: {path_str}")
    return resolved


def _load_lyrics_safe(path: Path) -> str:
    """Safely load lyrics text. Raises ValueError on rejection."""
    if path.stat().st_size > LYRICS_MAX_BYTES:
        raise ValueError(f"Lyrics file exceeds size limit ({LYRICS_MAX_BYTES} bytes)")
    raw = path.read_bytes()
    if b"\x00" in raw:
        raise ValueError("Lyrics file contains NUL bytes — rejected as binary")
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise ValueError("Lyrics file is not valid UTF-8") from exc
    if not text.strip():
        raise ValueError("Lyrics file is empty or whitespace-only")
    return text


def _analyze_lyrics_structure(text: str) -> LyricsStructuralObservations:
    """Deterministic structural analysis of lyrics text."""
    lines = text.split("\n")
    # Strip trailing empty lines
    while lines and not lines[-1].strip():
        lines.pop()

    sections: list[LyricsSection] = []
    current_label: str | None = None
    current_start = 1

    for i, line in enumerate(lines, start=1):
        stripped = line.strip()
        m = SECTION_LABEL_RE.match(stripped)
        if m:
            if current_label is not None:
                sections.append(LyricsSection(
                    label=current_label, start_line=current_start,
                    end_line=i - 1, line_count=i - current_start,
                ))
            current_label = m.group(1).strip("[]").strip()
            current_start = i
        elif not stripped and current_label is not None:
            # Empty line doesn't end a section
            pass

    if current_label is not None:
        sections.append(LyricsSection(
            label=current_label, start_line=current_start,
            end_line=len(lines), line_count=len(lines) - current_start + 1,
        ))

    # Detect repeated lines (normalized: strip, lowercase)

    from .hashing import sha256_bytes

    norm_lines: dict[str, list[int]] = {}
    for i, line in enumerate(lines, start=1):
        norm = line.strip().lower()
        if norm and len(norm) > 3:  # skip very short lines
            norm_lines.setdefault(norm, []).append(i)

    repeated: list[RepeatedLine] = []
    rep_count = 0
    for norm, locs in norm_lines.items():
        if len(locs) > 1:
            h = sha256_bytes(norm.encode("utf-8"))
            repeated.append(RepeatedLine(text_hash=h, occurrences=len(locs), locations=tuple(locs)))
            rep_count += len(locs) - 1  # count repetitions beyond first occurrence

    return LyricsStructuralObservations(
        sections=tuple(sections),
        repeated_lines=tuple(repeated),
        normalized_repetition_count=rep_count,
    )


def _process_lyrics(spec: OnePointSpec, evidence_dir: Path) -> LyricsEvidence | None:
    """Process lyrics if present in spec. Returns None if no lyrics in spec."""
    if spec.lyrics is None:
        return None

    lr = spec.lyrics

    # Rights check
    if lr.rights_basis == LyricsRights.UNKNOWN:
        return None  # body not read; caller handles NEEDS_EVIDENCE

    lyrics_dir = evidence_dir / "lyrics"
    lyrics_dir.mkdir(parents=True, exist_ok=True)

    # Validate and load
    try:
        resolved = _validate_lyrics_path(lr.path)
    except ValueError as exc:
        raise ValueError(f"[LYRICS_PATH_INVALID] {exc}") from exc

    try:
        text = _load_lyrics_safe(resolved)
    except ValueError as exc:
        raise ValueError(f"[LYRICS_LOAD_FAILED] {exc}") from exc

    # Save original copy
    original_copy = lyrics_dir / "original.txt"
    original_copy.write_bytes(resolved.read_bytes())
    from .hashing import sha256_file
    file_hash = sha256_file(resolved)
    (lyrics_dir / "original.txt.sha256").write_text(f"{file_hash}  original.txt\n", encoding="utf-8")

    # Parse
    lines = text.split("\n")
    while lines and not lines[-1].strip():
        lines.pop()
    paragraphs = [p for p in text.split("\n\n") if p.strip()]

    section_labels = SECTION_LABEL_RE.findall(text)
    unique_labels = list(dict.fromkeys(s.strip("[]").strip() for s in section_labels))

    source_facts = LyricsSourceFacts(
        path=str(resolved),
        sha256=file_hash,
        byte_size=resolved.stat().st_size,
        language=lr.language,
        version=lr.version.value,
        rights_basis=lr.rights_basis.value,
        line_count=len(lines),
        paragraph_count=len(paragraphs),
        has_explicit_section_labels=len(section_labels) > 0,
        section_labels_found=tuple(unique_labels),
    )

    structural = _analyze_lyrics_structure(text)

    uncertainties = [
        "Section labels matched by regex; not machine-classified.",
        "declared_intent is author-provided; no machine inference was performed.",
        "Structural observations are deterministic surface facts only.",
    ]

    conflicts: list[str] = []
    if lr.declared_intent:
        # Compare human-authored declarations only. Edition 0.1 never treats
        # the lyrics body as a semantic interpretation.
        punctuation = ".,;:!?()[]{}\"'"
        intent_tokens = {
            token.strip(punctuation).lower()
            for token in lr.declared_intent.split()
            if len(token.strip(punctuation)) >= 4
        }
        for item in spec.must_avoid:
            avoid_tokens = {
                token.strip(punctuation).lower()
                for token in item.split()
                if len(token.strip(punctuation)) >= 4
            }
            overlap = sorted(intent_tokens & avoid_tokens)
            if overlap:
                conflicts.append(
                    "Human-declared lyrics intent and must_avoid share the "
                    f"term(s) {', '.join(overlap)}. Owner review is required."
                )

    evidence = LyricsEvidence(
        source_facts=source_facts,
        declared_intent=lr.declared_intent,
        structural_observations=structural,
        uncertainties=tuple(uncertainties),
        conflicts=tuple(conflicts),
    )

    import json as _json
    (lyrics_dir / "lyrics_evidence.json").write_text(
        _json.dumps(_json.loads(evidence.model_dump_json()), indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    return evidence


def refine_prepare(spec: OnePointSpec, output_dir: Path) -> OnePointResult:
    """Execute the One-Point refine pipeline.

    1. Detect conflicts (fail-closed → BLOCKED).
    2. Delegate to existing PPE runner for case/ledger/evidence.
    3. Translate internal results to OnePointResult.
    4. Write progressive-disclosure result package.
    """
    import json as _json

    from .hashing import sha256_bytes

    # Reject unsafe or malformed authorized lyrics before creating a result
    # directory, so hard failures cannot leave a partial evidence package.
    if spec.lyrics is not None and spec.lyrics.rights_basis is not LyricsRights.UNKNOWN:
        try:
            preflight_path = _validate_lyrics_path(spec.lyrics.path)
        except ValueError as exc:
            raise ValueError(f"[LYRICS_PATH_INVALID] {exc}") from exc
        try:
            _load_lyrics_safe(preflight_path)
        except ValueError as exc:
            raise ValueError(f"[LYRICS_LOAD_FAILED] {exc}") from exc

    output_dir.mkdir(parents=True, exist_ok=True)
    evidence_dir = output_dir / "evidence"
    evidence_dir.mkdir(parents=True, exist_ok=True)

    # Canonical identity hash: semantic fields only, excluding UUIDs/timestamps
    canonical_fields = {
        "schema_version": spec.schema_version,
        "source": spec.source,
        "essence": spec.essence,
        "must_preserve": list(spec.must_preserve),
        "desired_change": spec.desired_change,
        "must_avoid": list(spec.must_avoid),
        "human_owner": spec.human_owner,
        "lyrics": (
            _json.loads(spec.lyrics.model_dump_json())
            if spec.lyrics is not None
            else None
        ),
    }
    spec_hash = sha256_bytes(
        _json.dumps(canonical_fields, sort_keys=True, separators=(",", ":")).encode()
    )

    # Save spec copy in evidence
    (evidence_dir / "spec.yaml").write_text(
        __import__("yaml").safe_dump(
            _json.loads(spec.model_dump_json()), sort_keys=False, allow_unicode=True,
        ),
        encoding="utf-8",
    )

    # ── Conflict detection ──
    conflicts = detect_conflicts(spec)
    if conflicts:
        result = OnePointResult(
            spec_identity=spec_hash,
            status=OnePointStatus.BLOCKED,
            essence=spec.essence,
            protect="; ".join(spec.must_preserve),
            allow=spec.desired_change,
            avoid="; ".join(spec.must_avoid),
            action="No action taken. Conflicts detected between desired_change and must_preserve/must_avoid.",
            entrust=f"Resolve the following conflicts with {spec.human_owner}: " + "; ".join(conflicts),
            owner=spec.human_owner,
            evidence_path="evidence/package_manifest.json",
            warnings=tuple(conflicts),
        )
        _write_refine_outputs(result, spec, output_dir, evidence_dir)
        return result

    # ── Lyrics processing (optional, before PPE) ──
    lyrics_evidence: LyricsEvidence | None = None
    lyrics_needs_evidence = False
    if spec.lyrics is not None:
        if spec.lyrics.rights_basis in (LyricsRights.UNKNOWN,):
            lyrics_needs_evidence = True
        else:
            try:
                lyrics_evidence = _process_lyrics(spec, evidence_dir)
            except ValueError as exc:
                err_msg = str(exc)
                # Path/format errors are hard rejections (exit 2 in CLI)
                if "[LYRICS_PATH_INVALID]" in err_msg or "[LYRICS_LOAD_FAILED]" in err_msg:
                    raise
                result = OnePointResult(
                    spec_identity=spec_hash,
                    status=OnePointStatus.NEEDS_EVIDENCE,
                    essence=spec.essence,
                    protect="; ".join(spec.must_preserve),
                    allow=spec.desired_change,
                    avoid="; ".join(spec.must_avoid),
                    action=f"Lyrics evidence could not be collected: {err_msg}",
                    entrust=f"{spec.human_owner} must provide valid lyrics evidence.",
                    owner=spec.human_owner,
                    evidence_path="evidence/package_manifest.json",
                    warnings=(err_msg,),
                )
                _write_refine_outputs(result, spec, output_dir, evidence_dir)
                return result

    # ── Delegate to PPE Runner ──
    source_path = Path(spec.source)
    if not source_path.exists():
        result = OnePointResult(
            spec_identity=spec_hash,
            status=OnePointStatus.NEEDS_EVIDENCE,
            essence=spec.essence,
            protect="; ".join(spec.must_preserve),
            allow=spec.desired_change,
            avoid="; ".join(spec.must_avoid),
            action="Source asset not found. No processing possible.",
            entrust=f"Provide a valid source path to {spec.human_owner}.",
            owner=spec.human_owner,
            evidence_path="evidence/package_manifest.json",
            warnings=(f"Source not found: {spec.source}",),
        )
        _write_refine_outputs(result, spec, output_dir, evidence_dir)
        return result

    # Preserve the exact case manifest used by the evidence pipeline. `source`
    # is a ProductionCase manifest in this prepare-only bridge facade, not an
    # audio asset path.
    (evidence_dir / "case.yaml").write_bytes(source_path.read_bytes())

    # Delegate to ppe_run for the full evidence pipeline and persist its
    # manifest, gates, environment, command log, status, and artifact hashes.
    manifest = ppe_run(source_path, evidence_dir)
    manifest = write_ppe_artifacts(manifest, evidence_dir)

    # ── Translate to OnePointResult ──
    gate_map = {g.gate_id: g.status.value for g in manifest.gates}

    if manifest.final_status == PPEFinalStatus.FAIL:
        status = OnePointStatus.FAILED
        action_text = "Technical pipeline failed. See evidence for details."
    elif manifest.final_status == PPEFinalStatus.PASS_WITH_WARNINGS:
        status = OnePointStatus.READY_FOR_REVIEW
        action_text = (
            "Input integrity verified. Evidence compiled. "
            "Technical report generated. No audio processing was performed."
        )
    else:
        status = OnePointStatus.READY_FOR_REVIEW
        action_text = "Pipeline completed. Evidence available for review."

    # ── Append lyrics evidence to action/entrust ──
    if lyrics_needs_evidence:
        status = OnePointStatus.NEEDS_EVIDENCE
        action_text += " Lyrics rights basis is unknown; lyrics evidence was not collected."
    elif lyrics_evidence is not None:
        action_text += " Lyrics structural evidence was collected."
        if lyrics_evidence.conflicts and status == OnePointStatus.READY_FOR_REVIEW:
            status = OnePointStatus.NEEDS_EVIDENCE

    entrust_text = f"{spec.human_owner} must review the evidence and make the final judgment."
    if lyrics_evidence is not None and lyrics_evidence.conflicts:
        entrust_text += (
            " Lyrics evidence conflicts were detected; owner should review "
            "evidence/lyrics/lyrics_evidence.json."
        )
    elif spec.lyrics is not None and lyrics_needs_evidence:
        entrust_text += (
            " Lyrics rights basis is unknown; owner must provide authorization "
            "before lyrics evidence can be collected."
        )

    warnings_list = [g.message for g in manifest.gates if g.status is GateStatus.WARN]
    if lyrics_evidence is not None:
        warnings_list.extend(lyrics_evidence.conflicts)

    result = OnePointResult(
        spec_identity=spec_hash,
        status=status,
        essence=spec.essence,
        protect="; ".join(spec.must_preserve),
        allow=spec.desired_change,
        avoid="; ".join(spec.must_avoid),
        action=action_text,
        entrust=entrust_text,
        owner=spec.human_owner,
        evidence_path="evidence/package_manifest.json",
        case_id=manifest.case_id,
        warnings=tuple(warnings_list),
        gate_summary=gate_map,
    )

    _write_refine_outputs(result, spec, output_dir, evidence_dir)
    return result


def _write_refine_outputs(result: OnePointResult, spec: OnePointSpec,
                          output_dir: Path, evidence_dir: Path) -> None:
    """Write the progressive-disclosure result package."""
    # result.json
    (output_dir / "result.json").write_text(
        result.model_dump_json(indent=2), encoding="utf-8",
    )

    # summary.md
    summary_md = _build_refine_summary(spec, result)
    (output_dir / "summary.md").write_text(summary_md, encoding="utf-8")

    # summary.html
    (output_dir / "summary.html").write_text(
        _build_refine_html(summary_md, spec.essence), encoding="utf-8",
    )

    # FINAL_STATUS.txt
    (output_dir / "FINAL_STATUS.txt").write_text(
        f"{result.status.value}\n", encoding="utf-8",
    )

    # One-Point package identity. This index is intentionally stored in the
    # evidence layer, keeping the default surface quiet while making every
    # material result independently verifiable.
    import json as _json

    material_paths = [
        output_dir / "result.json",
        output_dir / "summary.md",
        output_dir / "summary.html",
        output_dir / "FINAL_STATUS.txt",
        *sorted(path for path in evidence_dir.rglob("*") if path.is_file()),
    ]
    package_hashes = {
        path.relative_to(output_dir).as_posix(): sha256_file(path)
        for path in material_paths
        if path.name != "package_manifest.json"
    }
    (evidence_dir / "package_manifest.json").write_text(
        _json.dumps({"schema_version": "1.0.0", "artifacts": package_hashes}, indent=2),
        encoding="utf-8",
    )
