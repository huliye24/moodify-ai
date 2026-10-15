"""moodify.cpu-job/0.1 —— 任务契约与结果契约的唯一 Python 实现。

单一权威原则
------------
契约的权威是两份 JSON Schema 文件（`schemas/cloud/cpu_job.0.1.schema.json` 与
`cpu_result.0.1.schema.json`）。本模块只是它们在 worker 侧的**加载器 + 默认值补齐 +
错误码分类**，不构成第二权威；Studio 侧（JS）对本文件不做镜像实现，而是读同一份 schema。

任何无法对齐的指标写字符串 ``NOT_ALIGNABLE``，不得补算或估填。
"""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from typing import Any, Dict, Optional

try:
    import jsonschema
except ImportError as exc:  # pragma: no cover - 部署环境缺依赖时给出可操作的错误
    raise ImportError(
        "contract.py 需要 jsonschema（Moodify Core 的既有依赖）。"
        "请先安装 Core / `pip install jsonschema`。"
    ) from exc

JOB_SCHEMA_VERSION = "moodify.cpu-job/0.1"
RESULT_SCHEMA_VERSION = "moodify.cpu-result/0.1"

JOB_TYPES = ("probe", "transcode", "analyze", "judge_before", "manifest", "smoke")

#: 结果状态。INCONCLUSIVE / HUMAN_REQUIRED 不是失败，是诚实结论。
STATUS_DONE = "DONE"
STATUS_FAILED = "FAILED"
STATUS_INCONCLUSIVE = "INCONCLUSIVE"
STATUS_HUMAN_REQUIRED = "HUMAN_REQUIRED"

#: 无法对齐的指标的占位符。
NOT_ALIGNABLE = "not_alignable"

DEFAULT_TIMEOUT_SECONDS = 1800
DEFAULT_MAX_INPUT_BYTES = 2147483648  # 2 GiB

#: 错误码 → 是否可重试。可重试性由错误码决定，不由调用方随意填写。
RETRYABLE_BY_CODE: Dict[str, bool] = {
    "SCHEMA_INVALID": False,          # 生产者的问题，重投还是坏的
    "UNKNOWN_JOB_TYPE": False,        # 契约不认识，重投无用
    "INPUT_NOT_FOUND": True,          # 对象可能后到
    "INPUT_HASH_MISMATCH": False,     # 确定性失败，重投结果相同
    "INPUT_TOO_LARGE": False,         # 输入不会自己变小
    "OUTPUT_UPLOAD_FAILED": True,     # 网络/权限，可重试
    "TIMEOUT": True,                  # 可能是机器抖动
    "TUNABLE_CORE_NOT_AVAILABLE": False,  # 能力不存在，不是故障
    "CORE_UNAVAILABLE": True,         # Core 未安装/损坏，环境修好可重试
    "STALE_CLAIM_RECLAIMED": True,    # worker 崩溃后的回收
    "INTERNAL_ERROR": True,
}

_SCHEMA_FILENAMES = {
    "job": "cpu_job.0.1.schema.json",
    "result": "cpu_result.0.1.schema.json",
}


class ContractError(ValueError):
    """契约校验失败。``code`` 是稳定错误码，可直接进结果 JSON。"""

    def __init__(self, code: str, message: str, detail: str = ""):
        self.code = code
        self.message = message
        self.detail = detail
        super().__init__(f"{code}: {message}")


def _candidate_schema_dirs():
    """按优先级给出可能的 schema 目录。"""
    env = os.environ.get("MOODIFY_SCHEMA_DIR")
    if env:
        yield env
    here = os.path.dirname(os.path.abspath(__file__))
    # 部署形态：<worker_root>/bin/contract.py + <worker_root>/schemas/cloud/
    yield os.path.join(os.path.dirname(here), "schemas", "cloud")
    # 仓库形态：<repo>/ops/cloud_worker/contract.py + <repo>/schemas/cloud/
    yield os.path.join(os.path.dirname(os.path.dirname(here)), "schemas", "cloud")


def schema_dir() -> str:
    for d in _candidate_schema_dirs():
        if os.path.isfile(os.path.join(d, _SCHEMA_FILENAMES["job"])):
            return d
    tried = "\n  ".join(_candidate_schema_dirs())
    raise ContractError(
        "SCHEMA_INVALID",
        "找不到契约 schema 文件",
        f"已尝试：\n  {tried}\n可用 MOODIFY_SCHEMA_DIR 覆盖。",
    )


