"""W2 验收：adapter 层 —— 映射完整、无 Core 能力时不伪造产物。"""

import pytest

import contract
from adapters import REGISTRY, get_adapter, registry_covers_contract, unimplemented_job_types
from adapters.analyze import status_for_decision
from adapters.base import AdapterContext, AdapterError, Artifact


def test_registry_covers_every_contract_job_type():
    """契约声明的每种 job_type 都必须有人接 —— 否则等于收了任务却没人处理。"""
    assert registry_covers_contract()
    assert set(REGISTRY) == set(contract.JOB_TYPES)


def test_unknown_job_type_has_stable_code():
    with pytest.raises(AdapterError) as ei:
        get_adapter("demucs")
    assert ei.value.code == "UNKNOWN_JOB_TYPE"


def test_manifest_is_declared_unimplemented_not_silently_missing():
    """manifest 是**有意的降级实现**，必须能被自检看见，不能混在已支持里。"""
    assert "manifest" in unimplemented_job_types()


@pytest.mark.parametrize(
    ("decision", "expected"),
    [
        ("PASS_TO_LISTENING", contract.STATUS_HUMAN_REQUIRED),
        ("INCONCLUSIVE", contract.STATUS_INCONCLUSIVE),
        ("REJECT_TECHNICAL", contract.STATUS_DONE),
    ],
)
def test_judgment_mapping_is_translation_not_re_judgment(decision, expected):
    assert status_for_decision(decision) == expected


@pytest.mark.parametrize("decision", [None, "", "SOMETHING_NEW", "pass_to_listening"])
def test_unknown_decision_never_defaults_to_pass(decision):
    """认不出的判定必须保守成 INCONCLUSIVE —— 默认放行是最危险的失败模式。"""
    assert status_for_decision(decision) == contract.STATUS_INCONCLUSIVE


# ------------------------------------------------------------- Artifact 约束

def test_artifact_rejects_escaping_suffix():
    for bad in ("../escape.json", "/abs.json", "", "a/../../b.json"):
        with pytest.raises(ValueError):
            Artifact(path="x", role="report", key_suffix=bad)


def test_artifact_rejects_unknown_role():
    with pytest.raises(ValueError):
        Artifact(path="x", role="definitely-not-a-role", key_suffix="a.json")


def test_artifact_accepts_nested_suffix():
    art = Artifact(path="x", role="evidence", key_suffix="case_1/scan/metrics.json")
    assert art.key_suffix == "case_1/scan/metrics.json"


# ------------------------------------------------------------- adapter 参数

def _valid_job(job_type: str, **extra):
    payload = {
        "schema_version": contract.JOB_SCHEMA_VERSION,
        "job_id": "j1",
        "request_id": "r1",
        "job_type": job_type,
        "input": {"bucket": "moodify-dataset", "key": "k", "sha256": "a" * 64},
        "output_prefix": "results/j1/",
        "created_at": "2026-10-15T10:00:00Z",
    }
    payload.update(extra)
    return contract.validate_job(payload)


def _ctx(tmp_path, job):
    return AdapterContext(
        job=job,
        work_dir=tmp_path,
        input_path=tmp_path / "in.wav",
        out_dir=tmp_path / "out",
        scratch_dir=tmp_path / "scratch",
        core=None,
        timeout_seconds=60,
    )


def test_adapter_rejects_unknown_params(tmp_path):
    """静默忽略未知参数会让生产者以为参数生效了。"""
    from adapters import smoke

    job = _valid_job("smoke", params={"definitely_not_a_param": 1})

    with pytest.raises(AdapterError) as ei:
        smoke.run(_ctx(tmp_path, job))
    assert ei.value.code == "SCHEMA_INVALID"


def test_manifest_adapter_returns_tunable_core_not_available(tmp_path):
    """没有 Core 权威的能力必须稳定失败，且**不留假产物**。"""
    from adapters import manifest

    with pytest.raises(AdapterError) as ei:
        manifest.run(_ctx(tmp_path, _valid_job("manifest")))

    assert ei.value.code == "TUNABLE_CORE_NOT_AVAILABLE"
    assert not (tmp_path / "out").exists(), "失败路径不得产出任何产物"


def test_smoke_adapter_writes_evidence_artifact(tmp_path):
    """smoke 不做音频处理，但必须留下可核对的往返证据。"""
    import json

    from adapters import smoke

    (tmp_path / "in.wav").write_bytes(b"fake-audio")
    ctx = _ctx(tmp_path, _valid_job("smoke", params={"echo": "hello"}))
    ctx.out_dir.mkdir(parents=True, exist_ok=True)

    outcome = smoke.run(ctx)

    assert outcome.status == contract.STATUS_DONE
    assert [a.key_suffix for a in outcome.artifacts] == ["smoke.json"]
    payload = json.loads((tmp_path / "out" / "smoke.json").read_text(encoding="utf-8"))
    assert payload["echo"] == "hello"
    assert payload["input_bytes"] == len(b"fake-audio")
