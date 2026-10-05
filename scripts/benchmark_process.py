#!/usr/bin/env python3
"""PROCESS pipeline benchmark — real CLI entry points only.

Measures wall time and peak memory per stage of the public PROCESS path:

    validate  ->  moodify protocol validate <job>        (moodify.sound/0.1)
    analyze   ->  moodify protocol process <analyze job> (moodify.sound/0.2 type=analyze)
    process   ->  moodify protocol process <process job> (moodify.sound/0.1)
    verify    ->  moodify finishing verify --source --output
    total     ->  wall time of the whole sequence above

No stage is re-implemented and no private API is imported: every stage is a
subprocess call to the same CLI the desktop shell invokes
(`python -m moodify.release_cli ...`). Timings are wall-clock; peak memory is
sampled from the child's **process tree** (Windows only, no new dependencies):
a venv `python.exe` is a redirector whose real workload runs in a descendant,
and ffmpeg children appear there too.

Usage:
    python scripts/benchmark_process.py --input local_audio_assets/inputs/test_A_10s.wav --label A
    python scripts/benchmark_process.py --input ... --workdir local_audio_assets/bench/A_run1

Outputs:
    --out-json   machine-readable summary (default: <workdir>/benchmark.json)
    --out-md     markdown summary          (default: <workdir>/benchmark.md)
"""

from __future__ import annotations

import argparse
import ctypes
import ctypes.wintypes as wt
import json
import os
import subprocess
import sys
import threading
import time
from datetime import datetime, timezone
from pathlib import Path

# ---------------------------------------------------------------------------

IS_WINDOWS = sys.platform == "win32"

PROCESS_QUERY_LIMITED_INFORMATION = 0x1000


class _PROCESS_MEMORY_COUNTERS(ctypes.Structure):
    _fields_ = [
        ("cb", wt.DWORD),
        ("PageFaultCount", wt.DWORD),
        ("PeakWorkingSetSize", ctypes.c_size_t),
        ("WorkingSetSize", ctypes.c_size_t),
        ("QuotaPeakPagedPoolUsage", ctypes.c_size_t),
        ("QuotaPagedPoolUsage", ctypes.c_size_t),
        ("QuotaPeakNonPagedPoolUsage", ctypes.c_size_t),
        ("QuotaNonPagedPoolUsage", ctypes.c_size_t),
        ("PagefileUsage", ctypes.c_size_t),
        ("PeakPagefileUsage", ctypes.c_size_t),
    ]


def _sample_peak_ws(pid: int) -> tuple[int, int] | None:
    """(peak, current) working set in bytes for one live process; None if unavailable.

    NOTE (measured on this node): a venv `python.exe` on Windows is a redirector
    that spawns the base interpreter as its child, so the *real* workload lives in
    a descendant process. Sampling only the spawned pid measures the redirector
    (~4 MB). Callers must walk the process tree — see `_tree_pids`.
    """
    if not IS_WINDOWS:
        return None
    try:
        k32 = ctypes.windll.kernel32
        psapi = ctypes.windll.psapi
        # 64-bit HANDLEs must not be truncated to a default c_int: declare types.
        k32.OpenProcess.restype = ctypes.c_void_p
        k32.OpenProcess.argtypes = [wt.DWORD, wt.BOOL, wt.DWORD]
        k32.CloseHandle.argtypes = [ctypes.c_void_p]
        psapi.GetProcessMemoryInfo.argtypes = [
            ctypes.c_void_p, ctypes.POINTER(_PROCESS_MEMORY_COUNTERS), wt.DWORD,
        ]
        psapi.GetProcessMemoryInfo.restype = wt.BOOL
        access = PROCESS_QUERY_LIMITED_INFORMATION | 0x0400 | 0x0010  # QLI | QUERY | VM_READ
        h = k32.OpenProcess(access, False, pid)
        if not h:
            return None
        try:
            pmc = _PROCESS_MEMORY_COUNTERS()
            pmc.cb = ctypes.sizeof(pmc)
            if psapi.GetProcessMemoryInfo(h, ctypes.byref(pmc), pmc.cb):
                return int(pmc.PeakWorkingSetSize), int(pmc.WorkingSetSize)
            return None
        finally:
            k32.CloseHandle(h)
    except Exception:
        return None


# ── process-tree walking (Toolhelp32) ────────────────────────────────────────

TH32CS_SNAPPROCESS = 0x00000002
INVALID_HANDLE_VALUE = ctypes.c_void_p(-1).value


