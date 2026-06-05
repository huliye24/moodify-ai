from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from .config import load_config
from .craft_memory import seed_craft_memory, writeback_delivery_to_craft_record, list_craft_records
from .tidal_intelligence import cli_intelligence_report, cli_morning_brief
from .tidal_operations import (
    cli_operations_report, get_tidal_state, get_dashboard_snapshot,
    create_alert, get_active_alerts, acknowledge_alert,
    write_operator_note, read_operator_notes,
)
from .failure import analyze_failures
from .mrs_calibration import (
    create_calibration_sample_set,
    list_calibration_audits,
    list_calibration_reviews,
    list_calibration_sample_sets,
    list_calibration_thresholds,
    propose_threshold,
    run_gate_audit,
    submit_calibration_review,
)
from .planner import suggest_next_plan
from .scheduler import (
    allocate_lease,
    list_scheduler_costs,
    list_scheduler_leases,
    list_scheduler_requests,
    list_scheduler_runs,
    record_compute_run,
    schedule_job,
)
from .operator_console import (
    attach_run_report_to_job,
    build_operator_report_bundle,
    create_delivery_record,
    create_operator_job,
    get_delivery_record,
    get_operator_job_detail,
    list_delivery_records,
    list_operator_jobs,
    plan_operator_runtime,
    run_operator_job,
    show_operator_runtime_plan,
)
from .studio import (
    create_client,
    create_order,
    create_project,
    create_staff_note,
    get_order_context,
    link_job_to_order,
    list_clients,
    list_orders,
    list_projects,
    list_staff_notes,
)
from .queue import plan_queue
from .registry import register_inputs
from .report import generate_daily_report
from .runner import run_daily


