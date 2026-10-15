"""moodify.cpu-job/0.1 —— 任务契约与结果契约的唯一 Python 实现。

单一权威原则（2026-10-15 裁决）
-------------------------------
契约的权威是 `schemas/cloud/` 下的两份 JSON Schema。**本模块不定义任何枚举常量** ——
`JOB_TYPES` / `LIFECYCLE_STATES` / `TERMINAL_STATES` / `ERROR_CODES` 全部在 import 时
从 schema 里读出。这样「Schema 与 Python 常量漂移」在结构上不可能发生，而不是靠人记得同步。

本模块只做四件事：加载 schema、补默认值、按 schema 校验、把错误码映射成可重试性。

词汇表（两层，不要混）
----------------------
- **状态**：小写生命周期词 `pending / claimed / done / failed / inconclusive / human_required`。
  前两个是队列位置，永远不出现在结果里；结果只允许四个终态。
- **错误码**：稳定的大写机器码（见 :data:`ERROR_CODES`）。Studio 据以决定重试 / 停止 / 要求人工。

任何无法对齐的指标写字符串 :data:`NOT_ALIGNABLE`，不得补算或估填。
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
        "contract.py 需要 jsonschema。请先安装 Core / `pip install jsonschema`。"
    ) from exc

JOB_SCHEMA_VERSION = "moodify.cpu-job/0.1"
RESULT_SCHEMA_VERSION = "moodify.cpu-result/0.1"
REJECT_SCHEMA_VERSION = "moodify.cpu-reject/0.1"

#: 无法对齐的指标的占位符。
NOT_ALIGNABLE = "not_alignable"

DEFAULT_TIMEOUT_SECONDS = 1800
DEFAULT_MAX_INPUT_BYTES = 2147483648  # 2 GiB

#: 队列在传输途中**自己加上去**的字段，不属于生产者写的契约。
#: 契约（schema）描述生产者写什么；这些是 worker 的传输元数据，校验时必须先摘掉，
#: 否则 claim 一加字段任务就变成「非法」了。
RUNTIME_KEYS = (
    "claimed_at",
    "worker_id",
    "attempt",
    "retry_of",
    "last_error",
    "reclaimed_by",
    "not_before",
    "retry_count",
)

_SCHEMA_FILENAMES = {
    "job": "cpu_job.0.1.schema.json",
    "result": "cpu_result.0.1.schema.json",
    "reject": "cpu_reject.0.1.schema.json",
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
    # 部署形态：<worker_root>/contract.py + <worker_root>/schemas/cloud/
    yield os.path.join(here, "schemas", "cloud")
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
    """加载并缓存 schema。kind ∈ {"job", "result", "reject"}。"""
    if kind not in _SCHEMA_FILENAMES:
        raise ValueError(f"未知 schema kind: {kind!r}")
    if kind not in _CACHE:
        path = os.path.join(schema_dir(), _SCHEMA_FILENAMES[kind])
        with open(path, "r", encoding="utf-8") as f:
            _CACHE[kind] = json.load(f)
    return _CACHE[kind]


def schema_fingerprint() -> str:
    """schema 目录的 SHA-256（按文件名排序后拼接内容）。

    W4 的 Studio 按这个指纹对齐版本；schema 一改指纹就变，两侧不可能悄悄用不同版本。
    """
    import hashlib

    h = hashlib.sha256()
    for name in sorted(_SCHEMA_FILENAMES.values()):
        path = os.path.join(schema_dir(), name)
        h.update(name.encode("utf-8"))
        with open(path, "rb") as f:
            h.update(f.read())
    return h.hexdigest()


def _validator_for(kind: str):
    return jsonschema.Draft202012Validator(
        load_schema(kind), format_checker=jsonschema.FormatChecker()
    )


# ------------------------------------------------------------------ 派生常量
# 全部从 schema 读出。**不要在这里手写枚举值** —— 那就是第二份权威。


def _enum_error_codes() -> tuple:
    schema = load_schema("result")
    return tuple(schema["$defs"]["error_code"]["enum"])


def _enum_lifecycle() -> tuple:
    schema = load_schema("result")
    return tuple(schema["$defs"]["lifecycle_state"]["enum"])


def _enum_terminal() -> tuple:
    schema = load_schema("result")
    return tuple(schema["$defs"]["terminal_state"]["enum"])


def _enum_job_types() -> tuple:
    return tuple(load_schema("job")["properties"]["job_type"]["enum"])


JOB_TYPES: tuple = _enum_job_types()
LIFECYCLE_STATES: tuple = _enum_lifecycle()
TERMINAL_STATES: tuple = _enum_terminal()
ERROR_CODES: tuple = _enum_error_codes()

# 队列位置（不是结果状态）
STATUS_PENDING = "pending"
STATUS_CLAIMED = "claimed"
# 终态
STATUS_DONE = "done"
STATUS_FAILED = "failed"
STATUS_INCONCLUSIVE = "inconclusive"
STATUS_HUMAN_REQUIRED = "human_required"

_outcome_enum = tuple(load_schema("result")["properties"]["outcome"]["enum"])
OUTCOME_EXECUTED, OUTCOME_ALREADY_COMPLETED = _outcome_enum

#: 结果放在哪个队列前缀下。inconclusive / human_required 也是**产出了结果**，
#: 与 done 同样落 done/；failed/ 只放「没能产出结果」的那些。
QUEUE_PREFIX_BY_TERMINAL = {
    STATUS_DONE: "done",
    STATUS_INCONCLUSIVE: "done",
    STATUS_HUMAN_REQUIRED: "done",
    STATUS_FAILED: "failed",
}

#: 错误码 → 是否可重试。可重试性由错误码决定，不由调用方随意填写。
RETRYABLE_BY_CODE: Dict[str, bool] = {
    "SCHEMA_INVALID": False,          # 生产者的问题，重投还是坏的
    "UNKNOWN_JOB_TYPE": False,        # 契约不认识，重投无用
    "INPUT_NOT_FOUND": True,          # 对象可能后到
    "INPUT_HASH_MISMATCH": False,     # 确定性失败，重投结果相同
    "INPUT_TOO_LARGE": False,         # 输入不会自己变小
    "OUTPUT_UPLOAD_FAILED": True,     # 网络/权限，可重试
    "TIMEOUT": True,                  # 可能是机器抖动
    "TOOL_FAILED": False,             # 同一输入下外部工具确定性失败
    "CORE_NOT_AVAILABLE": True,       # 环境问题：把 Core 装好就能重试
    "TUNABLE_CORE_NOT_AVAILABLE": False,  # 能力缺口，装什么都不会变出来
    "CORE_JOB_FAILED": False,         # Core 跑了并确定性拒绝
    "RETRY_EXHAUSTED": False,         # 尝试次数用满，重投没有意义
    "INTERNAL_ERROR": True,
}

assert set(RETRYABLE_BY_CODE) == set(ERROR_CODES), (
    "RETRYABLE_BY_CODE 与 schema 的 error_code 枚举不一致："
    f"多 {sorted(set(RETRYABLE_BY_CODE) - set(ERROR_CODES))}，"
    f"少 {sorted(set(ERROR_CODES) - set(RETRYABLE_BY_CODE))}"
)
assert {STATUS_PENDING, STATUS_CLAIMED, STATUS_DONE, STATUS_FAILED,
        STATUS_INCONCLUSIVE, STATUS_HUMAN_REQUIRED} == set(LIFECYCLE_STATES)
assert set(TERMINAL_STATES) == {STATUS_DONE, STATUS_FAILED,
                                STATUS_INCONCLUSIVE, STATUS_HUMAN_REQUIRED}
assert set(QUEUE_PREFIX_BY_TERMINAL) == set(TERMINAL_STATES)


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

    校验前先摘掉 :data:`RUNTIME_KEYS`（队列在传输途中加的元数据），校验后再原样放回 ——
    这样「生产者写错了字段」仍会被 schema 抓住，而 claim 加字段不会把任务变成非法。

    失败抛 :class:`ContractError`，``code`` 为 ``SCHEMA_INVALID``（含未知 job_type）。
    """
    if not isinstance(job, dict):
        raise ContractError("SCHEMA_INVALID", f"任务必须是 JSON 对象，收到 {type(job).__name__}")

    runtime = {k: job[k] for k in RUNTIME_KEYS if k in job}
    payload = {k: v for k, v in job.items() if k not in RUNTIME_KEYS}

    errors = sorted(_validator_for("job").iter_errors(payload), key=lambda e: list(e.absolute_path))
    if errors:
        # job_type 非法时给稳定且更可操作的错误码，便于队列侧分类
        for e in errors:
            if list(e.absolute_path) == ["job_type"]:
                raise ContractError(
                    "UNKNOWN_JOB_TYPE",
                    f"未知 job_type: {payload.get('job_type')!r}",
                    f"支持：{', '.join(JOB_TYPES)}",
                )
        first = errors[0]
        where = "/".join(str(p) for p in first.absolute_path) or "<root>"
        raise ContractError("SCHEMA_INVALID", f"字段 {where} 不合法：{first.message}")

    return {**apply_job_defaults(payload), **runtime}


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
    outcome: str = OUTCOME_EXECUTED,
    deduplicated_from: Optional[str] = None,
) -> Dict[str, Any]:
    """构造结果 JSON。``duration_seconds`` 由起止时间算出，不接受外部传入。"""
    finished_at = finished_at or utc_now()
    duration = _seconds_between(started_at, finished_at)

    if status == STATUS_FAILED and error is None:
        raise ValueError("status=failed 必须给 error")
    if status != STATUS_FAILED and error is not None:
        raise ValueError(f"status={status} 不应带 error")
    if status not in TERMINAL_STATES:
        raise ValueError(f"{status!r} 不是终态；结果只能写 {', '.join(TERMINAL_STATES)}")

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
        "outcome": outcome,
        "deduplicated_from": deduplicated_from,
        "error": error,
    }
    validate_result(result)
    return result


