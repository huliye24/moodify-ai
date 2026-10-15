"""W2 验收：worker 端到端 —— 投递、幂等、失败分类、崩溃恢复、清理。

全程用内存 S3；Core 用一个可控的替身（真实 Core 在 W3 的节点冒烟里验）。
"""

import time

import pytest

import contract
import s3queue
import worker
from helpers import make_job, read_json, seed_input, sha256_hex, submit

WID = "worker-test"
AUDIO = b"RIFF....fake wav bytes for testing"


@pytest.fixture
def ready(fake_s3, work_root):
    """放好输入文件，返回 (fake_s3, key, sha256)。"""
    key = seed_input(fake_s3, AUDIO)
    return fake_s3, key, sha256_hex(AUDIO)


def _done(fake_s3, job_id):
    return read_json(fake_s3, s3queue.QUEUE_BUCKET, f"{s3queue.PREFIX_DONE}{job_id}.json")


def _failed(fake_s3, job_id):
    return read_json(fake_s3, s3queue.QUEUE_BUCKET, f"{s3queue.PREFIX_FAILED}{job_id}.json")


# ------------------------------------------------------------- 成功路径

def test_smoke_job_round_trip(ready):
    fake, key, digest = ready
    job = make_job(key=key, sha256=digest)
    submit(fake, job)

    assert worker.process_one(WID) is True

    result = _done(fake, job["job_id"])
    contract.validate_result(result)
    assert result["status"] == "done"
    assert result["input_sha256"] == digest
    assert fake.keys(s3queue.QUEUE_BUCKET, s3queue.PREFIX_CLAIMED) == []
    assert [o["key"] for o in result["outputs"]] == [
        f"results/{job['job_id']}/smoke.json"
    ]
    assert result["outputs"][0]["sha256"], "输出哈希必须实测填写"
    assert result["duration_seconds"] >= 0


def test_source_object_is_never_touched(ready):
    """输入对象全程只读 —— 方案 §3.2 明令禁止覆盖源文件。"""
    fake, key, digest = ready
    job = make_job(key=key, sha256=digest)
    submit(fake, job)

    worker.process_one(WID)

    assert fake.get(s3queue.INPUT_BUCKET, key) == AUDIO
    assert not any(c.startswith("delete:raw/") for c in fake.calls)
    assert not any(c.startswith("put:raw/") for c in fake.calls)


def test_work_dir_is_cleaned_after_success(ready, work_root):
    """结果先上传后清理：S3 是数据面，本地不留成功产物。"""
    fake, key, digest = ready
    job = make_job(key=key, sha256=digest)
    submit(fake, job)

    worker.process_one(WID)

    assert not (work_root / job["job_id"]).exists()


def test_empty_queue_reports_no_work(fake_s3, work_root):
    assert worker.process_one(WID) is False


def test_drain_processes_up_to_limit(ready):
    fake, key, digest = ready
    for i in range(3):
        submit(fake, make_job(job_id=f"job-{i}", request_id=f"req-{i}", key=key, sha256=digest))

    assert worker.drain(WID, 2) == 2
    assert len(fake.keys(s3queue.QUEUE_BUCKET, s3queue.PREFIX_DONE)) == 2
    assert len(fake.keys(s3queue.QUEUE_BUCKET, s3queue.PREFIX_PENDING)) == 1


# ------------------------------------------------------------- 幂等

def test_same_job_id_resubmission_does_not_reexecute(ready):
    fake, key, digest = ready
    job = make_job(key=key, sha256=digest)
    submit(fake, job)
    worker.process_one(WID)
    first = _done(fake, job["job_id"])

    submit(fake, job)  # 同 request_id、同 job_id 再投一次
    assert worker.process_one(WID) is True

    assert _done(fake, job["job_id"]) == first, "结果必须逐字不变，不能重算"
    assert fake.keys(s3queue.QUEUE_BUCKET, s3queue.PREFIX_CLAIMED) == []


