"""W2 验收：队列语义 —— 竞争、过期回收、幂等、原子写、重试。

这些是「S3 没有原子 rename」带来的全部边界，必须逐条有名字、有断言，
而不是靠「应该不会发生」蒙过去。
"""

import json
import time

import pytest

import contract
import s3queue
from helpers import make_job, read_json, seed_input, sha256_hex, submit


# ------------------------------------------------------------ claim 的非原子性

def test_claim_order_creates_a_race_window(fake_s3):
    """claim 的动作顺序是 get → put claimed → delete pending，**因此存在竞争窗口**。

    窗口的具体位置：两个 worker 都读完 pending、都写了自己的 claimed 之后，才轮到删除。
    S3 没有原子 rename，这个窗口无法消除，只能靠下游容忍重复执行。断言调用顺序，
    是为了让这个结构事实无法被悄悄改掉而没人发现。
    """
    job = make_job()
    submit(fake_s3, job)
    fake_s3.calls.clear()

    s3queue.claim(job["job_id"], "worker-a")

    assert fake_s3.calls == [
        f"get:{s3queue.PREFIX_PENDING}{job['job_id']}.json",
        f"put:{s3queue.PREFIX_CLAIMED}{job['job_id']}.json",
        f"delete:{s3queue.PREFIX_PENDING}{job['job_id']}.json",
    ], "顺序变了就意味着竞争窗口变了；改动这里必须同时重新论证下游的容忍度"


def test_two_workers_can_both_win_the_same_job(fake_s3):
    """把上一条的窗口**真实复现**：两个 worker 都读到同一份 pending，于是都成功认领。

    这不是 bug，是上面那条顺序的直接后果。下游因此必须容忍同一任务被执行两次
    —— 结果写入的幂等性就是为此存在的。
    """
    job = make_job()
    submit(fake_s3, job)
    pending_key = f"{s3queue.PREFIX_PENDING}{job['job_id']}.json"
    # B 在 A 删 pending 之前读到了同一份内容
    snapshot = fake_s3.get(s3queue.QUEUE_BUCKET, pending_key)

    first = s3queue.claim(job["job_id"], "worker-a")
    fake_s3.seed(s3queue.QUEUE_BUCKET, pending_key, snapshot)  # 还原 B 读到的那一刻
    second = s3queue.claim(job["job_id"], "worker-b")

    assert first is not None and second is not None, "两个 worker 都认为自己拿到了任务"
    assert first["worker_id"] == "worker-a"
    assert second["worker_id"] == "worker-b"


def test_claim_returns_none_when_pending_absent(fake_s3):
    assert s3queue.claim("no-such-job", "worker-a") is None


def test_claim_removes_pending_and_records_metadata(fake_s3):
    job = make_job()
    submit(fake_s3, job)

    claimed = s3queue.claim(job["job_id"], "worker-a")

    assert claimed["worker_id"] == "worker-a"
    assert claimed["attempt"] == 1
    assert fake_s3.keys(s3queue.QUEUE_BUCKET, s3queue.PREFIX_PENDING) == []
    assert fake_s3.keys(s3queue.QUEUE_BUCKET, s3queue.PREFIX_CLAIMED) == [
        f"{s3queue.PREFIX_CLAIMED}{job['job_id']}.json"
    ]


# ------------------------------------------------------------ 过期 claimed 回收

def test_claim_preserves_existing_attempt(fake_s3):
    """claim 不得把 attempt 打回 1。

    回归用例：曾有一版 claim 无条件写 ``attempt = 1``，于是 requeue 的每次递增都被
    抹平，``MAX_ATTEMPTS`` 永远用不满 —— 坏任务会无限重投。
    """
    job = make_job()
    job["attempt"] = 2
    submit(fake_s3, job)

    claimed = s3queue.claim(job["job_id"], "worker-a")

    assert claimed["attempt"] == 2


def test_reclaim_moves_stale_claim_back_to_pending(fake_s3):
    job = make_job()
    submit(fake_s3, job)
    claimed = s3queue.claim(job["job_id"], "worker-a")

    # 把认领时间拨回两小时（超过 1 小时门限）
    claimed["claimed_at"] -= 7200
    s3queue.write_json(s3queue.PREFIX_CLAIMED + f"{job['job_id']}.json", claimed)

    reclaimed = s3queue.reclaim_stale("worker-b", timeout_sec=3600)

    assert reclaimed == [job["job_id"]]
    pending = read_json(fake_s3, s3queue.QUEUE_BUCKET, f"{s3queue.PREFIX_PENDING}{job['job_id']}.json")
    assert pending["attempt"] == 2, "回收必须让 attempt 前进，否则坏任务会无限循环"
    assert "worker_id" not in pending, "回收后要清掉上一个 worker 的印记"
    assert fake_s3.keys(s3queue.QUEUE_BUCKET, s3queue.PREFIX_CLAIMED) == []