class _PROCESSENTRY32(ctypes.Structure):
    _fields_ = [
        ("dwSize", wt.DWORD),
        ("cntUsage", wt.DWORD),
        ("th32ProcessID", wt.DWORD),
        ("th32DefaultHeapID", ctypes.POINTER(ctypes.c_ulong)),
        ("th32ModuleID", wt.DWORD),
        ("cntThreads", wt.DWORD),
        ("th32ParentProcessID", wt.DWORD),
        ("pcPriClassBase", ctypes.c_long),
        ("dwFlags", wt.DWORD),
        ("szExeFile", ctypes.c_char * 260),
    ]


def _tree_pids(root_pid: int) -> list[int]:
    """root pid + all its descendants (snapshot at call time)."""
    if not IS_WINDOWS:
        return [root_pid]
    try:
        k32 = ctypes.windll.kernel32
        k32.CreateToolhelp32Snapshot.restype = ctypes.c_void_p
        k32.CreateToolhelp32Snapshot.argtypes = [wt.DWORD, wt.DWORD]
        snap = k32.CreateToolhelp32Snapshot(TH32CS_SNAPPROCESS, 0)
        if not snap or snap == INVALID_HANDLE_VALUE:
            return [root_pid]
        try:
            entry = _PROCESSENTRY32()
            entry.dwSize = ctypes.sizeof(entry)
            children: dict[int, list[int]] = {}
            ok = k32.Process32First(snap, ctypes.byref(entry))
            while ok:
                children.setdefault(int(entry.th32ParentProcessID), []).append(
                    int(entry.th32ProcessID))
                ok = k32.Process32Next(snap, ctypes.byref(entry))
        finally:
            k32.CloseHandle(snap)
        out, stack = [root_pid], [root_pid]
        while stack:
            for child in children.get(stack.pop(), []):
                if child not in out:
                    out.append(child)
                    stack.append(child)
        return out
    except Exception:
        return [root_pid]


