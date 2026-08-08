from __future__ import annotations

import json
from pathlib import Path
from uuid import UUID

import typer

from .hashing import sha256_file
from .metrics import comparison_metrics
from .schemas import (
    HumanApproval,
    MeasurementRecord,
    MoodifyRule,
    OnePointSpec,
    PPEFinalStatus,
    ProductionCase,
    ResearchHypothesis,
    RuleState,
)
from .serialization import read_model, write_yaml
from .services import (
    TRANSITIONS,
    build_report,
    compile_evidence,
    load_audio,
    measure_all,
    ppe_run,
    promote_rule_atomic,
    refine_prepare,
    regression,
    validate_case,
    validate_rule,
    write_metric_parquet,
    write_ppe_artifacts,
)
from .store import LedgerStore

app = typer.Typer(help="Immutable local research-production evidence bridge.", no_args_is_help=True)
case_app = typer.Typer(no_args_is_help=True)
assets_app = typer.Typer(no_args_is_help=True)
measure_app = typer.Typer(no_args_is_help=True)
evidence_app = typer.Typer(no_args_is_help=True)
hypothesis_app = typer.Typer(no_args_is_help=True)
rule_app = typer.Typer(no_args_is_help=True)
regression_app = typer.Typer(no_args_is_help=True)
report_app = typer.Typer(no_args_is_help=True)
ppe_app = typer.Typer(no_args_is_help=True)
refine_app = typer.Typer(no_args_is_help=True)
app.add_typer(case_app, name="case"); app.add_typer(assets_app, name="assets")
app.add_typer(measure_app, name="measure"); app.add_typer(evidence_app, name="evidence")
app.add_typer(hypothesis_app, name="hypothesis"); app.add_typer(rule_app, name="rule")
app.add_typer(regression_app, name="regression"); app.add_typer(report_app, name="report")
app.add_typer(ppe_app, name="ppe"); app.add_typer(refine_app, name="refine")


def store(root: Path) -> LedgerStore:
    return LedgerStore(root)


def emit(model: object) -> None:
    if hasattr(model, "model_dump_json"):
        typer.echo(model.model_dump_json(indent=2))
    else:
        typer.echo(json.dumps(model, indent=2, default=str))


@case_app.command("create")
def case_create(manifest: Path, root: Path = typer.Option(Path(".moodify-bridge"), "--root")) -> None:
    case = read_model(manifest, ProductionCase)
    store(root).create_case(case)
    typer.echo(str(case.case_id))


@case_app.command("validate")
def case_validate(case_id: UUID, root: Path = typer.Option(Path(".moodify-bridge"), "--root")) -> None:
    db = store(root); result = validate_case(db.get_case(case_id)); db.add_validation(result); emit(result)
    if not result.valid: raise typer.Exit(1)


@assets_app.command("hash")
def assets_hash(path: Path) -> None:
    typer.echo(sha256_file(path))


@measure_app.command("run")
def measure_run(case_id: UUID, asset_id: UUID, audio: Path,
                root: Path = typer.Option(Path(".moodify-bridge"), "--root")) -> None:
    db = store(root); case = db.get_case(case_id)
    asset = next((a for a in case.assets if a.asset_id == asset_id), None)
    if asset is None: raise typer.BadParameter(f"asset {asset_id} is not in case {case_id}")
    if sha256_file(audio) != asset.sha256: raise typer.BadParameter("audio hash does not match archived asset identity")
    samples, rate = load_audio(audio)
    for adapter, output in measure_all(samples, rate).items():
        parquet = root / "metrics" / str(case_id) / f"{asset_id}-{adapter}.parquet"
        write_metric_parquet(parquet, output)
        record = MeasurementRecord(case_id=case_id, asset_id=asset_id, adapter=adapter,
                                   values=output.values, units=output.units,
                                   parquet_path=str(parquet.resolve()), warnings=output.warnings)
        db.add_measurement(record); emit(record)


