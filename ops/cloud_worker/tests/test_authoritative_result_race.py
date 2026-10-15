"""W2 验收（裁决版）：争用之下**只有一个权威结果**。

裁决（2026-10-15）：
> 竞争测试应验证「最终只有一个权威结果」，而不是「只有一个 worker 读到任务」。

这两件事必须分清楚，因为后者**做不到**：
- ``claim`` 是 get → put claimed → delete pending 三步，S3 没有原子 rename，
  两个 worker 可以都读到同一份 pending、都认为自己拿到了任务（见
  ``test_claim_order_creates_a_race_window``）。
- 我们能保证的不是「谁拿到了」，而是「完成后谁的答案算数」。

所以本模块把两条路径都走到底：
1. **幂等路径**：第二个 worker 撞上既有结果 → 不重复执行，回同一份权威结果。
2. **双双真跑路径**：把第二个 worker 的幂等检查短路，让它**真的再跑一遍** →
   索引仍然只有一份，且**先写者**才是权威。
"""

from __future__ import annotations

import contract
import s3queue
import worker
from helpers import make_job, read_json, seed_input, sha256_hex, submit

WID_A = "worker-a"
WID_B = "worker-b"
AUDIO = b"RIFF....fake wav bytes for testing"


def _ready(fake_s3, work_root):
    key = seed_input(fake_s3, AUDIO)
    return key, sha256_hex(AUDIO)


def _index_entries(fake):
    return [k for k in fake.keys(s3queue.QUEUE_BUCKET, s3queue.PREFIX_IDEM) if k.endswith(".json")]


# ---------------------------------------------------------------- 1. 幂等路径

def test_second_worker_returns_the_same_authoritative_result(fake_s3, work_root):
    """第二个 worker 撞上既有结果时，必须回**同一份**答案，而不是再算一遍。"""
    key, digest = _ready(fake_s3, work_root)
    job = make_job(key=key, sha256=digest)
    submit(fake_s3, job)

    assert worker.process_one(WID_A) is True
    authoritative = read_json(
        fake_s3, s3queue.QUEUE_BUCKET, f"{s3queue.PREFIX_DONE}{job['job_id']}.json"
    )

    # 还原成 B 也读到过的那份 pending，让它走完整的认领流程
    submit(fake_s3, job)
    fake_s3.calls.clear()
    assert worker.process_one(WID_B) is True

    after = read_json(
        fake_s3, s3queue.QUEUE_BUCKET, f"{s3queue.PREFIX_DONE}{job['job_id']}.json"
    )
    assert after == authoritative, "既有结果逐字不变"
    assert not any(c.startswith("upload:") for c in fake_s3.calls), "不得重复执行"
    assert len(_index_entries(fake_s3)) == 1, "幂等索引只能有一份"


# ---------------------------------------------------------------- 2. 双双真跑

def test_index_records_exactly_one_winner_even_if_both_workers_execute(
    fake_s3, work_root, monkeypatch
):
    """把 B 的幂等检查短路，让它**真的再跑一遍** —— 索引仍只能有一份，且先写者赢。

    这正是 claim 非原子的后果：两个 worker 都可能跑完。所以「唯一」不能靠
    「只有一个 worker 拿到任务」来保证，只能靠**条件写入**来裁定。
    """
    key, digest = _ready(fake_s3, work_root)
    job = make_job(key=key, sha256=digest)
    submit(fake_s3, job)

    assert worker.process_one(WID_A) is True
    first_entry = read_json(fake_s3, s3queue.QUEUE_BUCKET, _index_entries(fake_s3)[0])
    assert first_entry["job_id"] == job["job_id"]

    # 短路 B 的幂等查找：它会以为自己是第一个，于是真的执行一遍并试图登记
    monkeypatch.setattr(s3queue, "find_existing_result", lambda j: None)
    submit(fake_s3, job)
    assert worker.process_one(WID_B) is True, "B 确实执行了 —— 这就是那个竞争窗口"

    entries = _index_entries(fake_s3)
    assert len(entries) == 1, "条件写入必须挡住后写者，索引只能有一份"
    assert read_json(fake_s3, s3queue.QUEUE_BUCKET, entries[0]) == first_entry, (
        "先写者的登记不得被后写者改写"
    )


