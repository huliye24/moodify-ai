#!/usr/bin/env python3
"""MFY-24X7 pilot orchestrator: sequential staging -> inbox -> case -> evidence.

Runs on the node. Sources must already be in staging as <label>.wav.part.
For each song: atomic move to inbox, run the inbox ingestor immediately
(the atomic move from staging is the upload-completion signal, so the
120 s minimum age is not required), then wait for the job to reach a
terminal state and record per-case evidence.
"""

from __future__ import annotations

import json
import os
import sqlite3
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path

STAGING = Path("/var/lib/moodify/staging")
PILOT = Path("/var/lib/moodify/pilot_sources")
INBOX = Path("/var/lib/moodify/inbox")
LEDGER = Path("/var/lib/moodify/ops/ingest.sqlite3")
QUEUE_DB = Path("/var/lib/moodify/node.sqlite3")
SNAPSHOTS = Path("/var/lib/moodify/ops/resource_snapshots.jsonl")
PROGRESS = Path("/var/lib/moodify/ops/pilot_progress.json")
NODE_CLI = "/opt/moodify/.venv/bin/moodify-node"
INGEST = "/opt/moodify/ops/data_node/inbox_ingest.py"


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def run(cmd: list[str]) -> str:
    p = subprocess.run(cmd, capture_output=True, text=True)
    return p.stdout


def ledger_row(sha: str | None = None):
    con = sqlite3.connect(LEDGER)
    con.row_factory = sqlite3.Row
    if sha:
        row = con.execute(
            "SELECT * FROM ingested_sources WHERE source_sha256=?", (sha,)
        ).fetchone()
    else:
        row = con.execute(
            "SELECT * FROM ingested_sources ORDER BY first_seen_at DESC LIMIT 1"
        ).fetchone()
    con.close()
    return dict(row) if row else None


def job(job_id: str) -> dict | None:
    out = run([NODE_CLI, "jobs"])
    try:
        jobs = json.loads(out)
    except json.JSONDecodeError:
        return None
    for j in jobs:
        if j["job_id"] == job_id:
            return j
    return None


def snapshots_since(since_iso: str) -> list[dict]:
    rows = []
    if not SNAPSHOTS.exists():
        return rows
    for line in SNAPSHOTS.read_text(encoding="utf-8").splitlines():
        try:
            row = json.loads(line)
        except json.JSONDecodeError:
            continue
        if row.get("timestamp", "") >= since_iso:
            rows.append(row)
    return rows


def main() -> int:
    manifest = json.loads(Path("/opt/moodify/ops/data_node/examples/pilot_10_manifest.json").read_text(encoding="utf-8"))
    progress = {"started_at": utc_now(), "cases": []}
    if PROGRESS.exists():
        progress = json.loads(PROGRESS.read_text(encoding="utf-8"))
        progress["started_at"] = utc_now()

    PILOT.mkdir(parents=True, exist_ok=True)
    for entry in manifest["songs"]:
        label = entry["label"]
        source = Path(entry["path"])
        if any(c["label"] == label and c["status"] == "SUCCEEDED" for c in progress["cases"]):
            continue
        if not source.exists():
            print(f"SKIP {label}: source missing {source}", flush=True)
            continue
        name = source.name
        inbox_target = INBOX / name
        os.replace(source, inbox_target)

        record = {"label": label, "source": name, "moved_to_inbox_at": utc_now()}
        progress["cases"].append(record)
        PROGRESS.write_text(json.dumps(progress, indent=2), encoding="utf-8")

        # ingest immediately; atomic move from staging is the completion signal
        run(["/opt/moodify/.venv/bin/python", INGEST,
             "--inbox", str(INBOX), "--source-store", "/var/lib/moodify/sources",
             "--ledger-db", str(LEDGER), "--node-cli", NODE_CLI, "--min-age-seconds", "0"])
        row = ledger_row()
        if not row or row["original_path"] != str(inbox_target):
            record["status"] = "INGEST_ERROR"
            record["error"] = f"no ledger row for {inbox_target}"
            print(json.dumps(record), flush=True)
            continue
        record["sha256"] = row["source_sha256"]
        record["stored_path"] = row["stored_path"]
        record["enqueued_at"] = row["enqueued_at"]
        record["job_id"] = row["job_id"]
        record["enqueue_wait_s"] = 0

        deadline = time.time() + 20 * 60
        while time.time() < deadline:
            j = job(row["job_id"])
            if j and j["status"] in ("SUCCEEDED", "FAILED"):
                record["status"] = j["status"]
                record["started_at"] = j.get("started_at")
                record["finished_at"] = j.get("finished_at")
                record["case_dir"] = j.get("case_dir")
                record["attempts"] = j.get("attempts")
                record["last_error"] = j.get("last_error")
                try:
                    start = datetime.fromisoformat(j["started_at"])
                    finish = datetime.fromisoformat(j["finished_at"])
                    record["runtime_s"] = round((finish - start).total_seconds(), 1)
                except (TypeError, ValueError):
                    pass
                window = [s for s in snapshots_since(record["enqueued_at"])
                          if s["timestamp"] <= (j.get("finished_at") or utc_now())]
                record["snapshots_in_window"] = len(window)
                if window:
                    record["peak_swap_mib"] = max(s["swap_used_mib"] for s in window)
                    record["min_available_mib"] = min(s["memory_available_mib"] for s in window)
                    record["min_free_disk_gib"] = min(s["disk_free_gib"] for s in window)
                record["finished_poll_at"] = utc_now()
                PROGRESS.write_text(json.dumps(progress, indent=2), encoding="utf-8")
                print(json.dumps(record), flush=True)
                break
            time.sleep(15)
        else:
            record["status"] = "TIMEOUT"
            PROGRESS.write_text(json.dumps(progress, indent=2), encoding="utf-8")
            print(json.dumps(record), flush=True)

    print("PILOT_ORCHESTRATOR_DONE", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