def test_reclaim_leaves_fresh_claims_alone(fake_s3):
    """刚认领的任务不能被动 —— 否则回收会把正在跑的任务复制成两份。"""
    job = make_job()
    submit(fake_s3, job)
    s3queue.claim(job["job_id"], "worker-a")

    assert s3queue.reclaim_stale("worker-b", timeout_sec=3600) == []
    assert fake_s3.keys(s3queue.QUEUE_BUCKET, s3queue.PREFIX_PENDING) == []
    assert len(fake_s3.keys(s3queue.QUEUE_BUCKET, s3queue.PREFIX_CLAIMED)) == 1


def test_reclaim_requeues_even_past_max_attempts(fake_s3):
    """回收**总是**把任务放回 pending 并推进 attempt —— 包括用满次数的那些。

    回归用例：曾有一版回收直接把原始 job 对象写进 failed/。那份东西不是契约结果
    （没有 status/error 对象/哈希），读起来却像结果 —— 那是伪造。
    判死要写一份契约合法的失败结果，所以判死属于 worker；队列层只负责让任务重新可见。
    """
    job = make_job()
    submit(fake_s3, job)
    claimed = s3queue.claim(job["job_id"], "worker-a")
    claimed["claimed_at"] -= 7200
    claimed["attempt"] = s3queue.MAX_ATTEMPTS
    s3queue.write_json(s3queue.PREFIX_CLAIMED + f"{job['job_id']}.json", claimed)

    reclaimed = s3queue.reclaim_stale("worker-b", timeout_sec=3600)

    assert reclaimed == [job["job_id"]]
    pending = read_json(
        fake_s3, s3queue.QUEUE_BUCKET, f"{s3queue.PREFIX_PENDING}{job['job_id']}.json"
    )
    assert pending["attempt"] == s3queue.MAX_ATTEMPTS + 1
    assert fake_s3.keys(s3queue.QUEUE_BUCKET, s3queue.PREFIX_FAILED) == [], (
        "队列层不得往 failed/ 写非契约对象"
    )


def test_reclaim_clears_backoff_so_recovered_work_is_runnable(fake_s3):
    """回收不是退避：捞回来的任务应当立刻可领，而不是继续等。"""
    job = make_job()
    submit(fake_s3, job)
    claimed = s3queue.claim(job["job_id"], "worker-a")
    claimed["claimed_at"] -= 7200
    claimed["not_before"] = time.time() + 9999
    s3queue.write_json(s3queue.PREFIX_CLAIMED + f"{job['job_id']}.json", claimed)

    s3queue.reclaim_stale("worker-b", timeout_sec=3600)

    pending = read_json(
        fake_s3, s3queue.QUEUE_BUCKET, f"{s3queue.PREFIX_PENDING}{job['job_id']}.json"
    )
    assert "not_before" not in pending


# ------------------------------------------------------------ 原子写

def test_write_json_atomic_promotes_and_leaves_no_tmp(fake_s3):
    uri = s3queue.write_json_atomic("done/x.json", {"a": 1})

    assert uri.endswith("done/x.json")
    assert json.loads(fake_s3.get(s3queue.QUEUE_BUCKET, "done/x.json")) == {"a": 1}
    assert fake_s3.keys(s3queue.QUEUE_BUCKET, s3queue.PREFIX_TMP) == [], "临时对象必须清理"


def test_write_json_atomic_never_promotes_corrupt_payload(fake_s3):
    """回读校验失败的产物**绝不能**落到最终键上。"""
    fake_s3.corrupt_prefixes.add(s3queue.PREFIX_TMP)

    with pytest.raises(s3queue.S3Error) as ei:
        s3queue.write_json_atomic("done/y.json", {"a": 1})

    assert ei.value.code == "ChecksumMismatch"
    assert fake_s3.get(s3queue.QUEUE_BUCKET, "done/y.json") is None
    assert fake_s3.keys(s3queue.QUEUE_BUCKET, s3queue.PREFIX_TMP) == []


# ------------------------------------------------------------ 幂等查找

def test_find_existing_result_none_when_never_run(fake_s3):
    assert s3queue.find_existing_result(make_job()) is None


