"""Operator CLI for cloud reconstruction jobs (MFY-CR-P08).

submit/status/cancel/result for jobs, worker to run the serial processor,
review for the internal HUMAN_REQUIRED path (explicit operator decision only;
never an automatic approval).
"""

from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path

from .contract import JobStatus, ReconstructionJob
from .engine import EngineConfig, admin_finalize
from .selection import SelectDecision
from .store import JobStore
from .worker import WorkerConfig, run_forever, run_once


def _store() -> JobStore:
    return JobStore(
        Path(__import__("os").environ.get("MOODIFY_RECON_DB", "state/reconstruction_jobs.db")),
        lease_seconds=int(__import__("os").environ.get("MOODIFY_RECON_LEASE_SECONDS", "21600")),
    )


def _workspace_root() -> Path:
    import os
    return Path(os.environ.get("MOODIFY_RECON_WORKSPACE_ROOT", "state/reconstruction_workspace"))


def _require_job(store: JobStore, owner: str, job_id: str) -> ReconstructionJob:
    job = store.get_job(owner, job_id)
    if job is None:
        raise SystemExit(f"unknown job: {job_id}")
    return job


def main() -> int:
    parser = argparse.ArgumentParser(description="Moodify cloud reconstruction jobs")
    parser.add_argument("--owner", default="dev-user")
    sub = parser.add_subparsers(dest="command", required=True)

    submit = sub.add_parser("submit")
    submit.add_argument("source", type=Path)
    submit.add_argument("--idempotency-key", default=None)
    submit.add_argument("--rebuild", action="store_true")

    status = sub.add_parser("status")
    status.add_argument("job_id")

    jobs = sub.add_parser("jobs")
    jobs.add_argument("--limit", type=int, default=50)

    cancel = sub.add_parser("cancel")
    cancel.add_argument("job_id")

    result = sub.add_parser("result")
    result.add_argument("job_id")

    review = sub.add_parser("review")
    review.add_argument("job_id")
    review.add_argument("--select", choices=["SOURCE", "A", "B", "C"], default="SOURCE")

    worker = sub.add_parser("worker")
    worker.add_argument("--once", action="store_true")

    args = parser.parse_args()
    store = _store()
    ws_root = _workspace_root()
    ws_root.mkdir(parents=True, exist_ok=True)

    if args.command == "submit":
        from .audio_util import sha256_file
        from .contract import BILLING_STATE_NOT_IMPLEMENTED
        from moodify.contracts.base import utc_now

        source = Path(args.source)
        if not source.is_file():
            raise SystemExit(f"source not found: {source}")
        sha256 = sha256_file(source)
        if args.idempotency_key:
            existing = store.find_existing(
                args.owner, sha256, "reconstruction-job-v0.1", args.idempotency_key)
            if existing is not None:
                print(json.dumps({"idempotency": "RETURN_EXISTING",
                                  "job": existing.product_view()}, indent=2))
                return 0
        if not args.rebuild:
            prior = store.find_latest_success(args.owner, sha256, "reconstruction-job-v0.1")
            if prior is not None:
                print(json.dumps({"idempotency": "RETURN_EXISTING",
                                  "job": prior.product_view()}, indent=2))
                return 0
        job_id = f"job_{__import__('uuid').uuid4().hex}"
        job_dir = ws_root / job_id
        (job_dir / "input").mkdir(parents=True, exist_ok=True)
        (job_dir / "tmp").mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, job_dir / "input" / f"original{source.suffix.lower()}")
        job = ReconstructionJob(
            job_id=job_id, owner_id=args.owner,
            source_asset_id=f"sha256:{sha256}", source_sha256=sha256,
            status=JobStatus.QUEUED.value, progress_stage=None,
            requested_at=utc_now().isoformat(timespec="seconds"),
            billing_state_placeholder=BILLING_STATE_NOT_IMPLEMENTED,
            idempotency_key=args.idempotency_key,
            workspace_path=str(job_dir),
        )
        store.insert_job(job)
        print(json.dumps({"idempotency": "CREATED", "job": job.product_view()}, indent=2))
        return 0

    if args.command == "status":
        job = _require_job(store, args.owner, args.job_id)
        print(json.dumps(job.product_view(), indent=2))
        return 0

    if args.command == "jobs":
        jobs = store.list_jobs(args.owner, limit=args.limit)
        print(json.dumps([j.product_view() for j in jobs], indent=2))
        return 0

    if args.command == "cancel":
        job = store.request_cancel(args.owner, args.job_id)
        if job is None:
            raise SystemExit(f"unknown job: {args.job_id}")
        print(json.dumps(job.product_view(), indent=2))
        return 0

    if args.command == "result":
        job = _require_job(store, args.owner, args.job_id)
        result = store.get_result(args.owner, args.job_id)
        if result is None:
            raise SystemExit(f"no result for job {args.job_id} (status={job.status})")
        print(json.dumps(result.to_dict(), indent=2))
        return 0

    if args.command == "review":
        job = _require_job(store, args.owner, args.job_id)
        if job.status != JobStatus.HUMAN_REQUIRED.value:
            raise SystemExit(f"job {args.job_id} is not HUMAN_REQUIRED (status={job.status})")
        decision = SelectDecision(
            status=JobStatus.SUCCEEDED.value if args.select != "SOURCE" else JobStatus.SOURCE_WINS.value,
            selected_candidate=args.select,
            plan_hash=None,
            identity_status="HUMAN_APPROVED",
            technical_status="operator_review",
        )
        terminal = admin_finalize(
            job, store, EngineConfig(workspace_root=ws_root), decision)
        print(json.dumps({"job_id": job.job_id, "finalized": terminal}, indent=2))
        return 0

    if args.command == "worker":
        config = WorkerConfig(db_path=store.db_path, workspace_root=ws_root)
        return run_once(config) if args.once else run_forever(config)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