@evidence_app.command("compile")
def evidence_compile(case_id: UUID, output: Path,
                     root: Path = typer.Option(Path(".moodify-bridge"), "--root")) -> None:
    packet = compile_evidence(store(root), case_id); write_yaml(output, packet); emit(packet)


@app.command("compare")
def compare(reference: Path, candidate: Path, output: Path | None = None) -> None:
    a, rate_a = load_audio(reference); b, rate_b = load_audio(candidate)
    if rate_a != rate_b: raise typer.BadParameter("sample rates differ; explicit resampling is required")
    result = comparison_metrics(a, b)
    if output is not None: write_metric_parquet(output, result)
    emit({"values": result.values, "units": result.units, "warnings": result.warnings})


@hypothesis_app.command("create")
def hypothesis_create(hypothesis_id: str, version: str, title: str, statement: str,
                      expected_evidence: list[str] = typer.Option(..., "--evidence"),
                      created_by: str = typer.Option(..., "--created-by"), output: Path = typer.Option(..., "--output")) -> None:
    hypothesis = ResearchHypothesis(hypothesis_id=hypothesis_id, version=version, title=title,
                                    statement=statement, expected_evidence=tuple(expected_evidence), created_by=created_by)
    write_yaml(output, hypothesis); emit(hypothesis)


@rule_app.command("validate")
def rule_validate(path: Path, root: Path = typer.Option(Path(".moodify-bridge"), "--root")) -> None:
    db = store(root); result = validate_rule(db, read_model(path, MoodifyRule)); db.add_validation(result); emit(result)
    if not result.valid: raise typer.Exit(1)


@rule_app.command("promote")
def rule_promote(path: Path, target: RuleState, approval: Path,
                 root: Path = typer.Option(Path(".moodify-bridge"), "--root")) -> None:
    try:
        record = read_model(approval, HumanApproval)
    except FileNotFoundError:
        typer.echo("[APPROVAL_FILE_MISSING] Human approval file not found.", err=True)
        raise typer.Exit(code=2)
    try:
        rule = read_model(path, MoodifyRule)
    except FileNotFoundError:
        typer.echo(f"[RULE_FILE_MISSING] Rule file not found: {path}", err=True)
        raise typer.Exit(code=2)
    if (record.rule_id, record.rule_version) != (rule.rule_id, rule.version):
        typer.echo(
            f"[APPROVAL_RULE_MISMATCH] approval ({record.rule_id}@{record.rule_version}) "
            f"does not match rule ({rule.rule_id}@{rule.version}).",
            err=True,
        )
        raise typer.Exit(code=2)
    if target not in TRANSITIONS[rule.state]:
        allowed = ", ".join(s.value for s in TRANSITIONS[rule.state]) if TRANSITIONS[rule.state] else "none"
        typer.echo(
            f"[INVALID_RULE_TRANSITION] {rule.state.value} -> {target.value}. "
            f"Allowed targets: {allowed}.",
            err=True,
        )
        raise typer.Exit(code=2)
    db = store(root)
    try:
        promoted = promote_rule_atomic(db, path, target, record)
    except RuntimeError as exc:
        typer.echo(f"[PROMOTION_RECOVERY_REQUIRED] {exc}", err=True)
        raise typer.Exit(code=3)
    emit(promoted)


@regression_app.command("run")
def regression_run(case_id: UUID, replay_case: Path,
                   root: Path = typer.Option(Path(".moodify-bridge"), "--root")) -> None:
    db = store(root); archived = db.get_case(case_id)
    if not archived.golden: raise typer.BadParameter("regression requires an archived golden case")
    result = regression(db, case_id, replay_case); db.add_validation(result); emit(result)
    if not result.valid: raise typer.Exit(1)


@report_app.command("build")
def report_build(case_id: UUID, output: Path,
                 root: Path = typer.Option(Path(".moodify-bridge"), "--root")) -> None:
    markdown, html_path = build_report(store(root), case_id, output)
    typer.echo(f"{markdown}\n{html_path}")