def run_stage(cmd: list[str], cwd: Path, env: dict[str, str]) -> dict:
    """Run one official CLI stage; return timing + peak memory + result."""
    peak_single = 0   # max over time of the largest single process in the tree
    peak_tree = 0     # max over time of the summed working set of the tree
    stop = threading.Event()

    proc = subprocess.Popen(
        cmd, cwd=str(cwd), env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )

    def sampler() -> None:
        nonlocal peak_single, peak_tree
        while not stop.is_set():
            tree_peak, tree_cur = 0, 0
            for pid in _tree_pids(proc.pid):
                s = _sample_peak_ws(pid)
                if s:
                    p, cur = s
                    tree_peak = max(tree_peak, p)
                    tree_cur += cur
            if tree_peak:
                peak_single = max(peak_single, tree_peak)
            if tree_cur:
                peak_tree = max(peak_tree, tree_cur)
            stop.wait(0.05)

    th = threading.Thread(target=sampler, daemon=True)
    t0 = time.perf_counter()
    th.start()
    out, err = proc.communicate()
    elapsed = time.perf_counter() - t0
    stop.set()
    th.join(timeout=1.0)

    mb = 1024 * 1024
    result: dict = {
        "elapsed_s": round(elapsed, 3),
        "peak_mem_mb": round(peak_single / mb, 1) if peak_single else None,
        "peak_tree_mb": round(peak_tree / mb, 1) if peak_tree else None,
        "exit_code": proc.returncode,
        "status": "ok" if proc.returncode == 0 else "failed",
    }
    stdout = out.decode("utf-8", errors="replace").strip()
    stderr = err.decode("utf-8", errors="replace").strip()
    if proc.returncode != 0:
        result["stderr_tail"] = stderr[-400:]
    # keep the stage's own JSON result when it produced one
    if stdout.startswith("{"):
        try:
            result["cli_result"] = json.loads(stdout)
        except json.JSONDecodeError:
            pass
    return result


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--input", required=True, help="input audio file (wav/flac/mp3/aiff/m4a)")
    ap.add_argument("--label", default=None, help="short label for this input (e.g. A/B/C)")
    ap.add_argument("--preset", default="clean_master",
                    choices=["clean_master", "warm_vocal", "wide_space"])
    ap.add_argument("--workdir", default=None,
                    help="working directory for generated jobs and outputs")
    ap.add_argument("--out-json", default=None)
    ap.add_argument("--out-md", default=None)
    ap.add_argument("--max-peak-dbfs", type=float, default=None,
                    help="optional peak gate passed to finishing verify")
    args = ap.parse_args()

    src = Path(args.input).resolve()
    if not src.is_file():
        print(f"input not found: {src}", file=sys.stderr)
        return 2

    label = args.label or src.stem
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    workdir = Path(args.workdir).resolve() if args.workdir else (
        src.parent.parent / "bench" / f"{label}_{stamp}"
    )
    workdir.mkdir(parents=True, exist_ok=True)

    # Jobs are written beside their outputs; relative paths resolve against the
    # job file's own directory (MSP rule), so jobs reference the source by
    # absolute path to stay independent of the workdir location.
    job_validate = workdir / "job_process.json"
    job_analyze = workdir / "job_analyze.json"
    job_process = workdir / "job_process_0_1.json"
    out_analyze = workdir / "out_analyze"
    out_process = workdir / "out_process"

    job_process.write_text(json.dumps({
        "protocol": "moodify.sound/0.1",
        "source": str(src),
        "preset": args.preset,
        "output_dir": str(out_process),
    }, indent=2), encoding="utf-8")
    job_validate.write_text(job_process.read_text(encoding="utf-8"), encoding="utf-8")
    job_analyze.write_text(json.dumps({
        "protocol": "moodify.sound/0.2",
        "type": "analyze",
        "source": str(src),
        "output_dir": str(out_analyze),
    }, indent=2), encoding="utf-8")

    env = dict(os.environ)
    env["PYTHONUTF8"] = "1"  # repo convention: python subprocesses on zh-CN Windows

    py = sys.executable
    base = [py, "-m", "moodify.release_cli"]

    stages: dict[str, dict] = {}
    t_total0 = time.perf_counter()

    stages["validate"] = run_stage(
        base + ["protocol", "validate", str(job_validate)], workdir, env)

    stages["analyze"] = run_stage(
        base + ["protocol", "process", str(job_analyze)], workdir, env)

    stages["process"] = run_stage(
        base + ["protocol", "process", str(job_process)], workdir, env)

    # Output wav path comes from the process job's own JSON result.
    out_wav = None
    cli = stages["process"].get("cli_result") or {}
    if isinstance(cli.get("output"), str):
        out_wav = Path(cli["output"])
    if out_wav and out_wav.is_file():
        cmd = base + ["finishing", "verify", "--source", str(src), "--output", str(out_wav)]
        if args.max_peak_dbfs is not None:
            cmd += ["--max-peak-dbfs", str(args.max_peak_dbfs)]
        stages["verify"] = run_stage(cmd, workdir, env)
    else:
        stages["verify"] = {
            "elapsed_s": None, "peak_mem_mb": None, "exit_code": None,
            "status": "skipped_no_output",
        }

    total_s = time.perf_counter() - t_total0

    summary = {
        "machine": os.environ.get("COMPUTERNAME", "unknown"),
        "date": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "label": label,
        "input": str(src),
        "input_seconds": None,
        "preset": args.preset,
        "backend": "cpu",
        "stages": {
            k: {kk: vv for kk, vv in v.items() if kk != "cli_result"}
            for k, v in stages.items()
        },
        "total_s": round(total_s, 3),
        "status": "pass" if all(
            s["status"] in ("ok", "skipped_no_output") for s in stages.values()
        ) else "fail",
    }

    # input duration via ffprobe (best effort, no new dependency)
    try:
        probe = subprocess.run(
            ["ffprobe", "-v", "error", "-show_entries", "format=duration",
             "-of", "csv=p=0", str(src)],
            capture_output=True, text=True, timeout=30,
        )
        summary["input_seconds"] = round(float(probe.stdout.strip()), 3)
    except Exception:
        pass

    out_json = Path(args.out_json) if args.out_json else workdir / "benchmark.json"
    out_md = Path(args.out_md) if args.out_md else workdir / "benchmark.md"
    out_json.write_text(json.dumps(summary, indent=2, sort_keys=True), encoding="utf-8")

    lines = [
        f"# PROCESS benchmark — {label}",
        "",
        f"- input: `{src}` ({summary['input_seconds']}s)",
        f"- preset: `{args.preset}` · backend: cpu · date: {summary['date']}",
        f"- status: **{summary['status']}** · total: **{summary['total_s']}s**",
        "",
        "| stage | wall (s) | peak RAM (MB) | result |",
        "|---|---:|---:|---|",
    ]
    for name in ("validate", "analyze", "process", "verify"):
        s = summary["stages"][name]
        mem = s["peak_mem_mb"] if s["peak_mem_mb"] is not None else "—"
        lines.append(
            f"| {name} | {s['elapsed_s']} | {mem} | {s['status']} |"
        )
    lines.append(f"| **total** | **{summary['total_s']}** | — | — |")
    out_md.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"benchmark: {summary['status']}  total={summary['total_s']}s")
    print(f"json: {out_json}")
    print(f"md:   {out_md}")
    return 0 if summary["status"] == "pass" else 1


if __name__ == "__main__":
    sys.exit(main())