def test_new_job_id_same_request_gets_alias_not_reexecution(ready):
    """换了 job_id 的重投：不重复执行，但要在它自己的键下给得出答案。"""
    fake, key, digest = ready
    first = make_job(job_id="aaaa", request_id="req-shared", key=key, sha256=digest)
    submit(fake, first)
    worker.process_one(WID)

    fake.calls.clear()
    second = make_job(job_id="bbbb", request_id="req-shared", key=key, sha256=digest)
    submit(fake, second)
    worker.process_one(WID)

    alias = _done(fake, "bbbb")
    assert alias["outcome"] == contract.OUTCOME_ALREADY_COMPLETED
    assert alias["deduplicated_from"] == "aaaa"
    assert alias["job_id"] == "bbbb", "别名挂在**本 job_id** 上，生产者才找得到"
    assert not any("upload:" in c for c in fake.calls), "不得重复执行 = 不得重复上传产物"
    assert fake.keys(s3queue.QUEUE_BUCKET, "results/bbbb/") == []


def test_authoritative_result_is_not_overwritten_by_a_replay(ready):
    """权威结果的口径不因多了一次重投而改变。"""
    fake, key, digest = ready
    first = make_job(job_id="aaaa", request_id="req-shared", key=key, sha256=digest)
    submit(fake, first)
    worker.process_one(WID)
    authoritative_before = _done(fake, "aaaa")

    second = make_job(job_id="bbbb", request_id="req-shared", key=key, sha256=digest)
    submit(fake, second)
    worker.process_one(WID)

    assert _done(fake, "aaaa") == authoritative_before, "原 job_id 下的权威结果逐字不变"


# ------------------------------------------------------------- 失败分类

def test_input_hash_mismatch_fails_before_any_processing(ready):
    fake, key, _digest = ready
    job = make_job(key=key, sha256="b" * 64)  # 故意声明错的哈希
    submit(fake, job)

    worker.process_one(WID)

    result = _failed(fake, job["job_id"])
    assert result["status"] == "failed"
    assert result["error"]["code"] == "INPUT_HASH_MISMATCH"
    assert result["retryable"] is False
    assert result["input_sha256"] == sha256_hex(AUDIO), "失败也要留下实测哈希"
    assert fake.keys(s3queue.QUEUE_BUCKET, s3queue.PREFIX_DONE) == []


def test_missing_input_fails_with_actionable_code(fake_s3, work_root):
    job = make_job(key="raw/non-ai/fixtures/absent.wav", sha256="c" * 64)
    submit(fake_s3, job)

    worker.process_one(WID)

    result = _failed(fake_s3, job["job_id"])
    assert result["error"]["code"] == "INPUT_NOT_FOUND"
    assert result["retryable"] is True, "对象可能后到，值得重投"


def test_over_limit_input_rejected_without_downloading(fake_s3, work_root):
    """预检的意义就是不把注定失败的几 GB 拉下来。"""
    key = seed_input(fake_s3, AUDIO)
    job = make_job(
        key=key, sha256=sha256_hex(AUDIO), limits={"max_input_bytes": 4, "timeout_seconds": 60}
    )
    submit(fake_s3, job)
    fake_s3.calls.clear()

    worker.process_one(WID)

    result = _failed(fake_s3, job["job_id"])
    assert result["error"]["code"] == "INPUT_TOO_LARGE"
    assert not any(c.startswith("download:") for c in fake_s3.calls)


def test_invalid_job_gets_rejection_slip_not_a_fake_result(fake_s3, work_root):
    """对象根本不是合法任务时，写退件单 —— 不套用结果契约伪造一份像结果的东西。"""
    job = make_job(job_type="demucs")
    submit(fake_s3, job)

    worker.process_one(WID)

    slip = _failed(fake_s3, job["job_id"])
    assert slip["schema_version"] == contract.REJECT_SCHEMA_VERSION
    assert slip["status"] == "REJECTED"
    assert slip["error"]["code"] == "UNKNOWN_JOB_TYPE"
    assert slip["raw_job"]["job_type"] == "demucs"
    assert fake_s3.keys(s3queue.QUEUE_BUCKET, s3queue.PREFIX_DONE) == []


