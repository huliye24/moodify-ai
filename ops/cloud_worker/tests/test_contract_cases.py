"""W1 验收：契约校验覆盖六类用例。

方案 W1 验收逐条对应：
  ① 合法          test_valid_job_* / test_valid_result_*
  ② 缺字段        test_missing_required_field_*
  ③ 未知 job_type test_unknown_job_type_*
  ④ 重复 request_id test_duplicate_request_id_*
  ⑤ 哈希不符      test_hash_mismatch_*
  ⑥ 超限输入      test_input_too_large_*

另附结果契约的边界用例（not_alignable 的合法位置、FAILED 必须带 error）。
"""

import copy
import json

import pytest

import contract
from contract import ContractError


def _valid_job(**overrides):
    job = {
        "schema_version": contract.JOB_SCHEMA_VERSION,
        "job_id": "b3f1c2d4-0000-4000-8000-000000000001",
        "request_id": "req-smoke-0001",
        "job_type": "probe",
        "input": {
            "bucket": "moodify-dataset",
            "key": "raw/non-ai/fixtures/sine_1s.wav",
            "sha256": "a" * 64,
        },
        "output_prefix": "results/b3f1c2d4-0000-4000-8000-000000000001/",
        "created_at": "2026-10-15T10:00:00Z",
    }
    job.update(overrides)
    return job


# ---------------------------------------------------------------- ① 合法

def test_valid_job_roundtrip_and_defaults():
    """合法任务通过校验，且省略的可选字段被补成 §5 的默认值。"""
    out = contract.validate_job(_valid_job())

    assert out["params"] == {}
    assert out["core_version"] == "resolved-at-runtime"
    assert out["limits"]["timeout_seconds"] == 1800
    assert out["limits"]["max_input_bytes"] == 2147483648


def test_valid_job_does_not_mutate_input():
    """校验不得就地改调用方的对象——worker 还要拿原始 job 做证据。"""
    job = _valid_job()
    before = copy.deepcopy(job)
    contract.validate_job(job)
    assert job == before


def test_valid_job_explicit_limits_win():
    job = _valid_job(limits={"timeout_seconds": 60, "max_input_bytes": 1024})
    out = contract.validate_job(job)
    assert out["limits"] == {"timeout_seconds": 60, "max_input_bytes": 1024}


@pytest.mark.parametrize("job_type", contract.JOB_TYPES)
def test_every_declared_job_type_is_accepted(job_type):
    """契约里列出的六种 job_type 必须都能通过 schema——否则等于写了不能投的类型。"""
    contract.validate_job(_valid_job(job_type=job_type))


def test_valid_result_done_and_failed():
    job = contract.validate_job(_valid_job())

    done = contract.build_result(
        job=job,
        worker_id="w-1",
        status=contract.STATUS_DONE,
        started_at="2026-10-15T10:00:00Z",
        finished_at="2026-10-15T10:00:03Z",
        input_sha256="a" * 64,
    )
    assert done["duration_seconds"] == 3.0
    assert done["error"] is None
    assert done["retryable"] is False
    contract.validate_result(done)

    failed = contract.build_result(
        job=job,
        worker_id="w-1",
        status=contract.STATUS_FAILED,
        started_at="2026-10-15T10:00:00Z",
        finished_at="2026-10-15T10:00:01Z",
        error=contract.build_error("TIMEOUT", "超时"),
    )
    assert failed["error"]["code"] == "TIMEOUT"
    assert failed["retryable"] is True
    contract.validate_result(failed)


# ---------------------------------------------------------------- ② 缺字段

@pytest.mark.parametrize(
    "missing",
    [
        "schema_version",
        "job_id",
        "request_id",
        "job_type",
        "input",
        "output_prefix",
        "created_at",
    ],
)
def test_missing_required_field_is_schema_invalid(missing):
    job = _valid_job()
    del job[missing]

    with pytest.raises(ContractError) as ei:
        contract.validate_job(job)
    assert ei.value.code == "SCHEMA_INVALID"


