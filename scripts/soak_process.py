#!/usr/bin/env python3
"""PROCESS soak test — run N jobs continuously and check for decay.

Runs the official `moodify protocol process` (0.1) job N times through the real
CLI, with fresh output directories per job, and observes (§20 of
MOODIFY_THINKPAD_HEAVY_LANE_001):

  - memory trend        (per-job peak working set of the child process)
  - output integrity    (output wav exists, non-empty, sha256 matches the
                         CLI's own reported hash)
  - process leaks       (stray ffmpeg/ffprobe children after each job)
  - temp/work files     (unexpected leftovers in the job workdir)
  - crashes             (non-zero exits, timeouts)

No models are loaded on this path, so "model cache behavior" is N/A here;
it is recorded as such rather than measured.

Usage:
    python scripts/soak_process.py --input local_audio_assets/inputs/test_A_10s.wav --jobs 12
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from benchmark_process import run_stage  # noqa: E402  (same-directory tool reuse)

POLL_STRAY = ("ffmpeg.exe", "ffprobe.exe")


def count_stray() -> dict[str, int]:
    """Count stray decoder children by image name (tasklist, no new deps)."""
    counts = {name: 0 for name in POLL_STRAY}
    try:
        out = subprocess.run(["tasklist", "/FO", "CSV", "/NH"],
                             capture_output=True, text=True, timeout=30).stdout
        low = out.lower()
        for name in POLL_STRAY:
            counts[name] = low.count(f'"{name}"')
    except Exception:
        pass
    return counts


def sha256_file(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--input", required=True)
    ap.add_argument("--jobs", type=int, default=10)
    ap.add_argument("--preset", default="clean_master",
                    choices=["clean_master", "warm_vocal", "wide_space"])
    ap.add_argument("--workdir", default=None)
    ap.add_argument("--out-json", default=None)
    args = ap.parse_args()

    src = Path(args.input).resolve()
    if not src.is_file():
        print(f"input not found: {src}", file=sys.stderr)
        return 2

    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    workdir = Path(args.workdir).resolve() if args.workdir else (
        src.parent.parent / "soak" / f"{src.stem}_{stamp}"
    )
    workdir.mkdir(parents=True, exist_ok=True)

    env = dict(os.environ)
    env["PYTHONUTF8"] = "1"
    base = [sys.executable, "-m", "moodify.release_cli"]

    print(f"soak: {args.jobs} jobs · input={src.name} · workdir={workdir}")
    jobs: list[dict] = []
    stray_before = count_stray()

    for i in range(1, args.jobs + 1):
        jdir = workdir / f"job_{i:02d}"
        jdir.mkdir(exist_ok=True)
        outdir = jdir / "out"
        job = jdir / "job.json"
        job.write_text(json.dumps({
            "protocol": "moodify.sound/0.1",
            "source": str(src),
            "preset": args.preset,
            "output_dir": str(outdir),
        }, indent=2), encoding="utf-8")

        stages = {}
        stages["validate"] = run_stage(base + ["protocol", "validate", str(job)], jdir, env)
        stages["process"] = run_stage(base + ["protocol", "process", str(job)], jdir, env)

        rec: dict = {
            "job": i,
            "status": "ok",
            "process_s": stages["process"]["elapsed_s"],
            "peak_mem_mb": stages["process"]["peak_mem_mb"],
            "output_matches_hash": None,
            "leftovers": [],
            "stray_after": {},
        }
        if stages["process"]["exit_code"] != 0:
            rec["status"] = "failed"
            rec["stderr_tail"] = stages["process"].get("stderr_tail", "")

        cli = stages["process"].get("cli_result") or {}
        out_wav = Path(cli["output"]) if isinstance(cli.get("output"), str) else None
        if out_wav and out_wav.is_file() and out_wav.stat().st_size > 0:
            # The CLI records raw hex (no "sha256:" prefix); tolerate both forms.
            cli_hash = str(cli.get("output_sha256") or "").removeprefix("sha256:")
            rec["output_matches_hash"] = (
                (sha256_file(out_wav) == cli_hash) if cli_hash else None
            )
        elif rec["status"] == "ok":
            rec["status"] = "no_output"

        time.sleep(1.0)  # let transient children exit before the stray check
        rec["stray_after"] = count_stray()
        rec["leftovers"] = sorted(
            p.name for p in jdir.iterdir()
            if p.name not in ("job.json", "out", "benchmark.json")
        )
        jobs.append(rec)
        print(f"  job {i:02d}: {rec['status']}  {rec['process_s']}s  "
              f"peak={rec['peak_mem_mb']}MB  hash_ok={rec['output_matches_hash']}")

    ok = [j for j in jobs if j["status"] == "ok"]
    mem = [j["peak_mem_mb"] for j in jobs if j["peak_mem_mb"] is not None]
    summary = {
        "machine": os.environ.get("COMPUTERNAME", "unknown"),
        "date": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "input": str(src),
        "jobs_requested": args.jobs,
        "jobs_ok": len(ok),
        "jobs_failed": args.jobs - len(ok),
        "process_s": {
            "first": jobs[0]["process_s"], "last": jobs[-1]["process_s"],
            "min": min(j["process_s"] for j in jobs),
            "max": max(j["process_s"] for j in jobs),
        },
        "peak_mem_mb": {
            "first": mem[0] if mem else None, "last": mem[-1] if mem else None,
            "max": max(mem) if mem else None,
        },
        "hash_mismatches": sum(1 for j in jobs if j["output_matches_hash"] is False),
        "stray_before": stray_before,
        "stray_end": count_stray(),
        "leftover_files": sorted({f for j in jobs for f in j["leftovers"]}),
        "model_cache": "N/A — no model is loaded on the 0.1 process path",
        "status": "pass" if len(ok) == args.jobs
        and all(j["output_matches_hash"] for j in ok) else "fail",
    }

    out_json = Path(args.out_json) if args.out_json else workdir / "soak.json"
    out_json.write_text(json.dumps(summary, indent=2, sort_keys=True), encoding="utf-8")
    print(f"soak: {summary['status']}  ok={summary['jobs_ok']}/{args.jobs}  "
          f"mem first={summary['peak_mem_mb']['first']}MB last={summary['peak_mem_mb']['last']}MB")
    print(f"json: {out_json}")
    return 0 if summary["status"] == "pass" else 1


if __name__ == "__main__":
    sys.exit(main())
