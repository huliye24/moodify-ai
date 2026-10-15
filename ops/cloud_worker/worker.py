#!/usr/bin/env python3
"""Moodify 宁夏 CPU worker —— S3 异步任务队列轮询器（adapter 版）。

用法::

    python3 worker.py                # 常驻轮询（Ctrl-C 停止）
    python3 worker.py --once         # 只扫一轮，处理 0 或 1 个任务后退出
    python3 worker.py --drain 10     # 最多处理 10 个任务后退出（冒烟用）
    python3 worker.py --check        # 只做连通性/权限/契约自检，不处理任务

职责边界（方案 §4 W2）
---------------------
worker **只**负责：认领、下载、超时、资源限制、调用 adapter、上传、状态转换、证据封装。
领域逻辑一律在 Core；job_type → Core 能力的映射在 ``adapters/``，那里也不许有领域逻辑。

设计纪律
--------
- 只**主动出站**访问 S3，不监听任何端口。
- 凭据只来自 EC2 instance profile；禁止 access key 落地，日志不打印凭据。
- 权限不足时**如实报错退出**，绝不静默假装成功。
- 未实现的能力稳定返回 ``TUNABLE_CORE_NOT_AVAILABLE``，**不留假产物**。
- 结果先上传 S3，再清理本地；失败目录最多保留 ``MOODIFY_FAILED_RETENTION_SEC``。
"""

from __future__ import annotations

import argparse
import os
import shutil
import sys
import time
import traceback
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

try:  # Unix only。Windows 上（本地跑单元测试）降级为「指标不可对齐」。
    import resource
except ImportError:  # pragma: no cover - 平台分支
    resource = None  # type: ignore[assignment]

