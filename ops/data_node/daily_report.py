#!/usr/bin/env python3
"""Generate a daily operations/data-production report from local evidence."""

from __future__ import annotations

import argparse
import json
import sqlite3
import statistics
import subprocess
from datetime import datetime, timedelta, timezone
from pathlib import Path


def utc_now_dt() -> datetime:
    return datetime.now(timezone.utc)


def parse_dt(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value)
    except ValueError:
        return None


def percentile(values: list[float], p: float) -> float | None:
    if not values:
        return None
    xs = sorted(values)
    if len(xs) == 1:
        return xs[0]
    pos = (len(xs) - 1) * p
    lo = int(pos)
    hi = min(lo + 1, len(xs) - 1)
    frac = pos - lo
    return xs[lo] * (1 - frac) + xs[hi] * frac


def read_jobs(db_path: Path, since: datetime) -> dict:
    result = {
        "counts": {},
        "succeeded_24h": 0,
        "failed_24h": 0,
        "duration_seconds": [],
        "recent_failures": [],
    }
    if not db_path.exists():
        return result
    con = sqlite3.connect(db_path)
    con.row_factory = sqlite3.Row
    try:
        rows = con.execute("SELECT status, COUNT(*) n FROM jobs GROUP BY status").fetchall()
        result["counts"] = {r["status"]: r["n"] for r in rows}
        jobs = con.execute(
            "SELECT * FROM jobs WHERE updated_at >= ? ORDER BY updated_at DESC",
            (since.isoformat(),),
        ).fetchall()
        for r in jobs:
            status = r["status"]
            if status == "SUCCEEDED":
                result["succeeded_24h"] += 1
                start = parse_dt(r["started_at"])
                finish = parse_dt(r["finished_at"])
                if start and finish:
                    result["duration_seconds"].append((finish - start).total_seconds())
            elif status == "FAILED":
                result["failed_24h"] += 1
                if len(result["recent_failures"]) < 5:
                    result["recent_failures"].append({
                        "job_id": r["job_id"],
                        "error": r["last_error"],
                    })
    finally:
        con.close()
    return result


def read_resources(path: Path, since: datetime) -> dict:
    rows = []
    if path.exists():
        for line in path.read_text(encoding="utf-8").splitlines():
            try:
                row = json.loads(line)
            except json.JSONDecodeError:
                continue
            stamp = parse_dt(row.get("timestamp"))
            if stamp and stamp >= since:
                rows.append(row)
    if not rows:
        return {}
    return {
        "samples": len(rows),
        "min_available_memory_mib": min(r.get("memory_available_mib", 10**9) for r in rows),
        "peak_swap_used_mib": max(r.get("swap_used_mib", 0) for r in rows),
        "min_free_disk_gib": min(r.get("disk_free_gib", 10**9) for r in rows),
        "max_load_1m": max(r.get("load_1m", 0) for r in rows),
    }


def journal_counts(service: str) -> dict:
    try:
        p = subprocess.run(
            ["journalctl", "-u", service, "--since", "24 hours ago", "--no-pager", "-o", "cat"],
            capture_output=True, text=True, timeout=15
        )
        text = p.stdout or ""
        return {
            "resource_defer_lines": text.count("resource_defer"),
            "worker_failed_lines": text.count("job_failed"),
        }
    except Exception:
        return {}


def oom_count() -> int | None:
    try:
        p = subprocess.run(
            ["journalctl", "-k", "--since", "24 hours ago", "--no-pager", "-o", "cat"],
            capture_output=True, text=True, timeout=15
        )
        text = (p.stdout or "").lower()
        needles = ("out of memory", "oom-killer", "killed process")
        return sum(text.count(n) for n in needles)
    except Exception:
        return None