def build_error(code: str, message: str, detail: str = "") -> Dict[str, Any]:
    """按错误码构造 error 对象，可重试性由 :func:`retryable_for` 决定。"""
    if code not in ERROR_CODES:
        raise ValueError(f"{code!r} 不在契约的错误码集合里：{'、'.join(ERROR_CODES)}")
    return {
        "code": code,
        "message": message,
        "detail": detail,
        "retryable": retryable_for(code),
    }


def build_alias(
    *,
    job: Dict[str, Any],
    existing: Dict[str, Any],
    attempt: int = 1,
) -> Dict[str, Any]:
    """把既有权威结果包装成「本 job_id 下的答案」。

    形态与结果契约一致，但 ``outcome=ALREADY_COMPLETED``、``deduplicated_from`` 指回原 job_id，
    且**不改写**原结果的任何字段 —— 权威结果的口径不因多了一次重投而改变。
    """
    alias = dict(existing)
    alias["outcome"] = OUTCOME_ALREADY_COMPLETED
    alias["deduplicated_from"] = str(existing.get("job_id", ""))
    alias["job_id"] = str(job["job_id"])
    alias["request_id"] = str(job["request_id"])
    validate_result(alias)
    return alias


def is_terminal(result: Dict[str, Any], attempt: int, max_attempts: int) -> bool:
    """这份结果是不是**终态**（可以拿来当权威结果作答）。

    终态 = done / inconclusive / human_required，或 failed 且（不可重试 或 已用满尝试次数）。
    可重试的中间失败**不是**终态 —— 否则一次抖动就会被当成最终结论，重试永远跑不到。
    """
    status = result.get("status")
    if status in (STATUS_DONE, STATUS_INCONCLUSIVE, STATUS_HUMAN_REQUIRED):
        return True
    if status != STATUS_FAILED:
        return False
    if not result.get("retryable"):
        return True
    return attempt >= max_attempts


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