HERE = Path(__file__).resolve().parent
for _p in (str(HERE), str(HERE / "lib")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import contract  # noqa: E402
import s3queue  # noqa: E402
from adapters import (  # noqa: E402
    CORE_REQUIRED_JOB_TYPES,
    AdapterContext,
    AdapterError,
    core_free_job_types,
    get_adapter,
    registry_covers_contract,
    unimplemented_job_types,
)
from adapters.analyze import require_core_available  # noqa: E402
from adapters.base import CoreRunner  # noqa: E402

POLL_INTERVAL = int(os.environ.get("MOODIFY_POLL_INTERVAL", "10"))
WORK_ROOT = Path(os.environ.get("MOODIFY_WORK_ROOT", "/home/ubuntu/moodify-worker/work"))
CORE_ENTRY = os.environ.get("MOODIFY_CORE_ENTRY", str(HERE / "core_entry.py"))
PYTHON_EXE = os.environ.get("MOODIFY_PYTHON", sys.executable)
LOCAL_QUOTA_BYTES = int(os.environ.get("MOODIFY_LOCAL_QUOTA_BYTES", str(150 * 1024**3)))
FAILED_RETENTION_SEC = int(os.environ.get("MOODIFY_FAILED_RETENTION_SEC", str(24 * 3600)))


def log(msg: str) -> None:
    print(f"[{time.strftime('%Y-%m-%dT%H:%M:%S')}] {msg}", flush=True)


# ------------------------------------------------------------------ 资源计量


def _children_rss() -> Optional[int]:
    """所有子进程的峰值 RSS（Linux 单位 KB → 字节）。非 Unix 返回 None。"""
    if resource is None:
        return None
    return resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss * 1024


def _children_cpu() -> Optional[float]:
    if resource is None:
        return None
    ru = resource.getrusage(resource.RUSAGE_CHILDREN)
    return ru.ru_utime + ru.ru_stime


class Meter:
    """任务期间的资源计量。

    峰值内存取子进程 ``ru_maxrss`` 的**增量**：跑完若没超过历史最大值，说明本次没过线，
    此时写 ``not_alignable`` 而不是拿一个属于别人的数字充数。
    """

    def __init__(self) -> None:
        self._rss_before = _children_rss()
        self._cpu_before = _children_cpu()
        self._wall_before = time.process_time()

    def peak_memory_bytes(self) -> Any:
        if resource is None:
            return contract.NOT_ALIGNABLE  # 平台测不到，就照实写
        now = _children_rss()
        return now if now > self._rss_before else contract.NOT_ALIGNABLE

    def cpu_seconds(self) -> Any:
        total = time.process_time() - self._wall_before
        children = _children_cpu()
        if children is not None:
            total += children - self._cpu_before
        return round(max(0.0, total), 3)


def work_root_bytes() -> int:
    total = 0
    if not WORK_ROOT.is_dir():
        return 0
    for entry in os.scandir(WORK_ROOT):
        if not entry.is_dir():
            continue
        for root, _dirs, files in os.walk(entry.path):
            for name in files:
                try:
                    total += os.path.getsize(os.path.join(root, name))
                except OSError:
                    pass
    return total


def sweep_failed_dirs(retention_sec: int = FAILED_RETENTION_SEC) -> int:
    """清掉超过保留期的失败任务目录。成功目录在任务收尾时就已删除。"""
    removed = 0
    if not WORK_ROOT.is_dir():
        return 0
    cutoff = time.time() - retention_sec
    for entry in os.scandir(WORK_ROOT):
        if not entry.is_dir():
            continue
        try:
            if entry.stat().st_mtime >= cutoff:
                continue
            shutil.rmtree(entry.path, ignore_errors=True)
            removed += 1
        except OSError:
            pass
    return removed


# ------------------------------------------------------------------ 任务执行


def _make_core_runner() -> CoreRunner:
    return CoreRunner(python_exe=PYTHON_EXE, core_entry=CORE_ENTRY, log=log)


def _upload_artifacts(artifacts: list, output_prefix: str) -> Tuple[list, list]:
    """上传产物。返回 (outputs, evidence)。上传失败即整体失败，不留半份结果。

    注意两层前缀：``output_prefix`` 是含 ``results/`` 的完整前缀（契约要求），而
    :func:`s3queue.upload_result` 自己会补 ``results/``。这里只剥一次，别剥两次。
    """
    rel_prefix = output_prefix
    if rel_prefix.startswith(s3queue.PREFIX_RESULTS):
        rel_prefix = rel_prefix[len(s3queue.PREFIX_RESULTS) :]

    outputs = []
    evidence = []
    for art in artifacts:
        key = f"{rel_prefix}{art.key_suffix}"
        try:
            s3queue.upload_result(art.path, key)
        except s3queue.S3Error as exc:
            raise AdapterError(
                "OUTPUT_UPLOAD_FAILED", f"产物上传失败：{art.key_suffix}", f"{exc.code}: {exc}"
            ) from exc
        digest = s3queue.sha256_file(art.path)
        size = os.path.getsize(art.path)
        full_key = f"{s3queue.PREFIX_RESULTS}{key}"
        outputs.append({"key": full_key, "sha256": digest, "bytes": size, "role": art.role})
        evidence.append({"key": full_key, "role": art.role, "sha256": digest})
    return outputs, evidence


def _cleanup(work_dir: Path, keep: bool) -> None:
    if keep:
        log(f"保留本地目录供诊断（{FAILED_RETENTION_SEC}s 后自动清理）：{work_dir}")
        return
    shutil.rmtree(work_dir, ignore_errors=True)


def handle(job: Dict[str, Any], raw_job: Any, wid: str) -> None:
    """处理一个已认领的任务。异常全部在内部消化成结果，不向外抛。"""
    job_id = str(job.get("job_id", "unknown"))

    # ---- 1. 契约校验。对象根本不是任务 → 退件单，不伪造结果 ----
    try:
        job = contract.validate_job(job)
    except contract.ContractError as exc:
        slip = contract.build_reject(
            job_id=job_id,
            worker_id=wid,
            code=exc.code,
            message=exc.message,
            detail=exc.detail,
            raw_job=raw_job,
        )
        s3queue.write_json_atomic(s3queue.PREFIX_FAILED + f"{job_id}.json", slip)
        s3queue.delete(s3queue.PREFIX_CLAIMED + f"{job_id}.json")
        log(f"退件 {job_id}：{exc.code} {exc.message}")
        return

    # ---- 2. 幂等：已有终态结果就直接回既有结果，不重复执行 ----
    existing = s3queue.find_existing_result(job)
    if existing is not None:
        attempt_before = int(existing.result.get("attempt") or 1)
        if existing.source == s3queue.SOURCE_IDEM or contract.is_terminal(
            existing.result, attempt_before, s3queue.MAX_ATTEMPTS
        ):
            # 同一个 job_id 的重投不需要别名（答案已经在它自己的键下）；换了 job_id 才要写，
            # 否则重投方永远等不到 —— 那是静默丢件。
            alias = None
            if contract.needs_alias(job, existing.result):
                alias = s3queue.publish_alias(
                    job_id, contract.build_alias(job=job, existing=existing.result)
                )
            s3queue.delete(s3queue.PREFIX_CLAIMED + f"{job_id}.json")
            log(
                f"{job_id} 命中既有结果（{existing.source}，"
                f"status={existing.result.get('status')}），跳过执行"
                + (f"；已写别名 {alias}" if alias else "")
            )
            return

    attempt = s3queue.attempt_of(job)

    # ---- 3. 尝试次数已用满：立刻终止，不再执行 ----
    # 这一条挡的是「能让 worker 崩溃的任务」—— 那种任务每次都在递增 attempt 之前就把进程
    # 带走，只有在这里判死才拦得住无限重跑。判死必须写一份契约合法的失败结果，
    # 所以它属于契约层（worker），不属于队列层。
    if attempt > s3queue.MAX_ATTEMPTS:
        stamp = contract.utc_now()
        result = contract.build_result(
            job=job,
            worker_id=wid,
            status=contract.STATUS_FAILED,
            attempt=attempt,
            started_at=stamp,
            finished_at=stamp,
            error=contract.build_error(
                "RETRY_EXHAUSTED",
                f"已尝试 {attempt - 1} 次，超过上限 {s3queue.MAX_ATTEMPTS}",
                "重投同一任务不会有不同结果；请修正输入本身。",
            ),
        )
        s3queue.mark_failed(job, result, wid)
        log(f"终止 {job_id}：RETRY_EXHAUSTED（attempt={attempt}）")
        return

    work_dir = WORK_ROOT / job_id
    in_dir = work_dir / "input"
    out_dir = work_dir / "out"
    scratch_dir = work_dir / "scratch"
    started_at = contract.utc_now()
    meter = Meter()
    core = _make_core_runner()

    result: Optional[Dict[str, Any]] = None
    keep_local = False

    try:
        # ---- 4. 下载前预检：不把注定失败的几 GB 拉下来 ----
        declared = s3queue.head_input(job["input"]["key"], job["input"]["bucket"])
        if declared is None:
            raise AdapterError("INPUT_NOT_FOUND", "输入对象不存在", f"{job['input']['bucket']}/{job['input']['key']}")
        contract.check_input_size(int(declared), job["limits"])

        # 需要 Core 的任务先确认 Core 在位 —— 省下把一个注定失败的 GB 级文件拉下来
        if job["job_type"] in CORE_REQUIRED_JOB_TYPES:
            require_core_available(core)

        for d in (in_dir, out_dir, scratch_dir):
            d.mkdir(parents=True, exist_ok=True)

        # ---- 5. 下载并核对哈希 ----
        local_input = in_dir / Path(job["input"]["key"]).name
        s3queue.download_input(job["input"]["key"], str(local_input), job["input"]["bucket"])
        actual = s3queue.sha256_file(str(local_input))
        contract.check_input_hash(job["input"]["sha256"], actual)

        # ---- 6. 交给 adapter（领域逻辑全在 Core 侧） ----
        adapter = get_adapter(job["job_type"])
        ctx = AdapterContext(
            job=job,
            work_dir=work_dir,
            input_path=local_input,
            out_dir=out_dir,
            scratch_dir=scratch_dir,
            core=core,
            timeout_seconds=int(job["limits"]["timeout_seconds"]),
            log=log,
        )
        outcome = adapter(ctx)

        # ---- 7. 先上传，后清理 ----
        outputs, evidence = _upload_artifacts(outcome.artifacts, job["output_prefix"])

        result = contract.build_result(
            job=job,
            worker_id=wid,
            status=outcome.status,
            attempt=attempt,
            started_at=started_at,
            input_sha256=actual,
            outputs=outputs,
            evidence=evidence,
            params={**outcome.params, "verdict": outcome.verdict} if outcome.verdict else outcome.params,
            cpu_seconds=meter.cpu_seconds(),
            peak_memory_bytes=meter.peak_memory_bytes(),
            core_version=outcome.core_version,
            tool_versions=outcome.tool_versions,
        )
        uri = s3queue.mark_done(job, result, wid)
        log(f"完成 {job_id} status={outcome.status} -> {uri}")

    except (contract.ContractError, AdapterError) as exc:
        code = getattr(exc, "code", "INTERNAL_ERROR")
        message = getattr(exc, "message", str(exc))
        detail = getattr(exc, "detail", "")
        result = contract.build_result(
            job=job,
            worker_id=wid,
            status=contract.STATUS_FAILED,
            attempt=attempt,
            started_at=started_at,
            input_sha256=_safe_hash_or_not_alignable(in_dir, job),
            cpu_seconds=meter.cpu_seconds(),
            peak_memory_bytes=meter.peak_memory_bytes(),
            core_version=core.version(),
            error=contract.build_error(code, message, detail),
        )
        if s3queue.should_retry(job, result):
            s3queue.mark_attempt_failed(job, result)
            s3queue.requeue_for_retry(job, result)
            log(f"{job_id} 第 {attempt} 次失败（{code}），已放回 pending 重试")
            keep_local = True
        else:
            s3queue.mark_failed(job, result, wid)
            log(f"失败 {job_id}：{code} {message}")
            keep_local = True

    except Exception as exc:  # noqa: BLE001 - 兜底：任何未预期异常都要留下可追溯的结果
        detail = traceback.format_exc(limit=6)
        result = contract.build_result(
            job=job,
            worker_id=wid,
            status=contract.STATUS_FAILED,
            attempt=attempt,
            started_at=started_at,
            input_sha256=contract.NOT_ALIGNABLE,
            cpu_seconds=meter.cpu_seconds(),
            peak_memory_bytes=meter.peak_memory_bytes(),
            core_version=contract.NOT_ALIGNABLE,
            error=contract.build_error("INTERNAL_ERROR", f"{type(exc).__name__}: {exc}", detail),
        )
        s3queue.mark_failed(job, result, wid)
        log(f"失败 {job_id}：未预期异常 {type(exc).__name__}: {exc}")
        log(detail)
        keep_local = True

    finally:
        _cleanup(work_dir, keep_local)


def _safe_hash_or_not_alignable(in_dir: Path, job: Dict[str, Any]) -> Any:
    """失败路径上尽力给出实测哈希；没下到就写 not_alignable，不猜。"""
    try:
        for candidate in in_dir.iterdir():
            if candidate.is_file():
                return s3queue.sha256_file(str(candidate))
    except OSError:
        pass
    return contract.NOT_ALIGNABLE


# ------------------------------------------------------------------ 主循环


def process_one(wid: str) -> bool:
    """取一个任务并处理。返回是否真的处理了任务。"""
    try:
        pending = s3queue.list_pending(limit=10)
    except s3queue.S3Error as exc:
        if exc.code in ("AccessDenied", "403", "AllAccessDisabled"):
            log(f"FATAL 无 S3 权限（{exc.code}）：instance role 未挂策略，无法轮询任务。")
            log("      请管理员把 worker 策略 attach 到 MoodifyExperimentWorkerRole。")
            raise SystemExit(2) from exc
        log(f"ERROR 列出任务失败：{exc}")
        return False

    if not pending:
        return False

    # 跳过仍在退避期的任务（not_before 未到）—— 退避是任务属性，不是轮询节奏
    now = time.time()
    job_id = None
    for candidate in pending:
        peeked = s3queue.peek_pending(candidate)
        if peeked is None:
            continue
        not_before = peeked.get("not_before")
        if isinstance(not_before, (int, float)) and not_before > now:
            continue
        job_id = candidate
        break
    if job_id is None:
        return False  # 队列里全是还在退避期的任务

    job = s3queue.claim(job_id, wid)
    if job is None:
        return False  # 被其它 worker 抢走

    log(f"认领任务 {job_id} type={job.get('job_type')}")
    handle(job, job, wid)
    return True


def drain(wid: str, max_jobs: int) -> int:
    """最多处理 max_jobs 个任务后返回实际处理数。冒烟与验收用。"""
    done = 0
    while done < max_jobs:
        if not process_one(wid):
            break
        done += 1
    return done


def self_check() -> int:
    """权限、工具、契约、目录自检。返回 0=就绪, 2=缺权限, 1=其它错误。"""
    print("=== Moodify CPU worker 自检 ===")
    ok = True

    print("\n[1] 身份")
    try:
        import boto3

        sts = boto3.client("sts", region_name=s3queue.REGION)
        arn = sts.get_caller_identity()["Arn"]
        print(f"    ARN: {arn}")
        if "MoodifyExperimentWorkerRole" not in arn:
            print("    WARN 当前身份不是 worker role")
    except Exception as exc:  # noqa: BLE001
        print(f"    FAIL {type(exc).__name__}: {str(exc)[:200]}")
        return 1

    print("\n[2] S3 权限")
    for label, fn in (
        ("列出任务 (ListBucket jobs/)", lambda: s3queue.list_pending(limit=1)),
        ("读结果前缀 (GetObject 探测)", lambda: s3queue.read_json("jobs/_selfcheck_missing.json")),
    ):
        try:
            fn()
            print(f"    OK   {label}")
        except s3queue.S3Error as exc:
            if exc.code == "NoSuchKey":
                print(f"    OK   {label}（权限通过，对象本就不存在）")
            else:
                print(f"    DENY {label} -> {exc.code}")
                ok = False
        except Exception as exc:  # noqa: BLE001
            print(f"    DENY {label} -> {type(exc).__name__} {str(exc)[:120]}")
            ok = False

    print("\n[3] 契约与 adapter")
    try:
        contract.load_schema("job")
        contract.load_schema("result")
        contract.load_schema("reject")
        print(f"    OK   schema 目录 {contract.schema_dir()}")
    except Exception as exc:  # noqa: BLE001
        print(f"    FAIL 契约 schema: {exc}")
        ok = False
    if registry_covers_contract():
        print(f"    OK   adapter 覆盖契约全部 {len(contract.JOB_TYPES)} 种 job_type")
    else:
        print("    FAIL adapter 未覆盖契约声明的 job_type")
        ok = False
    not_impl = unimplemented_job_types()
    if not_impl:
        print(f"    WARN 降级实现（将返回 TUNABLE_CORE_NOT_AVAILABLE）：{', '.join(not_impl)}")

    print("\n[4] 本地工具")
    for tool in ("ffmpeg", "ffprobe"):
        path = shutil.which(tool)
        print(f"    {'OK  ' if path else 'MISS'} {tool}: {path or '未安装'}")

    print("\n[5] Core")
    core = _make_core_runner()
    version = core.version()
    if version == contract.NOT_ALIGNABLE:
        print(
            f"    WARN Core 不可导入（{PYTHON_EXE}）；"
            f"{'/'.join(CORE_REQUIRED_JOB_TYPES)} 会返回 CORE_NOT_AVAILABLE，"
            f"其余任务不受影响（W3A 覆盖面：{', '.join(core_free_job_types())}）"
        )
    else:
        print(f"    OK   Core {version}")

    print("\n[6] 工作目录")
    try:
        WORK_ROOT.mkdir(parents=True, exist_ok=True)
        used = work_root_bytes()
        print(f"    OK   {WORK_ROOT} 可写；已用 {used / 1024**2:.1f} MiB / 上限 {LOCAL_QUOTA_BYTES / 1024**3:.0f} GiB")
    except Exception as exc:  # noqa: BLE001
        print(f"    FAIL {WORK_ROOT}: {exc}")
        ok = False

    print("\n=== 结论 ===")
    if ok:
        print("READY — 可以处理任务")
        return 0
    print("NOT READY — 最常见原因是 instance role 未挂 S3 策略（见上方 DENY 项）")
    return 2


def _over_quota() -> bool:
    used = work_root_bytes()
    if used <= LOCAL_QUOTA_BYTES:
        return False
    log(f"本地任务盘已用 {used / 1024**3:.1f} GiB，超过上限 {LOCAL_QUOTA_BYTES / 1024**3:.0f} GiB；本轮不认领新任务")
    return True


def main() -> int:
    ap = argparse.ArgumentParser(description="Moodify CPU 节点 S3 队列 worker")
    ap.add_argument("--once", action="store_true", help="只处理一个任务后退出")
    ap.add_argument("--drain", type=int, metavar="N", help="最多处理 N 个任务后退出")
    ap.add_argument("--check", action="store_true", help="只自检，不处理任务")
    ap.add_argument("--no-reclaim", action="store_true", help="启动时不回收过期 claimed")
    args = ap.parse_args()

    if args.check:
        return self_check()

    WORK_ROOT.mkdir(parents=True, exist_ok=True)
    wid = s3queue.worker_id()
    log(f"worker 启动 id={wid} bucket={s3queue.QUEUE_BUCKET} interval={POLL_INTERVAL}s")
    log(f"work_root={WORK_ROOT} core={CORE_ENTRY} python={PYTHON_EXE}")

    swept = sweep_failed_dirs()
    if swept:
        log(f"清理了 {swept} 个超过保留期的失败目录")

    if not args.no_reclaim:
        try:
            reclaimed = s3queue.reclaim_stale(wid)
            if reclaimed:
                log(f"回收过期 claimed：{len(reclaimed)} 个 -> {', '.join(reclaimed[:5])}")
        except s3queue.S3Error as exc:
            log(f"WARN 回收过期 claimed 失败：{exc}")

    if args.once:
        did = process_one(wid)
        log("单轮模式结束" + ("（处理了 1 个任务）" if did else "（队列为空）"))
        return 0

    if args.drain:
        n = drain(wid, args.drain)
        log(f"drain 结束：处理了 {n} 个任务")
        return 0

    idle_ticks = 0
    while True:
        try:
            if _over_quota():
                time.sleep(POLL_INTERVAL)
                continue
            did = process_one(wid)
            if did:
                idle_ticks = 0
            else:
                idle_ticks += 1
                if idle_ticks % 30 == 1:
                    log(f"空闲中（已 {idle_ticks * POLL_INTERVAL}s 无任务）")
        except KeyboardInterrupt:
            log("收到中断，退出")
            return 0
        except SystemExit:
            raise
        except Exception as exc:  # noqa: BLE001
            log(f"轮询异常 {type(exc).__name__}: {exc}")
        time.sleep(POLL_INTERVAL)


if __name__ == "__main__":
    sys.exit(main())