def recommendation(resources: dict, journals: dict, oom: int | None) -> str:
    if oom and oom > 0:
        return "REVIEW_MEMORY"
    if resources:
        peak_swap = resources.get("peak_swap_used_mib", 0)
        min_mem = resources.get("min_available_memory_mib", 10**9)
        min_disk = resources.get("min_free_disk_gib", 10**9)
        if min_disk < 3:
            return "REVIEW_DISK"
        # Conservative signals, not automatic resize commands.
        if peak_swap > 1024 or min_mem < 200:
            return "REVIEW_MEMORY"
    if journals.get("worker_failed_lines", 0) >= 3:
        return "REVIEW_STABILITY"
    return "KEEP_2C2G"


def make_report(db_path: Path, resource_log: Path, worker_service: str) -> dict:
    now = utc_now_dt()
    since = now - timedelta(hours=24)
    jobs = read_jobs(db_path, since)
    resources = read_resources(resource_log, since)
    journals = journal_counts(worker_service)
    oom = oom_count()
    durations = jobs.pop("duration_seconds")
    stats = {
        "median_job_seconds": round(statistics.median(durations), 2) if durations else None,
        "p95_job_seconds": round(percentile(durations, 0.95), 2) if durations else None,
    }
    return {
        "generated_at": now.isoformat(),
        "window_start": since.isoformat(),
        "jobs": jobs,
        "duration_stats": stats,
        "resources": resources,
        "journal": journals,
        "oom_evidence_count": oom,
        "hardware_recommendation": recommendation(resources, journals, oom),
    }


def to_markdown(report: dict) -> str:
    j = report["jobs"]
    r = report["resources"]
    lines = [
        "# Moodify 24/7 Node Daily Report",
        "",
        f"- Generated: `{report['generated_at']}`",
        f"- Hardware recommendation: **{report['hardware_recommendation']}**",
        "",
        "## Production",
        "",
        f"- Queue counts: `{json.dumps(j.get('counts', {}), sort_keys=True)}`",
        f"- Succeeded in last 24 h: **{j.get('succeeded_24h', 0)}**",
        f"- Failed in last 24 h: **{j.get('failed_24h', 0)}**",
        f"- Median job duration: `{report['duration_stats'].get('median_job_seconds')}` s",
        f"- P95 job duration: `{report['duration_stats'].get('p95_job_seconds')}` s",
        "",
        "## Resources",
        "",
        f"- Minimum available RAM: `{r.get('min_available_memory_mib')}` MiB",
        f"- Peak swap used: `{r.get('peak_swap_used_mib')}` MiB",
        f"- Minimum free disk: `{r.get('min_free_disk_gib')}` GiB",
        f"- Max 1m load: `{r.get('max_load_1m')}`",
        "",
        "## Reliability",
        "",
        f"- resource_defer lines: `{report['journal'].get('resource_defer_lines')}`",
        f"- worker failed lines: `{report['journal'].get('worker_failed_lines')}`",
        f"- OOM evidence count: `{report.get('oom_evidence_count')}`",
        "",
        "## Recent failures",
        "",
    ]
    failures = j.get("recent_failures", [])
    if not failures:
        lines.append("- None.")
    else:
        for item in failures:
            lines.append(f"- `{item['job_id']}` — {item.get('error')}")
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--db", type=Path, default=Path("/var/lib/moodify/node.sqlite3"))
    parser.add_argument("--resource-log", type=Path, default=Path("/var/lib/moodify/ops/resource_snapshots.jsonl"))
    parser.add_argument("--reports-root", type=Path, default=Path("/var/lib/moodify/reports"))
    parser.add_argument("--worker-service", default="moodify-data-worker.service")
    args = parser.parse_args()

    report = make_report(args.db, args.resource_log, args.worker_service)
    local_day = datetime.now().strftime("%Y-%m-%d")
    out = args.reports_root / local_day
    out.mkdir(parents=True, exist_ok=True)
    (out / "node_daily_report.json").write_text(
        json.dumps(report, indent=2, sort_keys=True), encoding="utf-8"
    )
    (out / "node_daily_report.md").write_text(to_markdown(report), encoding="utf-8")
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