def test_missing_nested_field_is_schema_invalid():
    job = _valid_job()
    del job["input"]["sha256"]

    with pytest.raises(ContractError) as ei:
        contract.validate_job(job)
    assert ei.value.code == "SCHEMA_INVALID"


def test_unknown_top_level_field_is_rejected():
    """additionalProperties=false：拼错的键必须报错，不能静默忽略。"""
    with pytest.raises(ContractError) as ei:
        contract.validate_job(_valid_job(imput={}))
    assert ei.value.code == "SCHEMA_INVALID"


def test_non_object_job_is_schema_invalid():
    with pytest.raises(ContractError) as ei:
        contract.validate_job(["not", "a", "dict"])
    assert ei.value.code == "SCHEMA_INVALID"


# ---------------------------------------------------------------- ③ 未知 job_type

def test_unknown_job_type_has_its_own_code():
    with pytest.raises(ContractError) as ei:
        contract.validate_job(_valid_job(job_type="demucs"))
    assert ei.value.code == "UNKNOWN_JOB_TYPE"
    assert "demucs" in str(ei.value)


def test_job_type_is_case_sensitive():
    with pytest.raises(ContractError) as ei:
        contract.validate_job(_valid_job(job_type="Probe"))
    assert ei.value.code == "UNKNOWN_JOB_TYPE"


def test_missing_job_type_is_schema_invalid_not_unknown():
    """缺 job_type 是「缺字段」，不是「未知类型」——两者错误码必须分得开。"""
    job = _valid_job()
    del job["job_type"]
    with pytest.raises(ContractError) as ei:
        contract.validate_job(job)
    assert ei.value.code == "SCHEMA_INVALID"


# ---------------------------------------------------------------- ④ 重复 request_id

def test_duplicate_request_id_returns_existing_result():
    """同一 request_id 已产出权威结果 → 直接回既有结果，不重复执行。"""
    job = contract.validate_job(_valid_job())
    existing = contract.build_result(
        job=job,
        worker_id="w-first",
        status=contract.STATUS_DONE,
        started_at="2026-10-15T10:00:00Z",
        finished_at="2026-10-15T10:00:02Z",
        input_sha256="a" * 64,
    )

    got = contract.resolve_idempotency("req-smoke-0001", existing)

    assert got is existing
    assert got["worker_id"] == "w-first", "必须回第一次的权威结果，不得被第二次覆盖"


def test_first_submission_has_no_existing_result():
    assert contract.resolve_idempotency("req-smoke-0001", None) is None


def test_idempotency_index_mismatch_is_internal_error():
    """索引串键属于 worker 自身 bug，必须炸，不得当成命中。"""
    job = contract.validate_job(_valid_job())
    existing = contract.build_result(
        job=job,
        worker_id="w-first",
        status=contract.STATUS_DONE,
        started_at="2026-10-15T10:00:00Z",
        finished_at="2026-10-15T10:00:02Z",
    )
    with pytest.raises(ContractError) as ei:
        contract.resolve_idempotency("req-OTHER", existing)
    assert ei.value.code == "INTERNAL_ERROR"


# ---------------------------------------------------------------- ⑤ 哈希不符

def test_hash_mismatch_detected():
    with pytest.raises(ContractError) as ei:
        contract.check_input_hash("a" * 64, "b" * 64)
    assert ei.value.code == "INPUT_HASH_MISMATCH"
    assert "a" * 64 in ei.value.detail and "b" * 64 in ei.value.detail


def test_hash_match_passes():
    contract.check_input_hash("c" * 64, "c" * 64)


def test_hash_mismatch_is_not_retryable():
    """对象已被改动或投错键，重投结果相同 —— 不可重试。"""
    assert contract.retryable_for("INPUT_HASH_MISMATCH") is False


def test_declared_sha256_must_be_lowercase_hex64():
    """大小写/长度不符在 schema 层就被挡住，不会走到运行时比对。"""
    with pytest.raises(ContractError) as ei:
        contract.validate_job(
            _valid_job(input={"bucket": "b", "key": "k", "sha256": "A" * 64})
        )
    assert ei.value.code == "SCHEMA_INVALID"


