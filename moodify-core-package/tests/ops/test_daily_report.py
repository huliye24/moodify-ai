from __future__ import annotations

import importlib.util
import json
import sqlite3
from datetime import datetime, timedelta, timezone
from pathlib import Path


def load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


MODULE = load_module(
    Path(__file__).parents[3] / "ops" / "data_node" / "daily_report.py",
    "daily_report",
)


def make_db(path: Path):
    con = sqlite3.connect(path)
    con.executescript("""
    CREATE TABLE jobs (
      job_id TEXT PRIMARY KEY,
      source_path TEXT,
      output_root TEXT,
      status TEXT,
      attempts INTEGER DEFAULT 0,
      created_at TEXT,
      updated_at TEXT,
      started_at TEXT,
      finished_at TEXT,
      lease_until TEXT,
      case_dir TEXT,
      last_error TEXT
    );
    """)
    now = datetime.now(timezone.utc)
    con.execute(
        "INSERT INTO jobs VALUES(?,?,?,?,?,?,?,?,?,?,?,?)",
        (
            "job_1","a.wav","out","SUCCEEDED",1,
            (now-timedelta(minutes=2)).isoformat(),
            now.isoformat(),
            (now-timedelta(seconds=40)).isoformat(),
            now.isoformat(),None,"case",None
        )
    )
    con.commit()
    con.close()


def test_read_jobs_and_resources(tmp_path: Path):
    db = tmp_path / "node.sqlite3"
    make_db(db)
    since = datetime.now(timezone.utc) - timedelta(hours=24)
    jobs = MODULE.read_jobs(db, since)
    assert jobs["succeeded_24h"] == 1
    assert jobs["duration_seconds"][0] >= 39

    log = tmp_path / "res.jsonl"
    now = datetime.now(timezone.utc).isoformat()
    log.write_text(json.dumps({
        "timestamp": now,
        "memory_available_mib": 700,
        "swap_used_mib": 76,
        "disk_free_gib": 20,
        "load_1m": 0.5
    }) + "\n", encoding="utf-8")
    resources = MODULE.read_resources(log, since)
    assert resources["peak_swap_used_mib"] == 76
    assert MODULE.recommendation(resources, {}, 0) == "KEEP_2C2G"