@ppe_app.command("run")
def ppe_run_command(
    case_path: Path = typer.Argument(..., help="Path to case YAML manifest."),
    output_dir: Path = typer.Option(..., "--output-dir", help="New or empty output directory."),
) -> None:
    if output_dir.exists():
        contents = list(output_dir.iterdir())
        if contents:
            typer.echo(
                f"[OUTPUT_DIR_NOT_EMPTY] {output_dir.resolve()} is not empty. "
                "Specify a new or empty directory to avoid overwriting history.",
                err=True,
            )
            raise typer.Exit(code=2)

    try:
        manifest = ppe_run(case_path, output_dir)
    except Exception as exc:  # noqa: BLE001
        typer.echo(f"Error: {exc}", err=True)
        raise typer.Exit(code=1)

    manifest = write_ppe_artifacts(manifest, output_dir)

    if manifest.final_status == PPEFinalStatus.FAIL:
        typer.echo("\nPPE run FAILED — status: FAIL")
    else:
        typer.echo(f"\nPPE run complete — status: {manifest.final_status.value}")

    typer.echo(f"  Run dir:   {manifest.run_dir}")
    typer.echo(f"  Case ID:   {manifest.case_id}")
    typer.echo(f"  Evidence:  {manifest.evidence_path}")
    typer.echo(f"  Report MD: {manifest.report_md_path}")
    typer.echo(f"  Report HTML: {manifest.report_html_path}")
    typer.echo("  Gates:")
    for g in manifest.gates:
        flag = {"PASS": "[PASS]", "WARN": "[WARN]", "FAIL": "[FAIL]"}[g.status.value]
        typer.echo(f"    {flag} {g.gate_id}: {g.reason_code}")

    final_code = 0 if manifest.final_status != PPEFinalStatus.FAIL else 1
    raise typer.Exit(code=final_code)


@refine_app.command("prepare")
def refine_prepare_command(
    spec_path: Path = typer.Argument(..., help="Path to OnePointSpec YAML."),
    output_dir: Path = typer.Option(..., "--output-dir", help="New or empty output directory."),
) -> None:
    """Prepare a One-Point refinement plan and evidence package."""
    if output_dir.exists():
        contents = list(output_dir.iterdir())
        if contents:
            typer.echo(
                f"[OUTPUT_DIR_NOT_EMPTY] {output_dir.resolve()} is not empty. "
                "Specify a new or empty directory to avoid overwriting history.",
                err=True,
            )
            raise typer.Exit(code=2)

    try:
        spec = read_model(spec_path, OnePointSpec)
    except FileNotFoundError:
        typer.echo(f"[SPEC_FILE_MISSING] Spec file not found: {spec_path}", err=True)
        raise typer.Exit(code=2)
    except Exception as exc:  # noqa: BLE001
        typer.echo(f"[SPEC_INVALID] Cannot parse spec: {exc}", err=True)
        raise typer.Exit(code=2)

    try:
        result = refine_prepare(spec, output_dir)
    except ValueError as exc:
        err_msg = str(exc)
        if "[LYRICS_PATH_INVALID]" in err_msg or "[LYRICS_LOAD_FAILED]" in err_msg:
            typer.echo(f"[LYRICS_REJECTED] {err_msg}", err=True)
        else:
            typer.echo(f"[SPEC_INVALID] {err_msg}", err=True)
        raise typer.Exit(code=2)
    except Exception as exc:  # noqa: BLE001
        typer.echo(f"Error: {exc}", err=True)
        raise typer.Exit(code=1)

    typer.echo(f"\nRefine complete — status: {result.status.value}")
    typer.echo(f"  Essence: {result.essence}")
    typer.echo(f"  Owner:   {result.owner}")
    typer.echo(f"  Action:  {result.action}")
    typer.echo(f"  Entrust: {result.entrust}")
    if result.warnings:
        typer.echo(f"  Warnings: {'; '.join(result.warnings)}")

    exit_map = {
        "READY_FOR_REVIEW": 0,
        "BLOCKED": 2,
        "NEEDS_EVIDENCE": 1,
        "FAILED": 1,
    }
    raise typer.Exit(code=exit_map.get(result.status.value, 1))


if __name__ == "__main__":
    app()