def test_smoke_fail_mode_exercises_the_failure_path(ready):
    """失败路径要能主动演习，不能只靠推理认为它存在。"""
    fake, key, digest = ready
    job = make_job(key=key, sha256=digest, params={"mode": "fail", "fail_with": "TIMEOUT"})
    submit(fake, job)

    worker.process_one(WID)

    result = _failed(fake, job["job_id"])
    assert result["error"]["code"] == "TIMEOUT"
    assert result["retryable"] is True


# ------------------------------------------------------------- 重试

def test_retryable_failure_is_requeued_not_recorded_as_authoritative(ready):
    fake, key, digest = ready
    job = make_job(
        key=key, sha256=digest, params={"mode": "fail", "fail_with": "TIMEOUT"}
    )
    submit(fake, job)
    worker.process_one(WID)

    pending = read_json(
        fake, s3queue.QUEUE_BUCKET, f"{s3queue.PREFIX_PENDING}{job['job_id']}.json"
    )
    assert pending["attempt"] == 2
    assert fake.keys(s3queue.QUEUE_BUCKET, s3queue.PREFIX_IDEM) == [], (
        "中间失败登记索引会把一次抖动变成永久结论，重试再也跑不到"
    )


def test_non_retryable_failure_is_terminal(ready):
    fake, key, digest = ready
    job = make_job(
        key=key, sha256=digest, params={"mode": "fail", "fail_with": "INPUT_TOO_LARGE"}
    )
    submit(fake, job)
    worker.process_one(WID)

    assert fake.keys(s3queue.QUEUE_BUCKET, s3queue.PREFIX_PENDING) == []
    result = _failed(fake, job["job_id"])
    assert result["retryable"] is False
    assert len(fake.keys(s3queue.QUEUE_BUCKET, s3queue.PREFIX_IDEM)) == 1


def test_retry_stops_at_max_attempts(ready):
    """坏任务不能 crash loop：用满尝试次数后转终态。"""
    fake, key, digest = ready
    job = make_job(key=key, sha256=digest, params={"mode": "fail", "fail_with": "TIMEOUT"})
    job["attempt"] = s3queue.MAX_ATTEMPTS
    submit(fake, job)

    worker.process_one(WID)

    assert fake.keys(s3queue.QUEUE_BUCKET, s3queue.PREFIX_PENDING) == []
    assert len(fake.keys(s3queue.QUEUE_BUCKET, s3queue.PREFIX_IDEM)) == 1


# ------------------------------------------------------------- 崩溃恢复

def test_stale_claim_is_reclaimed_and_then_processed(ready):
    """worker 崩溃留下的僵死 claimed 必须能被捞回来跑完。"""
    fake, key, digest = ready
    job = make_job(key=key, sha256=digest)
    submit(fake, job)
    stale = s3queue.claim(job["job_id"], "worker-that-died")
    stale["claimed_at"] = time.time() - 7200
    s3queue.write_json(s3queue.PREFIX_CLAIMED + f"{job['job_id']}.json", stale)

    assert s3queue.reclaim_stale(WID, timeout_sec=3600) == [job["job_id"]]
    assert worker.process_one(WID) is True

    result = _done(fake, job["job_id"])
    assert result["status"] == "done"
    assert result["attempt"] == 2, "恢复后重跑算第 2 次尝试"


def test_failed_dir_is_kept_then_swept(ready, work_root):
    """失败目录留 24 小时供诊断，之后自动清理。"""
    fake, key, digest = ready
    job = make_job(key=key, sha256="d" * 64)
    submit(fake, job)
    worker.process_one(WID)

    job_dir = work_root / job["job_id"]
    assert job_dir.exists(), "失败现场要留下来供诊断"

    old = time.time() - 90_000
    import os

    os.utime(job_dir, (old, old))
    assert worker.sweep_failed_dirs(retention_sec=3600) == 1
    assert not job_dir.exists()