# ---------------------------------------------------------------- ⑥ 超限输入

def test_input_too_large_rejected_before_download():
    limits = {"timeout_seconds": 1800, "max_input_bytes": 1024}
    with pytest.raises(ContractError) as ei:
        contract.check_input_size(2048, limits)
    assert ei.value.code == "INPUT_TOO_LARGE"


def test_input_exactly_at_limit_passes():
    """边界：等于上限放行，只有严格超过才拒。"""
    contract.check_input_size(1024, {"max_input_bytes": 1024})


def test_input_too_large_is_not_retryable():
    assert contract.retryable_for("INPUT_TOO_LARGE") is False


def test_limit_above_ceiling_is_schema_invalid():
    """生产者不能靠抬 limits 把 worker 的看门狗关掉。"""
    with pytest.raises(ContractError) as ei:
        contract.validate_job(_valid_job(limits={"timeout_seconds": 999999}))
    assert ei.value.code == "SCHEMA_INVALID"


def test_unknown_limit_key_is_rejected():
    with pytest.raises(ContractError) as ei:
        contract.validate_job(_valid_job(limits={"max_bytes": 10}))
    assert ei.value.code == "SCHEMA_INVALID"


# ------------------------------------------------- 结果契约边界（W1 附则）

def test_not_alignable_is_legal_for_unmeasurable_metrics():
    """测不到的指标必须能合法写 not_alignable —— 否则会逼人补算。"""
    job = contract.validate_job(_valid_job())
    result = contract.build_result(
        job=job,
        worker_id="w-1",
        status=contract.STATUS_DONE,
        started_at="2026-10-15T10:00:00Z",
        finished_at="2026-10-15T10:00:01Z",
        peak_memory_bytes=contract.NOT_ALIGNABLE,
        cpu_seconds=contract.NOT_ALIGNABLE,
        core_version=contract.NOT_ALIGNABLE,
        input_sha256=contract.NOT_ALIGNABLE,
    )
    assert result["peak_memory_bytes"] == "not_alignable"
    assert result["input_sha256"] == "not_alignable"
    contract.validate_result(result)


def test_failed_status_requires_error_object():
    job = contract.validate_job(_valid_job())
    with pytest.raises(ValueError, match="必须给 error"):
        contract.build_result(
            job=job,
            worker_id="w-1",
            status=contract.STATUS_FAILED,
            started_at="2026-10-15T10:00:00Z",
        )


def test_non_failed_status_must_not_carry_error():
    job = contract.validate_job(_valid_job())
    with pytest.raises(ValueError, match="不应带 error"):
        contract.build_result(
            job=job,
            worker_id="w-1",
            status=contract.STATUS_INCONCLUSIVE,
            started_at="2026-10-15T10:00:00Z",
            error=contract.build_error("TIMEOUT", "x"),
        )


def test_inconclusive_and_human_required_are_not_failures():
    """两者是诚实结论，不是失败：retryable=false、无 error。"""
    job = contract.validate_job(_valid_job())
    for status in (contract.STATUS_INCONCLUSIVE, contract.STATUS_HUMAN_REQUIRED):
        result = contract.build_result(
            job=job,
            worker_id="w-1",
            status=status,
            started_at="2026-10-15T10:00:00Z",
            finished_at="2026-10-15T10:00:01Z",
        )
        assert result["retryable"] is False
        assert result["error"] is None
        contract.validate_result(result)


def test_unknown_error_code_defaults_to_retryable():
    """未知错误码保守判可重试：宁可重投一次，不可静默丢失。"""
    assert contract.retryable_for("SOMETHING_NEW") is True


def test_schemas_are_self_consistent_ids():
    job_schema = contract.load_schema("job")
    result_schema = contract.load_schema("result")
    assert job_schema["$id"] == contract.JOB_SCHEMA_VERSION
    assert result_schema["$id"] == contract.RESULT_SCHEMA_VERSION
    # schema 必须能独立序列化（Studio 侧读的是同一份文件）
    json.dumps(job_schema)