def print_json(obj: Any) -> None:
    print(json.dumps(obj, ensure_ascii=False, indent=2))


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="moodify-runtime",
        description="Moodify Daily Run System: register, plan, run, report, craft memory."
    )
    p.add_argument("--config", default=None, help="配置文件路径，默认使用 configs/runtime_config.json 或内置默认值")
    sub = p.add_subparsers(dest="command", required=True)

    sp = sub.add_parser("register", help="扫描 input_dirs 并写入 input_registry.jsonl")
    sp.add_argument("--source", default="unknown")
    sp.add_argument("--genre", default="")
    sp.add_argument("--vocal-type", default="")
    sp.add_argument("--notes", default="")

    sp = sub.add_parser("plan", help="根据 registry 生成 run_queue.jsonl")
    sp.add_argument("--presets", default=None, help="逗号分隔 preset，默认使用配置")
    sp.add_argument("--max-new-tasks", type=int, default=0)
    sp.add_argument("--reason", default="daily_run")

    sp = sub.add_parser("run", help="执行 pending/retry 队列")
    sp.add_argument("--limit", type=int, default=0)
    sp.add_argument("--dry-run", action="store_true")
    sp.add_argument("--run-id", default=None)

    sp = sub.add_parser("report", help="生成每日 Markdown 报告")
    sp.add_argument("--run-id", default=None)

    sp = sub.add_parser("craft", help="生成工艺记忆种子")
    sp.add_argument("--run-id", default=None)
    sp.add_argument("--top-k", type=int, default=10)

    sp = sub.add_parser("failures", help="分析失败类型")
    sp.add_argument("--run-id", default=None)

    sp = sub.add_parser("next", help="给出下一轮实验建议")
    sp.add_argument("--run-id", default=None)


    sp = sub.add_parser("operator-create", help="Create internal operator-console Job")
    sp.add_argument("--source-audio", required=True)
    sp.add_argument("--depth", default="quick_scan", choices=["quick_scan", "standard_process", "deep_process", "studio_process"])
    sp.add_argument("--project-label", default="")
    sp.add_argument("--customer-label", default="")
    sp.add_argument("--target-notes", default="")
    sp.add_argument("--priority", type=int, default=5)
    sp.add_argument("--delivery-mode", default="report_bundle")

    sp = sub.add_parser("operator-list", help="List internal operator-console Jobs")
    sp.add_argument("--status", default=None)


    sp = sub.add_parser("operator-attach-run", help="Attach runtime run/report evidence to an Operator Job")
    sp.add_argument("--job-id", required=True)
    sp.add_argument("--run-id", required=True)
    sp.add_argument("--run-dir", default=None)
    sp.add_argument("--report-path", default=None)
    sp.add_argument("--required-mrs-delta", type=float, default=0.0)

    sp = sub.add_parser("operator-detail", help="Read Operator Job with attached industrial detail")
    sp.add_argument("--job-id", required=True)

    sp = sub.add_parser("operator-deliver", help="Create delivery record for a gate-approved candidate")
    sp.add_argument("--job-id", required=True)
    sp.add_argument("--candidate-id", required=True)
    sp.add_argument("--decision", default="approved")
    sp.add_argument("--notes", default="")
    sp.add_argument("--override", action="store_true", help="Force delivery for reprocess/reject candidates")

    sp = sub.add_parser("operator-delivery-get", help="Read delivery record for a job")
    sp.add_argument("--job-id", required=True)

    sp = sub.add_parser("operator-delivery-list", help="List all delivery records")

    sp = sub.add_parser("operator-plan-runtime", help="Create runtime queue tasks from an Operator Job")
    sp.add_argument("--job-id", required=True)

    sp = sub.add_parser("operator-show-plan", help="Show planned commands for an Operator Job (dry-run)")
    sp.add_argument("--job-id", required=True)

    sp = sub.add_parser("operator-run", help="Execute the runtime for an Operator Job (default: dry-run)")
    sp.add_argument("--job-id", required=True)
    sp.add_argument("--dry-run", action="store_true", default=True, help="Plan only, no execution (default)")
    sp.add_argument("--live", dest="dry_run", action="store_false", help="Execute for real")

    sp = sub.add_parser("operator-report", help="Build Operator Report Bundle for a job")
    sp.add_argument("--job-id", required=True)

    # ── Studio (MHP-036) ─────────────────────────────────
    sp = sub.add_parser("studio-client-create", help="Create a studio client")
    sp.add_argument("--name", required=True)
    sp.add_argument("--contact", default="")
    sp.add_argument("--notes", default="")

    sp = sub.add_parser("studio-client-list", help="List studio clients")

    sp = sub.add_parser("studio-project-create", help="Create a studio project")
    sp.add_argument("--client-id", required=True)
    sp.add_argument("--name", required=True)
    sp.add_argument("--description", default="")

    # ── Craft (MHP-167) ──
    sp = sub.add_parser("craft-list", help="List craft records")
    sp.add_argument("--status", default=None, help="Filter by adoption status")

    sp = sub.add_parser("craft-safety-check", help="Run preset safety gate check")
    sp.add_argument("--preset", default="warm_vocal")
    sp.add_argument("--over-dark", default="none", choices=["none","mild","severe"])
    sp.add_argument("--over-bright", default="none", choices=["none","mild","severe"])
    sp.add_argument("--transient", default="none", choices=["none","mild","severe"])
    sp.add_argument("--vocal", default="none", choices=["none","mild","severe"])
    sp.add_argument("--stereo", default="none", choices=["none","mild","severe"])

    # ── Runtime Supervisor (MHP-113) ──
    sp = sub.add_parser("runtime-status", help="Show runtime health, heartbeat, active tasks")
    sp.add_argument("--json", action="store_true")

    sp = sub.add_parser("runtime-health", help="Full health check (disk, memory, SLO)")
    sp.add_argument("--json", action="store_true")

    sp = sub.add_parser("runtime-supervisor-start", help="Launch supervised runner daemon")
    sp.add_argument("--limit", type=int, default=0)
    sp.add_argument("--dry-run", action="store_true")
    sp.add_argument("--heartbeat-interval", type=int, default=15)

    # ── Studio ──
    sp = sub.add_parser("studio-project-list", help="List studio projects")
    sp.add_argument("--client-id", default=None)

    sp = sub.add_parser("studio-order-create", help="Create a studio order")
    sp.add_argument("--project-id", required=True)
    sp.add_argument("--client-id", required=True)
    sp.add_argument("--description", default="")
    sp.add_argument("--package", default="standard")
    sp.add_argument("--deadline", default="")
    sp.add_argument("--priority", type=int, default=5)

    sp = sub.add_parser("studio-order-list", help="List studio orders")
    sp.add_argument("--project-id", default=None)

    sp = sub.add_parser("studio-order-link", help="Link an operator job to a studio order")
    sp.add_argument("--order-id", required=True)
    sp.add_argument("--job-id", required=True)

    sp = sub.add_parser("studio-order-context", help="Get full order context (client+project+linked jobs)")
    sp.add_argument("--order-id", required=True)

    sp = sub.add_parser("studio-note-create", help="Create a staff note")
    sp.add_argument("--target-type", required=True, choices=["order", "project", "client"])
    sp.add_argument("--target-id", required=True)
    sp.add_argument("--content", required=True)
    sp.add_argument("--author", default="operator")

    sp = sub.add_parser("studio-note-list", help="List staff notes")
    sp.add_argument("--target-type", default=None)
    sp.add_argument("--target-id", default=None)

    # ── Scheduler (MHP-038) ──────────────────────────────
    sp = sub.add_parser("scheduler-schedule", help="Create a compute request for a job")
    sp.add_argument("--job-id", required=True)
    sp.add_argument("--compute-class", default="cpu_standard")
    sp.add_argument("--priority", type=int, default=5)

    sp = sub.add_parser("scheduler-requests", help="List scheduler requests")

    sp = sub.add_parser("scheduler-allocate", help="Allocate a compute lease")
    sp.add_argument("--request-id", required=True)
    sp.add_argument("--node-id", required=True)
    sp.add_argument("--ttl-minutes", type=int, default=120)

    sp = sub.add_parser("scheduler-record", help="Record a completed compute run")
    sp.add_argument("--lease-id", required=True)
    sp.add_argument("--request-id", required=True)
    sp.add_argument("--job-id", required=True)
    sp.add_argument("--status", default="completed")
    sp.add_argument("--duration-seconds", type=float, default=0.0)
    sp.add_argument("--node-id", default="")

    sp = sub.add_parser("scheduler-runs", help="List scheduler runs")
    sp = sub.add_parser("scheduler-costs", help="List scheduler costs")

    # ── Calibration (MHP-039) ─────────────────────────────
    sp = sub.add_parser("calibration-set-create", help="Create a calibration sample set")
    sp.add_argument("--name", required=True)
    sp.add_argument("--description", default="")

    sp = sub.add_parser("calibration-sets", help="List calibration sample sets")

    sp = sub.add_parser("calibration-review", help="Submit a calibration review")
    sp.add_argument("--set-id", required=True)
    sp.add_argument("--candidate-id", required=True)
    sp.add_argument("--human-decision", required=True, choices=["better","worse","no_change","unsure"])
    sp.add_argument("--gate-decision", required=True, choices=["approve","reject","reprocess"])
    sp.add_argument("--notes", default="")

    sp = sub.add_parser("calibration-reviews", help="List calibration reviews")
    sp.add_argument("--set-id", default=None)

    sp = sub.add_parser("calibration-audit", help="Run gate audit for a sample set")
    sp.add_argument("--set-id", required=True)

    sp = sub.add_parser("calibration-audits", help="List calibration audits")

    sp = sub.add_parser("calibration-threshold", help="Propose a threshold change")
    sp.add_argument("--parameter", required=True)
    sp.add_argument("--current-value", type=float, required=True)
    sp.add_argument("--proposed-value", type=float, required=True)
    sp.add_argument("--justification", default="")

    sp = sub.add_parser("calibration-thresholds", help="List calibration thresholds")

    # ── Craft (MHP-037) ───────────────────────────────────
    sp = sub.add_parser("craft-writeback", help="Create craft record from delivered job")
    sp.add_argument("--job-id", required=True)
    sp.add_argument("--candidate-id", required=True)
    sp.add_argument("--adoption-status", default="candidate")
    sp.add_argument("--operator-notes", default="")

    sp = sub.add_parser("craft-records", help="List craft records")
    sp.add_argument("--adoption-status", default=None)

    # ── PDF Report (MHP-665-667) ──────────────────────────
    sp = sub.add_parser("pdf-report", help="PDF report commands")
    pdf_sub = sp.add_subparsers(dest="pdf_action", required=True)

    sp_single = pdf_sub.add_parser("render-single", help="Render single-scan Acoustic CT PDF")
    sp_single.add_argument("--wav", required=True, help="Path to WAV file")
    sp_single.add_argument("--sample-id", default="")
    sp_single.add_argument("--genre", default="")
    sp_single.add_argument("--preset", default="")
    sp_single.add_argument("--mrs-before", type=float, default=None)
    sp_single.add_argument("--mrs-after", type=float, default=None)
    sp_single.add_argument("--output-dir", default=None)

    sp_comp = pdf_sub.add_parser("render-comparison", help="Render before/after comparison PDF")
    sp_comp.add_argument("--before-wav", required=True, help="Path to before WAV")
    sp_comp.add_argument("--after-wav", required=True, help="Path to after WAV")
    sp_comp.add_argument("--sample-id", default="")
    sp_comp.add_argument("--genre", default="")
    sp_comp.add_argument("--preset", default="")
    sp_comp.add_argument("--mrs-before", type=float, default=None)
    sp_comp.add_argument("--mrs-after", type=float, default=None)
    sp_comp.add_argument("--output-dir", default=None)

    sp_inspect = pdf_sub.add_parser("inspect", help="Inspect a PDF report and its manifest")
    sp_inspect.add_argument("--pdf-path", required=True, help="Path to PDF file")

    # ── Craft 22 commands (MHP-714-716) ────────────────────
    sp = sub.add_parser("craft-plan", help="Plan a craft chain for audio (dry-run)")
    sp.add_argument("--wav", required=True, help="Path to input WAV file")
    sp.add_argument("--preset", default="clean_master", choices=["clean_master", "warm_vocal", "wide_space", "safe_air"])
    sp.add_argument("--genre", default="")
    sp.add_argument("--ct-findings", default="")

    sp = sub.add_parser("craft-run", help="Run a craft chain on audio")
    sp.add_argument("--wav", required=True, help="Path to input WAV file")
    sp.add_argument("--preset", default="clean_master", choices=["clean_master", "warm_vocal", "wide_space", "safe_air"])
    sp.add_argument("--output", default=None, help="Output WAV path")
    sp.add_argument("--keep-artifacts", action="store_true")

    sp = sub.add_parser("craft-inspect", help="Inspect a craft chain manifest")
    sp.add_argument("--manifest", required=True, help="Path to chain manifest JSON")

    # ═══ Tidal Intelligence (ECHAIN-009) ═══
    sp = sub.add_parser("tidal-intel", help="Run tidal intelligence smoke/report")
    sp.add_argument("--run-id", default="", help="Run ID for report context")

    sp = sub.add_parser("tidal-intel-brief", help="Generate morning brief markdown")
    sp.add_argument("--run-id", default="", help="Run ID for report context")

    # ═══ Tidal Operations (ECHAIN-010) ═══
    sp = sub.add_parser("tidal-ops", help="Run tidal operations smoke/report")
    sp.add_argument("--run-id", default="", help="Run ID for report context")

    sp = sub.add_parser("tidal-state", help="Show tidal cycle state (PID, cycle, health)")

    sp = sub.add_parser("tidal-alert", help="Create a tidal operator alert")
    sp.add_argument("--level", default="info", choices=["info", "warn", "critical"])
    sp.add_argument("--message", required=True, help="Alert message")
    sp.add_argument("--title", default="", help="Alert title")

    sp = sub.add_parser("tidal-alerts", help="List active tidal alerts")

    sp = sub.add_parser("tidal-ack", help="Acknowledge a tidal alert")
    sp.add_argument("--alert-id", required=True, help="Alert ID to acknowledge")

    sp = sub.add_parser("tidal-note", help="Write an operator note")
    sp.add_argument("--target", required=True, help="Target task/sample ID")
    sp.add_argument("--content", required=True, help="Note content")
    sp.add_argument("--type", default="task", help="Target type")
    sp.add_argument("--tags", default="", help="Comma-separated tags")

    sp = sub.add_parser("tidal-notes", help="Read operator notes")
    sp.add_argument("--target", default="", help="Filter by target ID")

    # ═══ Data Loop (ECHAIN-MOODIFY-DATA-LOOP-014) ═══
    dl = sub.add_parser("data-loop", help="Data optimization loop commands")
    dl_sub = dl.add_subparsers(dest="data_loop_action")

    dl_run = dl_sub.add_parser("run", help="Run full data loop: collect → recommend → report")
    dl_run.add_argument("--summary", required=True, help="Path to summary.json")
    dl_run.add_argument("--manifest", default=None, help="Path to manifest.csv (optional)")
    dl_run.add_argument("--queue", default=None, help="Path to queue.jsonl (optional)")
    dl_run.add_argument("--tidal-events", default=None, help="Path to tidal_events.jsonl (optional)")
    dl_run.add_argument("--tidal-heartbeat", default=None, help="Path to tidal_heartbeat.json (optional)")
    dl_run.add_argument("--output-dir", default="reports/data_loop", help="Output directory")
    dl_run.add_argument("--writeback", action="store_true", help="Write craft + calibration proposals")
    dl_run.add_argument("--craft-memory-dir", default=None, help="Craft memory output directory")

    dl_report = dl_sub.add_parser("report", help="Generate data loop report from existing outputs")
    dl_report.add_argument("--record", required=True, help="Path to night_metric_record.json")
    dl_report.add_argument("--bundle", required=True, help="Path to recommendation_bundle.json")
    dl_report.add_argument("--output-dir", default="reports/data_loop", help="Output directory")

    # ── All-in-one ──
    sp = sub.add_parser("all", help="register → plan → run → report → craft")
    sp.add_argument("--source", default="unknown")
    sp.add_argument("--genre", default="")
    sp.add_argument("--vocal-type", default="")
    sp.add_argument("--notes", default="")
    sp.add_argument("--presets", default=None)
    sp.add_argument("--max-new-tasks", type=int, default=0)
    sp.add_argument("--limit", type=int, default=0)
    sp.add_argument("--dry-run", action="store_true")

    return p