def test_replay_after_contention_resolves_to_the_recorded_winner(fake_s3, work_root, monkeypatch):
    """争用之后再来一次投递，答案必须来自**被登记的那个** job。

    用**不同的 job_id、相同的 request_id** 才有判别力：同一个 job_id 下两个 worker 写的是
    同一个键，看不出谁算数；换了 job_id 才有「两份都像是答案」的问题，也才需要索引裁定。
    """
    key, digest = _ready(fake_s3, work_root)
    first = make_job(job_id="aaaa", request_id="req-contended", key=key, sha256=digest)
    second = make_job(job_id="bbbb", request_id="req-contended", key=key, sha256=digest)
    submit(fake_s3, first)

    assert worker.process_one(WID_A) is True

    # B 以为自己是第一个（短路幂等查找），于是真的跑了一遍并试图登记
    monkeypatch.setattr(s3queue, "find_existing_result", lambda j: None)
    submit(fake_s3, second)
    assert worker.process_one(WID_B) is True
    monkeypatch.undo()

    entry = read_json(fake_s3, s3queue.QUEUE_BUCKET, _index_entries(fake_s3)[0])
    assert entry["job_id"] == "aaaa", "先写者才是被登记的那一个"

    third = make_job(job_id="cccc", request_id="req-contended", key=key, sha256=digest)
    hit = s3queue.find_existing_result(third)

    assert hit is not None
    assert hit.result["job_id"] == "aaaa", "续投解析到被登记的先写者，而不是后写者"


def test_same_job_id_overwrite_is_benign_because_the_content_is_the_same(
    fake_s3, work_root, monkeypatch
):
    """同一 job_id 的两个 worker 都会写 ``done/<job_id>.json``；后写者覆盖是良性的。

    为什么良性：同一份输入 + 同一份参数 → 同一份实质性结论。差异只在
    worker_id / 时间戳 / 耗时这些属于「谁跑的」而非「跑出了什么」的字段上。
    这里断言**实质性字段**一致 —— 若哪天它们会不一致，这个覆盖就不再良性，
    这条测试会先炸。
    """
    key, digest = _ready(fake_s3, work_root)
    job = make_job(key=key, sha256=digest)
    submit(fake_s3, job)
    worker.process_one(WID_A)
    first = read_json(
        fake_s3, s3queue.QUEUE_BUCKET, f"{s3queue.PREFIX_DONE}{job['job_id']}.json"
    )

    monkeypatch.setattr(s3queue, "find_existing_result", lambda j: None)
    submit(fake_s3, job)
    worker.process_one(WID_B)
    second = read_json(
        fake_s3, s3queue.QUEUE_BUCKET, f"{s3queue.PREFIX_DONE}{job['job_id']}.json"
    )

    for field in ("status", "job_id", "request_id", "job_type", "input_sha256"):
        assert first[field] == second[field], f"实质性字段 {field} 不该因谁跑过而变"
    assert [o["key"] for o in first["outputs"]] == [o["key"] for o in second["outputs"]]
    assert [o["sha256"] for o in first["outputs"]] == [o["sha256"] for o in second["outputs"]], (
        "产物内容哈希一致 —— 否则后写者覆盖就不再是良性的"
    )


# ---------------------------------------------------------------- 3. 反面

def test_contention_never_produces_two_authoritative_entries(fake_s3, work_root, monkeypatch):
    """把「两个 worker 都写索引」这件事直接试穿：第二条必须写不进去。"""
    key, digest = _ready(fake_s3, work_root)
    job = make_job(key=key, sha256=digest, request_id="req-twice")

    monkeypatch.setattr(s3queue, "find_existing_result", lambda j: None)
    submit(fake_s3, job)
    worker.process_one(WID_A)
    submit(fake_s3, job)
    worker.process_one(WID_B)

    assert len(_index_entries(fake_s3)) == 1


def test_contended_result_still_validates_against_the_contract(fake_s3, work_root, monkeypatch):
    """争用产生的还是**契约合法的结果**，不是「总之写进去了」的东西。"""
    key, digest = _ready(fake_s3, work_root)
    job = make_job(key=key, sha256=digest, request_id="req-valid")
    submit(fake_s3, job)
    worker.process_one(WID_A)

    monkeypatch.setattr(s3queue, "find_existing_result", lambda j: None)
    submit(fake_s3, job)
    worker.process_one(WID_B)

    result = read_json(
        fake_s3, s3queue.QUEUE_BUCKET, f"{s3queue.PREFIX_DONE}{job['job_id']}.json"
    )
    contract.validate_result(result)
    assert result["outcome"] == contract.OUTCOME_EXECUTED
    assert len(_index_entries(fake_s3)) == 1