def needs_alias(job: Dict[str, Any], existing_result: Dict[str, Any]) -> bool:
    """幂等命中时是否要另写别名：只有**换了 job_id** 才需要。

    同一个 job_id 的重投，答案本来就在它自己的键下，再写一次反而会覆盖权威记录。
    """
    return str(existing_result.get("job_id", "")) != str(job["job_id"])


def resolve_idempotency(
    request_id: str,
    existing: Optional[Dict[str, Any]],
) -> Optional[Dict[str, Any]]:
    """幂等裁决：同一 request_id 已产出权威结果时，返回既有结果，不重复执行。

    ``existing`` 为已登记的终态结果，无记录则为 None。返回非 None 即调用方**必须**
    直接回既有结果并跳过执行。只有终态才登记；进行中的任务不在此列。
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


def build_reject(
    *,
    job_id: str,
    worker_id: str,
    code: str,
    message: str,
    detail: str = "",
    raw_job: Any = None,
) -> Dict[str, Any]:
    """对象根本不是一份合法任务时的退件单（moodify.cpu-reject/0.1）。

    为什么不套用结果契约：结果契约要求 ``job_type`` / ``input`` 等字段可解析，
    而这些字段恰恰就是坏的。硬凑一份「像结果的」对象等于伪造 —— 退件单只说一件事：
    这份东西不是任务，原因是什么。
    """
    if code not in ("SCHEMA_INVALID", "UNKNOWN_JOB_TYPE", "INTERNAL_ERROR"):
        code = "INTERNAL_ERROR"
    slip = {
        "schema_version": REJECT_SCHEMA_VERSION,
        "status": "REJECTED",
        "job_id": str(job_id),
        "worker_id": worker_id,
        "detected_at": utc_now(),
        "error": {"code": code, "message": message, "detail": detail, "retryable": False},
        "raw_job": raw_job if isinstance(raw_job, (dict, list)) else None,
    }
    _validator_for("reject").validate(slip)
    return slip


def _seconds_between(started_at: str, finished_at: str) -> float:
    a = datetime.fromisoformat(started_at.replace("Z", "+00:00"))
    b = datetime.fromisoformat(finished_at.replace("Z", "+00:00"))
    return round(max(0.0, (b - a).total_seconds()), 3)