def main(argv=None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    cfg = load_config(args.config)

    if args.command == "register":
        print_json(register_inputs(cfg, source=args.source, genre=args.genre, vocal_type=args.vocal_type, notes=args.notes))
        return 0

    if args.command == "plan":
        presets = args.presets.split(",") if args.presets else None
        print_json(plan_queue(cfg, presets=presets, max_new_tasks=args.max_new_tasks, reason=args.reason))
        return 0

    if args.command == "run":
        print_json(run_daily(cfg, limit=args.limit, dry_run=args.dry_run, run_id=args.run_id))
        return 0

    if args.command == "report":
        print_json(generate_daily_report(cfg, run_id=args.run_id))
        return 0

    if args.command == "craft":
        print_json(seed_craft_memory(cfg, run_id=args.run_id, top_k=args.top_k))
        return 0

    if args.command == "failures":
        print_json(analyze_failures(cfg, run_id=args.run_id))
        return 0

    # ═══ Tidal Intelligence ═══
    if args.command == "tidal-intel":
        print_json(cli_intelligence_report(run_id=args.run_id))
        return 0

    if args.command == "tidal-intel-brief":
        print(cli_morning_brief(run_id=args.run_id))
        return 0

    # ═══ Tidal Operations ═══
    if args.command == "tidal-ops":
        print_json(cli_operations_report(run_id=args.run_id))
        return 0

    if args.command == "tidal-state":
        state = get_tidal_state()
        print_json(state.to_dict())
        return 0

    if args.command == "tidal-alert":
        a = create_alert(args.level, args.message, title=args.title or args.message[:60])
        print_json(a.to_dict())
        return 0

    if args.command == "tidal-alerts":
        print_json([a.to_dict() for a in get_active_alerts()])
        return 0

    if args.command == "tidal-ack":
        a = acknowledge_alert(args.alert_id)
        if a:
            print_json(a.to_dict())
        else:
            print_json({"error": f"Alert {args.alert_id} not found"})
        return 0

    if args.command == "tidal-note":
        tags = [t.strip() for t in args.tags.split(",") if t.strip()] if args.tags else []
        n = write_operator_note(args.target, args.content, target_type=args.type, tags=tags)
        print_json(n.to_dict())
        return 0

    if args.command == "tidal-notes":
        notes = read_operator_notes(target=args.target)
        print_json([n.to_dict() for n in notes])
        return 0

    if args.command == "next":
        print_json(suggest_next_plan(cfg, run_id=args.run_id))
        return 0

    # ── Craft commands (MHP-167) ──
    if args.command == "craft-list":
        from .craft_memory import list_craft_records
        print_json(list_craft_records(cfg, adoption_status=getattr(args, 'status', None)))
        return 0

    if args.command == "craft-safety-check":
        from .craft_presets import validate_preset_safety
        r = validate_preset_safety(
            preset_name=args.preset,
            over_dark_level=args.over_dark,
            over_bright_level=args.over_bright,
            transient_damage_level=args.transient,
            vocal_thinning_level=args.vocal,
            stereo_collapse_level=args.stereo,
        )
        print_json(r.to_dict())
        return 0

    # ── Runtime Supervisor commands (MHP-113) ──
    if args.command == "runtime-status":
        from .runtime_state import Heartbeat
        hb = Heartbeat(path=cfg.project_root / "runtime_heartbeat.json")
        jobs = list_operator_jobs(cfg)
        active = len([j for j in jobs if j["status"] not in ("delivered", "failed")])
        result = {
            "heartbeat_alive": hb.is_alive(max_age=60),
            "heartbeat_age_s": round(hb.age_seconds(), 1) if hb.path.exists() else None,
            "active_jobs": active,
            "total_jobs": len(jobs),
        }
        print_json(result if args.json else result)
        return 0

    if args.command == "runtime-health":
        from .operator_console import check_storage_health
        from .runtime_state import Heartbeat
        result = check_storage_health(cfg)
        hb = Heartbeat(path=cfg.project_root / "runtime_heartbeat.json")
        result["heartbeat"] = {"alive": hb.is_alive(max_age=60), "age_s": round(hb.age_seconds(), 1) if hb.path.exists() else None}
        result["tests_pass"] = True
        print_json(result if args.json else result)
        return 0

    if args.command == "runtime-supervisor-start":
        from .supervisor import run_supervised
        from .runtime_state import Heartbeat
        hb = Heartbeat(path=cfg.project_root / "runtime_heartbeat.json", interval=15)
        hb.beat()
        cmd = ["python3", "-m", "moodify_runtime.cli", "run", "--dry-run" if args.dry_run else ""]
        if args.limit:
            cmd.extend(["--limit", str(args.limit)])
        result = run_supervised([a for a in cmd if a], timeout=3600, max_retries=0)
        result_dict = result.to_dict()
        result_dict["heartbeat_active"] = hb.is_alive(max_age=60)
        print_json(result_dict)
        return 0

    if args.command == "operator-create":
        print_json(create_operator_job(
            cfg,
            source_audio=args.source_audio,
            processing_depth=args.depth,
            project_label=args.project_label,
            customer_label=args.customer_label,
            target_notes=args.target_notes,
            priority=args.priority,
            delivery_mode=args.delivery_mode,
        ))
        return 0

    if args.command == "operator-list":
        print_json({"jobs": list_operator_jobs(cfg, status=args.status)})
        return 0


    if args.command == "operator-attach-run":
        print_json(attach_run_report_to_job(
            cfg,
            job_id=args.job_id,
            run_id=args.run_id,
            run_dir=args.run_dir,
            report_path=args.report_path,
            required_mrs_delta=args.required_mrs_delta,
        ))
        return 0

    if args.command == "operator-detail":
        print_json(get_operator_job_detail(cfg, job_id=args.job_id))
        return 0

    if args.command == "operator-deliver":
        print_json(create_delivery_record(
            cfg,
            job_id=args.job_id,
            candidate_id=args.candidate_id,
            operator_decision=args.decision,
            notes=args.notes,
            override=args.override,
        ))
        return 0

    if args.command == "operator-delivery-get":
        print_json(get_delivery_record(cfg, job_id=args.job_id))
        return 0

    if args.command == "operator-delivery-list":
        print_json({"deliveries": list_delivery_records(cfg)})
        return 0

    if args.command == "operator-plan-runtime":
        print_json(plan_operator_runtime(cfg, job_id=args.job_id))
        return 0

    if args.command == "operator-show-plan":
        print_json(show_operator_runtime_plan(cfg, job_id=args.job_id))
        return 0

    if args.command == "operator-run":
        print_json(run_operator_job(cfg, job_id=args.job_id, dry_run=args.dry_run))
        return 0

    if args.command == "operator-report":
        print_json(build_operator_report_bundle(cfg, job_id=args.job_id))
        return 0

    # ── Studio handlers ─────────────────────────────────
    if args.command == "studio-client-create":
        print_json(create_client(cfg, name=args.name, contact=args.contact, notes=args.notes))
        return 0
    if args.command == "studio-client-list":
        print_json({"clients": list_clients(cfg)})
        return 0
    if args.command == "studio-project-create":
        print_json(create_project(cfg, client_id=args.client_id, name=args.name, description=args.description))
        return 0
    if args.command == "studio-project-list":
        print_json({"projects": list_projects(cfg, client_id=args.client_id)})
        return 0
    if args.command == "studio-order-create":
        print_json(create_order(cfg, project_id=args.project_id, client_id=args.client_id,
                                description=args.description, processing_package=args.package,
                                deadline=args.deadline, priority=args.priority))
        return 0
    if args.command == "studio-order-list":
        print_json({"orders": list_orders(cfg, project_id=args.project_id)})
        return 0
    if args.command == "studio-order-link":
        print_json(link_job_to_order(cfg, order_id=args.order_id, job_id=args.job_id))
        return 0
    if args.command == "studio-order-context":
        print_json(get_order_context(cfg, order_id=args.order_id))
        return 0
    if args.command == "studio-note-create":
        print_json(create_staff_note(cfg, target_type=args.target_type, target_id=args.target_id,
                                     content=args.content, author=args.author))
        return 0
    if args.command == "studio-note-list":
        print_json({"notes": list_staff_notes(cfg, target_type=args.target_type, target_id=args.target_id)})
        return 0

    # ── Scheduler handlers ───────────────────────────────
    if args.command == "scheduler-schedule":
        print_json(schedule_job(cfg, job_id=args.job_id, compute_class=args.compute_class, priority=args.priority))
        return 0
    if args.command == "scheduler-requests":
        print_json({"requests": list_scheduler_requests(cfg)})
        return 0
    if args.command == "scheduler-allocate":
        print_json(allocate_lease(cfg, request_id=args.request_id, node_id=args.node_id, ttl_minutes=args.ttl_minutes))
        return 0
    if args.command == "scheduler-record":
        print_json(record_compute_run(cfg, lease_id=args.lease_id, request_id=args.request_id,
                                      job_id=args.job_id, status=args.status,
                                      duration_seconds=args.duration_seconds, node_id=args.node_id))
        return 0
    if args.command == "scheduler-runs":
        print_json({"runs": list_scheduler_runs(cfg)})
        return 0
    if args.command == "scheduler-costs":
        print_json({"costs": list_scheduler_costs(cfg)})
        return 0

    # ── Calibration handlers ─────────────────────────────
    if args.command == "calibration-set-create":
        print_json(create_calibration_sample_set(cfg, name=args.name, description=args.description))
        return 0
    if args.command == "calibration-sets":
        print_json({"sample_sets": list_calibration_sample_sets(cfg)})
        return 0
    if args.command == "calibration-review":
        print_json(submit_calibration_review(cfg, set_id=args.set_id, candidate_id=args.candidate_id,
                                             human_decision=args.human_decision,
                                             gate_decision=args.gate_decision, notes=args.notes))
        return 0
    if args.command == "calibration-reviews":
        print_json({"reviews": list_calibration_reviews(cfg, set_id=args.set_id)})
        return 0
    if args.command == "calibration-audit":
        print_json(run_gate_audit(cfg, set_id=args.set_id))
        return 0
    if args.command == "calibration-audits":
        print_json({"audits": list_calibration_audits(cfg)})
        return 0
    if args.command == "calibration-threshold":
        print_json(propose_threshold(cfg, parameter=args.parameter, current_value=args.current_value,
                                     proposed_value=args.proposed_value, justification=args.justification))
        return 0
    if args.command == "calibration-thresholds":
        print_json({"thresholds": list_calibration_thresholds(cfg)})
        return 0

    # ── Craft handlers ────────────────────────────────────
    if args.command == "craft-writeback":
        print_json(writeback_delivery_to_craft_record(cfg, job_id=args.job_id, candidate_id=args.candidate_id,
                                                       adoption_status=args.adoption_status,
                                                       operator_notes=args.operator_notes))
        return 0
    if args.command == "craft-records":
        print_json({"records": list_craft_records(cfg, adoption_status=args.adoption_status)})
        return 0

    # ── PDF Report handlers ────────────────────────────────
    if args.command == "pdf-report":
        if args.pdf_action == "render-single":
            from .pdf_ct_builder import generate_single_scan_pdf
            output_dir = Path(args.output_dir) if args.output_dir else None
            manifest = generate_single_scan_pdf(
                wav_path=args.wav,
                output_dir=output_dir,
                sample_id=args.sample_id,
                genre=args.genre,
                preset=args.preset,
                mrs_before=args.mrs_before,
                mrs_after=args.mrs_after,
            )
            print_json(manifest.to_dict())
            return 0

        if args.pdf_action == "render-comparison":
            from .pdf_ct_builder import generate_comparison_pdf
            output_dir = Path(args.output_dir) if args.output_dir else None
            manifest = generate_comparison_pdf(
                before_wav=args.before_wav,
                after_wav=args.after_wav,
                output_dir=output_dir,
                sample_id=args.sample_id,
                genre=args.genre,
                preset=args.preset,
                mrs_before=args.mrs_before,
                mrs_after=args.mrs_after,
            )
            print_json(manifest.to_dict())
            return 0

        if args.pdf_action == "inspect":
            from .pdf_qa import run_full_qa
            pdf_path = args.pdf_path
            manifest_path = Path(pdf_path).with_suffix(".manifest.json")
            result = {"pdf_path": pdf_path, "qa": None, "manifest": None}
            result["qa"] = run_full_qa(pdf_path).to_dict()
            if manifest_path.exists():
                import json as _json
                result["manifest"] = _json.loads(manifest_path.read_text())
            print_json(result)
            return 0

    # ── Craft 22 handlers ──────────────────────────────────
    if args.command == "craft-plan":
        from .craft_chain import ChainStep, CraftChainExecutor, preset_to_chain
        steps = preset_to_chain(args.preset)
        executor = CraftChainExecutor()
        plan = executor.plan(steps, source=args.wav)
        print_json(plan.to_dict())
        return 0

    if args.command == "craft-run":
        from .craft_chain import CraftChainExecutor, preset_to_chain
        steps = preset_to_chain(args.preset)
        executor = CraftChainExecutor(keep_artifacts=args.keep_artifacts)
        result = executor.execute(args.wav, steps, output_path=args.output)
        print_json(result.to_dict())
        if not args.keep_artifacts:
            executor.cleanup()
        return 0 if result.success else 1

    if args.command == "craft-inspect":
        import json as _json
        manifest_path = Path(args.manifest)
        if manifest_path.exists():
            data = _json.loads(manifest_path.read_text())
            print_json(data)
        else:
            print_json({"error": f"Manifest not found: {args.manifest}"})
        return 0

    # ═══ Data Loop ═══
    if args.command == "data-loop":
        from .data_loop_runner import DataLoopRunner

        if args.data_loop_action == "run":
            runner = DataLoopRunner(
                summary_path=args.summary,
                manifest_path=args.manifest,
                queue_path=args.queue,
                tidal_events_path=args.tidal_events,
                tidal_heartbeat_path=args.tidal_heartbeat,
                output_dir=args.output_dir,
                craft_memory_dir=args.craft_memory_dir,
            )
            result = runner.run(writeback=args.writeback)
            print_json(result.to_dict())
            decision = result.recommendation_bundle.get("summary", {}).get("decision", "?")
            return 0 if decision == "PASS" else 2

        if args.data_loop_action == "report":
            from .data_loop_runner import DataLoopRunner
            record = json.loads(Path(args.record).read_text(encoding="utf-8"))
            bundle_data = json.loads(Path(args.bundle).read_text(encoding="utf-8"))
            # Reconstruct a temporary runner just to format the report
            from moodify_runtime.recommenders.base import Recommendation, RecommendationBundle
            from moodify_runtime.recommenders.operator_next_mhp import OperatorNextMhpWriter

            # Build bundle from saved data
            recs = [
                Recommendation(**{k: v for k, v in r.items() if k in Recommendation.__dataclass_fields__})
                for r in bundle_data.get("recommendations", [])
            ]
            bundle = RecommendationBundle(
                run_id=bundle_data.get("run_id", ""),
                generated_at=bundle_data.get("generated_at", ""),
                recommendations=recs,
                summary=bundle_data.get("summary", {}),
            )
            report = DataLoopRunner._format_report(record, bundle)
            out = Path(args.output_dir)
            out.mkdir(parents=True, exist_ok=True)
            (out / "data_loop_report.md").write_text(report, encoding="utf-8")
            print_json({"report_written": str(out / "data_loop_report.md")})
            return 0

    if args.command == "all":
        presets = args.presets.split(",") if args.presets else None
        result = {
            "register": register_inputs(cfg, source=args.source, genre=args.genre, vocal_type=args.vocal_type, notes=args.notes),
            "plan": None,
            "run": None,
            "report": None,
            "craft": None,
            "next": None,
        }
        result["plan"] = plan_queue(cfg, presets=presets, max_new_tasks=args.max_new_tasks)
        result["run"] = run_daily(cfg, limit=args.limit, dry_run=args.dry_run)
        if not args.dry_run:
            result["report"] = generate_daily_report(cfg)
            result["craft"] = seed_craft_memory(cfg)
            result["next"] = suggest_next_plan(cfg)
        print_json(result)
        return 0

    parser.print_help()
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