def test_find_existing_result_hits_done_by_job_id(fake_s3):
    job = make_job()
    s3queue.write_json(s3queue.PREFIX_DONE + f"{job['job_id']}.json", {"job_id": job["job_id"], "status": "done"})

    hit = s3queue.find_existing_result(job)

    assert hit is not None and hit.source == s3queue.SOURCE_DONE


def test_find_existing_result_follows_idem_index_across_job_ids(fake_s3):
    """换了 job_id 的重投靠 request_id 找到既有权威结果。"""
    s3queue.write_json(s3queue.PREFIX_DONE + "aaaa.json", {"job_id": "aaaa", "status": "done"})
    s3queue.write_json(
        s3queue.idem_key("req-shared"),
        {"request_id": "req-shared", "result_key": s3queue.PREFIX_DONE + "aaaa.json"},
    )

    hit = s3queue.find_existing_result(make_job(job_id="bbbb", request_id="req-shared"))

    assert hit is not None
    assert hit.source == s3queue.SOURCE_IDEM
    assert hit.result["job_id"] == "aaaa"


def test_publish_alias_writes_answer_under_this_job_id(fake_s3):
    """换了 job_id 的重投方也要能在自己的键上查到答案。

    队列层只负责「按 status 选前缀 + 原子写」；别名对象由 contract.build_alias 构造
    （见 test_contract_cases.py 的别名用例）。
    """
    payload = {
        "job_id": "bbbb",
        "status": "done",
        "outcome": "ALREADY_COMPLETED",
        "deduplicated_from": "aaaa",
    }

    key = s3queue.publish_alias("bbbb", payload)

    assert key == f"{s3queue.PREFIX_DONE}bbbb.json"
    assert read_json(fake_s3, s3queue.QUEUE_BUCKET, key) == payload


def test_publish_alias_uses_failed_prefix_for_failed_results(fake_s3):
    key = s3queue.publish_alias("cccc", {"job_id": "cccc", "status": "failed"})
    assert key == f"{s3queue.PREFIX_FAILED}cccc.json"


# ------------------------------------------------------------ 重试语义

def _failed_result(retryable=True, attempt=1, job=None):
    job = job or make_job()
    return contract.build_result(
        job=job,
        worker_id="w",
        status=contract.STATUS_FAILED,
        attempt=attempt,
        started_at="2026-10-15T10:00:00Z",
        finished_at="2026-10-15T10:00:01Z",
        error=contract.build_error("TIMEOUT" if retryable else "SCHEMA_INVALID", "x"),
    )


def test_should_retry_only_for_retryable_errors():
    assert s3queue.should_retry(make_job(), _failed_result(retryable=True)) is True
    assert s3queue.should_retry(make_job(), _failed_result(retryable=False)) is False


def test_should_retry_stops_at_max_attempts():
    job = make_job()
    job["attempt"] = s3queue.MAX_ATTEMPTS
    assert s3queue.should_retry(job, _failed_result(retryable=True)) is False


def test_should_retry_false_for_success():
    job = make_job()
    done = contract.build_result(
        job=job, worker_id="w", status=contract.STATUS_DONE,
        started_at="2026-10-15T10:00:00Z", finished_at="2026-10-15T10:00:01Z",
    )
    assert s3queue.should_retry(job, done) is False


def test_requeue_for_retry_increments_attempt(fake_s3):
    job = make_job()
    result = _failed_result(retryable=True, attempt=1, job=job)

    uri = s3queue.requeue_for_retry(job, result)

    assert uri.endswith(f"{s3queue.PREFIX_PENDING}{job['job_id']}.json")
    requeued = read_json(
        fake_s3, s3queue.QUEUE_BUCKET, f"{s3queue.PREFIX_PENDING}{job['job_id']}.json"
    )
    assert requeued["attempt"] == 2
    assert requeued["last_error"] == "TIMEOUT"


def test_retry_delay_is_exponential():
    """退避是任务属性，不是轮询节奏：30s / 60s（方案 §5 的最多 2 次重试）。"""
    assert s3queue.retry_delay_seconds(1) == s3queue.RETRY_BASE_SEC
    assert s3queue.retry_delay_seconds(2) == s3queue.RETRY_BASE_SEC * 2


def test_requeue_sets_not_before_into_the_future(fake_s3):
    job = make_job()
    result = _failed_result(retryable=True, attempt=1, job=job)
    before = time.time()

    s3queue.requeue_for_retry(job, result)

    requeued = read_json(
        fake_s3, s3queue.QUEUE_BUCKET, f"{s3queue.PREFIX_PENDING}{job['job_id']}.json"
    )
    assert requeued["not_before"] >= before + s3queue.RETRY_BASE_SEC


# ------------------------------------------------------------ 幂等索引的条件写入

