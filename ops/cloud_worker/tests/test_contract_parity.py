"""Schema ↔ Python 一致性。

裁决（2026-10-15）：**JSON Schema 是唯一契约权威**，`CI 必须检测 Schema 与 Python 常量是否漂移`。

本模块分两层：
1. **结构层**：常量从 schema 派生，漂移在构造上不可能（`contract.py` import 时读枚举）。
   这里断言派生确实发生了、且各集合自洽。
2. **用法层**：扫描源码，确认没有任何模块**绕开契约**自己写状态字面量或错误码。
   这一层才是真正会抓到回归的 —— 派生只能保证常量对，管不住有人手写 `"DONE"`。

另附「旧大写状态被拒绝」用例：裁决明确本次**不做兼容迁移层**（当前无生产任务）。
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

import contract
from adapters.base import ROLES

_WORKER_ROOT = Path(__file__).resolve().parent.parent

#: 会被扫描「有没有绕开契约写状态/错误码」的源码。
_SCANNED = [
    _WORKER_ROOT / "worker.py",
    _WORKER_ROOT / "lib" / "s3queue.py",
    *_WORKER_ROOT.joinpath("adapters").glob("*.py"),
]

_STATUS_TOKENS = (
    "pending", "claimed", "done", "failed", "inconclusive", "human_required",
    "PENDING", "CLAIMED", "DONE", "FAILED", "INCONCLUSIVE", "HUMAN_REQUIRED",
)
_STATUS_LITERAL_RE = re.compile(r"""["'](%s)["']""" % "|".join(_STATUS_TOKENS))

_ERROR_CODE_CALL_RE = re.compile(r"""(?:AdapterError|ContractError)\(\s*["']([A-Z_]{4,})["']""")

#: 允许出现的大写状态字面量：Core 的 `workflow_decision` 词汇表是 **Core 的**，不是我们的。
#: 必须是「映射键 → 契约状态常量」这种形态，也就是只在做翻译，不是在写状态。
_CORE_DECISION_KEY_RE = re.compile(r"""^\s*["'](?:INCONCLUSIVE|PASS_TO_LISTENING|REJECT_TECHNICAL)["']\s*:\s*STATUS_""")


# ------------------------------------------------------------ 结构层

def test_job_types_come_from_schema():
    schema = contract.load_schema("job")
    assert contract.JOB_TYPES == tuple(schema["properties"]["job_type"]["enum"])
    assert contract.JOB_TYPES, "派生结果不能是空的 —— 那说明 schema 没被读到"


def test_lifecycle_values_come_from_schema():
    schema = contract.load_schema("result")
    assert contract.LIFECYCLE_STATES == tuple(schema["$defs"]["lifecycle_state"]["enum"])
    assert contract.TERMINAL_STATES == tuple(schema["$defs"]["terminal_state"]["enum"])


def test_error_codes_come_from_schema():
    schema = contract.load_schema("result")
    assert contract.ERROR_CODES == tuple(schema["$defs"]["error_code"]["enum"])


def test_retryable_map_covers_every_error_code():
    """少一个键 → 某个错误码的可重试性会落到「未知码默认 True」的兜底上，静默走样。"""
    assert set(contract.RETRYABLE_BY_CODE) == set(contract.ERROR_CODES)


def test_terminal_states_are_a_subset_of_lifecycle():
    assert set(contract.TERMINAL_STATES) < set(contract.LIFECYCLE_STATES)
    assert set(contract.LIFECYCLE_STATES) - set(contract.TERMINAL_STATES) == {
        contract.STATUS_PENDING,
        contract.STATUS_CLAIMED,
    }, "生命周期里除四个终态外，只应剩队列位置"


def test_queue_prefix_mapping_covers_every_terminal_state():
    assert set(contract.QUEUE_PREFIX_BY_TERMINAL) == set(contract.TERMINAL_STATES)


def test_artifact_roles_match_schema_enum():
    schema = contract.load_schema("result")
    enum = schema["properties"]["outputs"]["items"]["properties"]["role"]["enum"]
    assert tuple(ROLES) == tuple(enum)


def test_outcome_values_match_schema_enum():
    schema = contract.load_schema("result")
    enum = schema["properties"]["outcome"]["enum"]
    assert (contract.OUTCOME_EXECUTED, contract.OUTCOME_ALREADY_COMPLETED) == tuple(enum)


def test_schema_fingerprint_is_stable_and_reported():
    """W4 的 Studio 按这个指纹对齐版本；它必须稳定且可复算。"""
    first = contract.schema_fingerprint()
    second = contract.schema_fingerprint()
    assert first == second
    assert len(first) == 64 and all(c in "0123456789abcdef" for c in first)


# ------------------------------------------------------------ 用法层：源码扫描

def test_adapter_error_codes_are_all_declared_in_the_contract():
    """adapter 抛的错误码必须都在契约里 —— 否则 Studio 收到一个它不认识的码。"""
    undeclared = []
    for path in _SCANNED:
        text = path.read_text(encoding="utf-8")
        for code in _ERROR_CODE_CALL_RE.findall(text):
            if code not in contract.ERROR_CODES:
                undeclared.append(f"{path.name}: {code}")
    assert not undeclared, f"这些错误码不在契约里：{undeclared}"


def test_no_uppercase_or_foreign_status_literals_in_source():
    """源码里不得出现契约之外的状态字面量，尤其不得有旧的大写写法。"""
    offenders = []
    for path in _SCANNED:
        for lineno, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            for token in _STATUS_LITERAL_RE.findall(line):
                if token in contract.TERMINAL_STATES:
                    continue  # 小写终态，契约内
                if _CORE_DECISION_KEY_RE.match(line) and token == "INCONCLUSIVE":
                    continue  # Core 的判定词汇表，在做翻译而非写状态
                offenders.append(f"{path.name}:{lineno}: {token!r}")
    assert not offenders, (
        "这些状态字面量绕开了契约（大写是旧词汇表，已废弃）：\n  " + "\n  ".join(offenders)
    )


# ------------------------------------------------------------ 旧大写状态：拒绝

def _job():
    return contract.validate_job(
        {
            "schema_version": contract.JOB_SCHEMA_VERSION,
            "job_id": "11111111-1111-4111-8111-111111111111",
            "request_id": "req-1",
            "job_type": "smoke",
            "input": {"bucket": "moodify-dataset", "key": "k", "sha256": "a" * 64},
            "output_prefix": "results/11111111-1111-4111-8111-111111111111/",
            "created_at": "2026-10-15T10:00:00Z",
        }
    )


@pytest.mark.parametrize("legacy", ["DONE", "FAILED", "INCONCLUSIVE", "HUMAN_REQUIRED"])
def test_legacy_uppercase_status_is_rejected(legacy):
    """旧词汇表在 schema 层就被拒绝。

    裁决明确：当前**没有生产任务**，因此不需要兼容迁移层 —— 这是最后一个低成本冻结窗口。
    """
    result = contract.build_result(
        job=_job(),
        worker_id="w",
        status=contract.STATUS_DONE,
        started_at="2026-10-15T10:00:00Z",
        finished_at="2026-10-15T10:00:01Z",
    )
    result["status"] = legacy

    with pytest.raises(contract.ContractError):
        contract.validate_result(result)


def test_build_result_rejects_non_terminal_status():
    """队列位置（pending / claimed）不是结果状态，不许写进结果。"""
    for queue_state in (contract.STATUS_PENDING, contract.STATUS_CLAIMED):
        with pytest.raises(ValueError, match="不是终态"):
            contract.build_result(
                job=_job(),
                worker_id="w",
                status=queue_state,
                started_at="2026-10-15T10:00:00Z",
            )


def test_unknown_error_code_is_rejected_at_construction():
    """错误码不在契约里时构造就炸，别等到 Studio 收到一个不认识的码。"""
    with pytest.raises(ValueError, match="不在契约的错误码集合"):
        contract.build_error("SOMETHING_NOT_DECLARED", "x")


def test_core_decisions_translate_into_contract_statuses():
    """Core 的判定词汇表 → 我们的终态，映射结果必须全部落在契约里。"""
    from adapters.analyze import DECISION_TO_STATUS

    assert set(DECISION_TO_STATUS.values()) <= set(contract.TERMINAL_STATES)
