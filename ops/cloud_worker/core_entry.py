"""core_entry.py —— worker 调用唯一 Moodify Core 的**唯一**入口。

这里是 adapter 层的 RPC 垫片，不是第二套 Core
------------------------------------------------
本文件只做三件事：接参数、调 Core 的既有函数、把返回值序列化成 JSON 落盘。
**它不得包含任何领域逻辑** —— 没有 DSP、没有阈值、没有判断规则、没有状态机。

如果某个 job_type 需要在这里写业务逻辑，那说明 Core 缺能力，正确做法是按 W2.3
返回 ``TUNABLE_CORE_NOT_AVAILABLE`` 并把它记成一个 Core 缺口，而不是在这里补。

为什么走子进程而不是 in-process import
--------------------------------------
analyze 单次要跑几分钟、峰值内存数 GB。子进程让 worker 能干净地施加超时与内存上限，
也避免 Core 的 import 失败（librosa / matplotlib）把轮询进程一起带走。

只暴露 Core 独占的能力。`media_probe` / `transcode` 用 ffprobe/ffmpeg，**不经过这里**
（裁决 2026-10-15：媒体事实提取允许直接调 ffprobe，不属于 One Core 管辖）。

用法::

    python core_entry.py version                        -> {"core_version": ...}
    python core_entry.py analyze --job J --out O.json
"""

from __future__ import annotations

import argparse
import json
import sys
import traceback


def _core_version() -> str:
    """解析运行期真实的 Core 版本。解析不到写 not_alignable，不猜。"""
    try:
        from importlib.metadata import version

        return version("moodify")
    except Exception:  # noqa: BLE001 - 版本取不到不该让任务失败
        try:
            import moodify

            return getattr(moodify, "__version__", "not_alignable")
        except Exception:  # noqa: BLE001
            return "not_alignable"


def _emit(payload: dict, out_path: str | None) -> None:
    text = json.dumps(payload, ensure_ascii=False, indent=2, default=str)
    if out_path:
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(text)
    else:
        print(text)


def cmd_version(args: argparse.Namespace) -> int:
    info = {"core_version": _core_version()}
    try:
        import moodify

        info["core_root"] = str(getattr(moodify, "__file__", ""))
    except Exception as exc:  # noqa: BLE001
        info["core_root"] = "not_alignable"
        info["import_error"] = f"{type(exc).__name__}: {exc}"
    _emit(info, args.out)
    return 0


def cmd_analyze(args: argparse.Namespace) -> int:
    """调 Core 的 MSP 0.2 analyze 作业执行器。

    直接调 ``sound_protocol.execute_job``（CLI `moodify protocol process` 走的是同一个
    函数），拿到结构化的返回 dict，不必去解析 CLI 的 stdout。
    """
    from pathlib import Path

    from moodify.sound_protocol import execute_job, load_job

    job = load_job(Path(args.job))
    result = execute_job(job)
    _emit({"ok": True, "job": job, "result": result, "core_version": _core_version()}, args.out)
    return 0


def build_parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(description="worker → Core 调用入口（零领域逻辑）")
    sub = ap.add_subparsers(dest="command", required=True)

    p_version = sub.add_parser("version", help="输出运行期 Core 版本")
    p_version.add_argument("--out")
    p_version.set_defaults(func=cmd_version)

    p_analyze = sub.add_parser("analyze", help="调 Core MSP 0.2 analyze 作业")
    p_analyze.add_argument("--job", required=True, help="MSP 0.2 job 文件（由 worker 落盘）")
    p_analyze.add_argument("--out")
    p_analyze.set_defaults(func=cmd_analyze)

    return ap


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        return args.func(args)
    except Exception as exc:  # noqa: BLE001 - 统一成可解析的错误信封
        payload = {
            "ok": False,
            "error_type": type(exc).__name__,
            "error": str(exc),
            "traceback": traceback.format_exc(limit=6),
        }
        _emit(payload, getattr(args, "out", None))
        print(f"core_entry 失败: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