def test_idempotency_index_keeps_the_first_writer(fake_s3):
    """并发重投时，权威结果由**先写者**决定，不是由最后写者决定。

    这是「只有一个权威结果」的机制本身：claim 无法保证只有一个 worker 拿到任务，
    但条件写入（If-None-Match: *）能保证只有一份索引登记。
    """
    job_a = make_job(job_id="aaaa", request_id="req-race")
    job_b = make_job(job_id="bbbb", request_id="req-race")
    result_a = {"job_id": "aaaa", "status": "done", "request_id": "req-race", "worker": "w-a"}
    result_b = {"job_id": "bbbb", "status": "done", "request_id": "req-race", "worker": "w-b"}

    assert s3queue._record_idempotency(job_a, result_a, "jobs/done/aaaa.json") is not None
    assert s3queue._record_idempotency(job_b, result_b, "jobs/done/bbbb.json") is None, (
        "第二个写者必须输 —— 否则权威结果会被后写者覆盖"
    )

    entry = read_json(fake_s3, s3queue.QUEUE_BUCKET, s3queue.idem_key("req-race"))
    assert entry["job_id"] == "aaaa"
    assert entry["result_key"] == "jobs/done/aaaa.json"


def test_idempotency_index_falls_back_loudly_when_conditional_write_unsupported(fake_s3, capsys):
    """后端不支持条件写时降级，但必须**出声** —— 不能让那句保证悄悄变成空话。"""
    from botocore.exceptions import ClientError

    fake_s3.fail_on["put_object"] = ClientError(
        {"Error": {"Code": "NotImplemented", "Message": "no If-None-Match"}}, "PutObject"
    )
    s3queue._conditional_write_supported = True
    job = make_job(request_id="req-fallback")
    try:
        s3queue._record_idempotency(job, {"status": "done"}, "jobs/done/x.json")
    finally:
        fake_s3.fail_on.pop("put_object", None)
        s3queue._conditional_write_supported = True

    out = capsys.readouterr().out
    assert "不支持条件写入" in out


def test_mark_attempt_failed_does_not_record_idempotency(fake_s3):
    """可重试的中间失败若不登记索引，就会被误当成权威结论。"""
    job = make_job()
    result = _failed_result(retryable=True, job=job)

    s3queue.mark_attempt_failed(job, result)

    assert fake_s3.keys(s3queue.QUEUE_BUCKET, s3queue.PREFIX_IDEM) == []
    assert len(fake_s3.keys(s3queue.QUEUE_BUCKET, s3queue.PREFIX_FAILED)) == 1


def test_mark_failed_records_idempotency_and_clears_claimed(fake_s3):
    job = make_job()
    s3queue.claim(job["job_id"], "worker-a")
    result = _failed_result(retryable=False, job=job)

    s3queue.mark_failed(job, result, "worker-a")

    assert len(fake_s3.keys(s3queue.QUEUE_BUCKET, s3queue.PREFIX_IDEM)) == 1
    assert fake_s3.keys(s3queue.QUEUE_BUCKET, s3queue.PREFIX_CLAIMED) == []


def test_mark_done_is_idempotent_by_request(fake_s3):
    job = make_job()
    result = contract.build_result(
        job=job, worker_id="w", status=contract.STATUS_DONE,
        started_at="2026-10-15T10:00:00Z", finished_at="2026-10-15T10:00:01Z",
    )

    s3queue.mark_done(job, result, "w")
    hit = s3queue.find_existing_result(job)

    assert hit is not None and hit.result["status"] == "done"


# ------------------------------------------------------------ 输入预检

def test_head_input_reports_size_and_missing(fake_s3):
    data = b"0123456789"
    key = seed_input(fake_s3, data)

    assert s3queue.head_input(key) == len(data)
    assert s3queue.head_input("raw/non-ai/fixtures/absent.wav") is None


def test_input_hash_uses_real_bytes(fake_s3, tmp_path):
    data = b"some audio bytes"
    key = seed_input(fake_s3, data)
    dest = tmp_path / "out" / "tone.wav"

    s3queue.download_input(key, str(dest))

    assert s3queue.sha256_file(str(dest)) == sha256_hex(data)


def test_unknown_client_fault_surfaces_as_s3error(fake_s3):
    from botocore.exceptions import ClientError

    fake_s3.fail_on["list_objects_v2"] = ClientError(
        {"Error": {"Code": "AccessDenied", "Message": "nope"}}, "ListObjectsV2"
    )

    with pytest.raises(s3queue.S3Error) as ei:
        s3queue.list_pending()

    assert ei.value.code == "AccessDenied"