# ------------------------------------------------------------- 产物上传失败

def test_upload_failure_is_classified_and_not_silently_done(ready):
    from botocore.exceptions import ClientError

    fake, key, digest = ready
    job = make_job(key=key, sha256=digest)
    submit(fake, job)
    fake.fail_on["upload_file"] = ClientError(
        {"Error": {"Code": "AccessDenied", "Message": "nope"}}, "PutObject"
    )

    worker.process_one(WID)

    result = _failed(fake, job["job_id"])
    assert result["error"]["code"] == "OUTPUT_UPLOAD_FAILED"
    assert fake.keys(s3queue.QUEUE_BUCKET, s3queue.PREFIX_DONE) == []


# ------------------------------------------------------------- media_probe（不碰 Core）

def test_media_probe_job_runs_without_core(ready, monkeypatch):
    """media_probe 属于 W3A：没有 Core 也必须能跑完。"""
    from adapters import media_probe

    fake, key, digest = ready
    monkeypatch.setattr(media_probe, "probe_media", lambda path, timeout: CANNED_FFPROBE)

    job = make_job(job_type="media_probe", key=key, sha256=digest)
    submit(fake, job)
    worker.process_one(WID)

    result = _done(fake, job["job_id"])
    assert result["status"] == "done"
    assert result["core_version"] == "not_alignable", "不碰 Core 就照实写不可对齐"
    assert [o["key"] for o in result["outputs"]] == [
        f"results/{job['job_id']}/media_probe.json"
    ]


class NoCoreRunner:
    """显式模拟「这台机器没装 Core」。

    不用环境里碰巧有没有 Core 来决定测试结果 —— 本机确实装了一份 editable 的 Core
    （指向另一个 worktree），依赖它会变成在测另一棵树。
    """

    def version(self):
        return "not_alignable"

    def call(self, *args, **kwargs):
        raise AssertionError("Core 不在时不该被调用")


def test_analyze_fails_with_core_not_available_and_leaves_no_artifact(ready, monkeypatch):
    """analyze 需要 Core；Core 不在时必须 CORE_NOT_AVAILABLE，且**不留假产物**。"""
    fake, key, digest = ready
    monkeypatch.setattr(worker, "_make_core_runner", lambda: NoCoreRunner())

    job = make_job(job_type="analyze", key=key, sha256=digest)
    submit(fake, job)
    fake.calls.clear()

    worker.process_one(WID)

    result = _failed(fake, job["job_id"])
    assert result["error"]["code"] == "CORE_NOT_AVAILABLE"
    assert result["retryable"] is True, "装上 Core 就能重试"
    assert result["outputs"] == []
    assert fake.keys(s3queue.QUEUE_BUCKET, f"results/{job['job_id']}/") == []
    assert not any(c.startswith("download:") for c in fake.calls), (
        "Core 不在就不该先把大文件拉下来"
    )


def test_judge_before_also_requires_core(ready, monkeypatch):
    fake, key, digest = ready
    monkeypatch.setattr(worker, "_make_core_runner", lambda: NoCoreRunner())

    job = make_job(job_type="judge_before", key=key, sha256=digest)
    submit(fake, job)
    worker.process_one(WID)

    result = _failed(fake, job["job_id"])
    assert result["error"]["code"] == "CORE_NOT_AVAILABLE"
    assert result["outputs"] == []


CANNED_FFPROBE = {
    "format": {"format_name": "wav", "duration": "1.000000", "size": "176444"},
    "streams": [
        {
            "codec_type": "audio",
            "codec_name": "pcm_s16le",
            "sample_rate": "44100",
            "channels": 1,
            "channel_layout": "mono",
            "bits_per_sample": 16,
        }
    ],
}


