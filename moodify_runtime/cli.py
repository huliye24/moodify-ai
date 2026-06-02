from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict

from .config import RuntimeConfig, load_config
from .craft_memory import seed_craft_memory
from .failure import analyze_failures
from .planner import suggest_next_plan
from .queue import plan_queue
from .registry import register_inputs
from .report import generate_daily_report
from .runner import run_daily
from .utils import write_json


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