_CACHE: Dict[str, Any] = {}


def load_schema(kind: str) -> Dict[str, Any]:
    """加载并缓存 schema。kind ∈ {"job", "result"}。"""
    if kind not in _SCHEMA_FILENAMES:
        raise ValueError(f"未知 schema kind: {kind!r}")
    if kind not in _CACHE:
        path = os.path.join(schema_dir(), _SCHEMA_FILENAMES[kind])
        with open(path, "r", encoding="utf-8") as f:
            _CACHE[kind] = json.load(f)
    return _CACHE[kind]


def _validator_for(kind: str):
    return jsonschema.Draft202012Validator(
        load_schema(kind), format_checker=jsonschema.FormatChecker()
    )


# ------------------------------------------------------------------ 任务侧


def apply_job_defaults(job: Dict[str, Any]) -> Dict[str, Any]:
    """补齐任务的可选字段默认值。返回新 dict，不改原对象。

    只补齐**生产者省略**的字段；已给出的值一律原样保留（是否合法交给校验）。
    """
    out = dict(job)
    out.setdefault("core_version", "resolved-at-runtime")
    out.setdefault("params", {})
    limits = dict(out.get("limits") or {})
    limits.setdefault("timeout_seconds", DEFAULT_TIMEOUT_SECONDS)
    limits.setdefault("max_input_bytes", DEFAULT_MAX_INPUT_BYTES)
    out["limits"] = limits
    return out


def validate_job(job: Dict[str, Any]) -> Dict[str, Any]:
    """校验任务 JSON 并补齐默认值。返回可安全投递给 adapter 的副本。

    失败抛 :class:`ContractError`，``code`` 为 ``SCHEMA_INVALID``（含未知 job_type）。
    """
    if not isinstance(job, dict):
        raise ContractError("SCHEMA_INVALID", f"任务必须是 JSON 对象，收到 {type(job).__name__}")

    errors = sorted(_validator_for("job").iter_errors(job), key=lambda e: list(e.absolute_path))
    if errors:
        # job_type 非法时给稳定且更可操作的错误码，便于队列侧分类
        for e in errors:
            if list(e.absolute_path) == ["job_type"]:
                raise ContractError(
                    "UNKNOWN_JOB_TYPE",
                    f"未知 job_type: {job.get('job_type')!r}",
                    f"支持：{', '.join(JOB_TYPES)}",
                )
        first = errors[0]
        where = "/".join(str(p) for p in first.absolute_path) or "<root>"
        raise ContractError("SCHEMA_INVALID", f"字段 {where} 不合法：{first.message}")

    return apply_job_defaults(job)


# ------------------------------------------------------------------ 结果侧


def retryable_for(code: str) -> bool:
    """错误码 → 可重试性。未知码保守判为可重试（宁可重投一次，不可静默丢失）。"""
    return RETRYABLE_BY_CODE.get(code, True)


