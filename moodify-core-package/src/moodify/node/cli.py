"""Operator CLI for the 24/7 Moodify node."""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict
from pathlib import Path

from .config import NodeConfig
from .queue import JobQueue
from .resources import snapshot
from .worker import run_forever


def _queue(config: NodeConfig) -> JobQueue:
    return JobQueue(config.db_path, lease_seconds=config.lease_seconds)


def main() -> int:
    parser = argparse.ArgumentParser(description="Moodify low-resource data node")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("init")

    enqueue = sub.add_parser("enqueue")
    enqueue.add_argument("source", type=Path)

    jobs = sub.add_parser("jobs")
    jobs.add_argument("--status", default=None)
    jobs.add_argument("--limit", type=int, default=100)

    retry = sub.add_parser("retry")
    retry.add_argument("job_id")

    sub.add_parser("recover")
    sub.add_parser("status")
    sub.add_parser("health")
    sub.add_parser("worker")

    args = parser.parse_args()
    config = NodeConfig.from_env()
    config.state_dir.mkdir(parents=True, exist_ok=True)
    config.output_root.mkdir(parents=True, exist_ok=True)
    queue = _queue(config)

    if args.command == "init":
        print(json.dumps({"db": str(config.db_path), "output_root": str(config.output_root)}, indent=2))
        return 0
    if args.command == "enqueue":
        job = queue.enqueue(args.source, config.output_root)
        print(json.dumps(asdict(job), indent=2))
        return 0
    if args.command == "jobs":
        print(json.dumps([asdict(x) for x in queue.list(args.status, args.limit)], indent=2))
        return 0
    if args.command == "retry":
        job = queue.get(args.job_id)
        if job is None:
            raise SystemExit(f"unknown job: {args.job_id}")
        queue.requeue(args.job_id)
        print(f"REQUEUED={args.job_id}")
        return 0
    if args.command == "recover":
        print(f"RECOVERED={queue.recover_expired()}")
        return 0
    if args.command == "status":
        print(json.dumps(queue.counts(), indent=2))
        return 0
    if args.command == "health":
        snap = snapshot(config.output_root)
        print(json.dumps({**queue.counts(), **asdict(snap)}, indent=2))
        return 0
    return run_forever(config)


if __name__ == "__main__":
    raise SystemExit(main())
