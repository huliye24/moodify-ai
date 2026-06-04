from __future__ import annotations

import argparse
import json
from typing import Any

from .config import load_config
from .craft_memory import seed_craft_memory
from .failure import analyze_failures
from .planner import suggest_next_plan
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

    sp = sub.add_parser("operator-run", help="Execute the runtime for an Operator Job")
    sp.add_argument("--job-id", required=True)
    sp.add_argument("--dry-run", action="store_true")

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

    if args.command == "next":
        print_json(suggest_next_plan(cfg, run_id=args.run_id))
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