def utc_now() -> str:
    """ISO-8601 UTC 时间戳，秒精度。"""
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def build_result(
    *,
    job: Dict[str, Any],
    worker_id: str,
    status: str,
    attempt: int = 1,
    started_at: str,
    finished_at: Optional[str] = None,
    input_sha256: str = NOT_ALIGNABLE,
    outputs: Optional[list] = None,
    evidence: Optional[list] = None,
    params: Optional[Dict[str, Any]] = None,
    cpu_seconds: Any = NOT_ALIGNABLE,
    peak_memory_bytes: Any = NOT_ALIGNABLE,
    core_version: str = NOT_ALIGNABLE,
    tool_versions: Optional[Dict[str, str]] = None,
    error: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """构造结果 JSON。``duration_seconds`` 由起止时间算出，不接受外部传入。"""
    finished_at = finished_at or utc_now()
    duration = _seconds_between(started_at, finished_at)

    if status == STATUS_FAILED and error is None:
        raise ValueError("status=FAILED 必须给 error")
    if status != STATUS_FAILED and error is not None:
        raise ValueError(f"status={status} 不应带 error")

    result: Dict[str, Any] = {
        "schema_version": RESULT_SCHEMA_VERSION,
        "status": status,
        "job_id": job["job_id"],
        "request_id": job["request_id"],
        "job_type": job["job_type"],
        "worker_id": worker_id,
        "attempt": attempt,
        "input": dict(job["input"]),
        "input_sha256": input_sha256,
        "outputs": outputs or [],
        "evidence": evidence or [],
        "started_at": started_at,
        "finished_at": finished_at,
        "duration_seconds": duration,
        "cpu_seconds": cpu_seconds,
        "peak_memory_bytes": peak_memory_bytes,
        "core_version": core_version,
        "tool_versions": tool_versions or {},
        "params": params if params is not None else dict(job.get("params") or {}),
        "limits_applied": dict(job.get("limits") or {}),
        "retryable": bool(error["retryable"]) if error else False,
        "error": error,
    }
    validate_result(result)
    return result


def build_error(code: str, message: str, detail: str = "") -> Dict[str, Any]:
    """按错误码构造 error 对象，可重试性由 :func:`retryable_for` 决定。"""
    return {
        "code": code,
        "message": message,
        "detail": detail,
        "retryable": retryable_for(code),
    }


# ------------------------------------------------- 契约语义（纯函数，I/O 留在 worker）

def check_input_size(declared_bytes: int, limits: Dict[str, Any]) -> None:
    """下载前用 HeadObject 的 ContentLength 预检。超限抛 INPUT_TOO_LARGE。

    预检的目的不是省事，是**不把一个注定失败的 2 GiB 拉下来**。
    """
    cap = int((limits or {}).get("max_input_bytes", DEFAULT_MAX_INPUT_BYTES))
    if declared_bytes > cap:
        raise ContractError(
            "INPUT_TOO_LARGE",
            f"输入 {declared_bytes} 字节超过上限 {cap} 字节",
            "如需处理，请提高任务 limits.max_input_bytes（上限 10 GiB）后重新投递。",
        )


def check_input_hash(expected: str, actual: str) -> None:
    """比对生产者声明的 sha256 与 worker 实测值。不符抛 INPUT_HASH_MISMATCH。"""
    if expected != actual:
        raise ContractError(
            "INPUT_HASH_MISMATCH",
            "输入对象 sha256 与任务声明不符",
            f"声明={expected} 实测={actual}。对象已被改动或任务投错了键。",
        )


def resolve_idempotency(
    request_id: str,
    existing: Optional[Dict[str, Any]],
) -> Optional[Dict[str, Any]]:
    """幂等裁决：同一 request_id 已产出权威结果时，返回既有结果，不重复执行。

    ``existing`` 为已登记的终态结果（DONE/FAILED/INCONCLUSIVE/HUMAN_REQUIRED），
    无记录则为 None。返回非 None 即调用方**必须**直接回既有结果并跳过执行。

    只有终态才登记；进行中的任务不在此列——重投同一 request_id 时由 claim 竞争
    决定谁执行，输的一方回既有结果。（重试用新的 request_id，见 §5 重试语义。）
    """
    if existing is None:
        return None
    if existing.get("request_id") != request_id:
        raise ContractError(
            "INTERNAL_ERROR",
            "幂等索引错配",
            f"索引键 {request_id} 下登记的是 {existing.get('request_id')!r}",
        )
    return existing


def validate_result(result: Dict[str, Any]) -> None:
    """校验结果 JSON。失败抛 :class:`ContractError`（code=SCHEMA_INVALID）。

    结果是自己写出来的，校验失败属于 worker 自身的 bug —— 必须炸，不得静默上传。
    """
    errors = sorted(
        _validator_for("result").iter_errors(result), key=lambda e: list(e.absolute_path)
    )
    if errors:
        first = errors[0]
        where = "/".join(str(p) for p in first.absolute_path) or "<root>"
        raise ContractError("SCHEMA_INVALID", f"结果字段 {where} 不合法：{first.message}")


def _seconds_between(started_at: str, finished_at: str) -> float:
    a = datetime.fromisoformat(started_at.replace("Z", "+00:00"))
    b = datetime.fromisoformat(finished_at.replace("Z", "+00:00"))
    return round(max(0.0, (b - a).total_seconds()), 3)