# ------------------------------------------------------------- 退避与尝试上限

def test_backoff_gated_job_is_not_claimed_yet(ready):
    """退避期未到的任务不该被领走 —— 否则退避等于没有。"""
    fake, key, digest = ready
    job = make_job(key=key, sha256=digest)
    job["not_before"] = time.time() + 300
    submit(fake, job)

    assert worker.process_one(WID) is False, "还在退避期，本轮应当什么都不做"
    assert len(fake.keys(s3queue.QUEUE_BUCKET, s3queue.PREFIX_PENDING)) == 1
    assert fake.keys(s3queue.QUEUE_BUCKET, s3queue.PREFIX_CLAIMED) == []


def test_backoff_expired_job_is_claimed(ready):
    fake, key, digest = ready
    job = make_job(key=key, sha256=digest)
    job["not_before"] = time.time() - 1
    submit(fake, job)

    assert worker.process_one(WID) is True
    assert _done(fake, job["job_id"])["status"] == "done"


def test_retryable_failure_schedules_backoff(ready):
    fake, key, digest = ready
    job = make_job(key=key, sha256=digest, params={"mode": "fail", "fail_with": "TIMEOUT"})
    submit(fake, job)
    before = time.time()

    worker.process_one(WID)

    pending = read_json(
        fake, s3queue.QUEUE_BUCKET, f"{s3queue.PREFIX_PENDING}{job['job_id']}.json"
    )
    assert pending["not_before"] >= before + s3queue.RETRY_BASE_SEC


def test_exhausted_attempts_are_terminated_with_a_contract_result(ready):
    """尝试次数用满后**判死**，且判死写的是一份契约合法的结果，不是原始 job。

    这条挡的是「能让 worker 崩溃的任务」：那种任务每次都在递增 attempt 之前把进程带走，
    只有领取时判死才拦得住无限重跑。
    """
    fake, key, digest = ready
    job = make_job(key=key, sha256=digest)
    job["attempt"] = s3queue.MAX_ATTEMPTS + 1
    submit(fake, job)
    fake.calls.clear()

    worker.process_one(WID)

    result = _failed(fake, job["job_id"])
    contract.validate_result(result)  # 判死也必须产出契约合法的结果，否则它就不是结果
    assert result["status"] == "failed"
    assert result["error"]["code"] == "RETRY_EXHAUSTED"
    assert result["retryable"] is False
    assert result["outputs"] == []
    assert not any(c.startswith("download:") for c in fake.calls), "判死不该先下载输入"
    assert fake.keys(s3queue.QUEUE_BUCKET, s3queue.PREFIX_PENDING) == [], "不得再放回队列"


def test_exhausted_job_does_not_loop_forever(ready):
    """端到端证明它真的会停：回收推进 attempt，跑满之后终止。"""
    fake, key, digest = ready
    job = make_job(key=key, sha256=digest, params={"mode": "fail", "fail_with": "TIMEOUT"})
    submit(fake, job)

    for _ in range(s3queue.MAX_ATTEMPTS):
        # 每轮把退避期抹掉，模拟时间流逝
        peeked = s3queue.peek_pending(job["job_id"])
        if peeked is not None:
            peeked.pop("not_before", None)
            s3queue.write_json(
                f"{s3queue.PREFIX_PENDING}{job['job_id']}.json", peeked
            )
        elif fake.get(
            s3queue.QUEUE_BUCKET, f"{s3queue.PREFIX_FAILED}{job['job_id']}.json"
        ):
            break
        worker.process_one(WID)

    result = _failed(fake, job["job_id"])
    assert result["error"]["code"] == "TIMEOUT", "前几次走正常重试路径"
    assert fake.keys(s3queue.QUEUE_BUCKET, s3queue.PREFIX_PENDING) == [], "最终必须停下来"
    assert len(fake.keys(s3queue.QUEUE_BUCKET, s3queue.PREFIX_IDEM)) == 1
