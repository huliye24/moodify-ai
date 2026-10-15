"""Moodify S3 任务队列 —— worker 侧封装（宁夏节点）。

设计前提（2026-10-15 实测）
--------------------------
- 香港 ↔ 宁夏 TCP 完全不通（安全组未放行），两端**不直接通信**，队列完全走 S3。
- 宁夏节点只能**主动出站**访问 S3，不接受任何入站连接。
- 凭据一律来自 EC2 instance profile，**禁止把 access key 写进文件或环境变量**。

路径约定（桶 ``moodify-experiments``）
------------------------------------
    jobs/pending/<job_id>.json     待处理（生产者的唯一投递口）
    jobs/claimed/<job_id>.json     已认领（含 worker_id / claimed_at / attempt）
    jobs/done/<job_id>.json        已完成（结果 JSON）
    jobs/failed/<job_id>.json      失败（结果 JSON，含 error 对象）
    idem/<hash>.json               request_id → 权威结果 的幂等索引
    results/<job_id>/...           产物

输入音频在 ``moodify-dataset``，由任务 JSON 的 ``input`` 指定。

原子性：S3 没有原子 rename —— 这是被接受的边界，不是 bug
-------------------------------------------------------
1. **claim** 是「先写 claimed、再删 pending」两步。两步之间崩溃会让任务同时出现在
   pending 与 claimed —— 由 :func:`reclaim_stale` 回收。两个 worker 同时认领同一任务
   时两边都会执行，因此结果写入必须幂等（见第 2 点），不能靠 claim 保证唯一。
2. **结果写入**走「临时键 → 回读校验 → 最终键」。最终键是权威；重复执行产生的是同一份
   确定性结果，后写者覆盖先写者，语义不变。
3. **幂等索引**在结果落最终键之后写。若在这两步之间崩溃，同一 ``request_id`` 可能再执行
   一次 —— 这是已知且被接受的窄窗口，worker 侧用 ``done/<job_id>.json`` 存在性先兜一层。
"""

from __future__ import annotations

import hashlib
import json
import os
import time
import uuid
from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Optional

import boto3
import botocore

REGION = "cn-northwest-1"
QUEUE_BUCKET = "moodify-experiments"
INPUT_BUCKET = "moodify-dataset"

PREFIX_PENDING = "jobs/pending/"
PREFIX_CLAIMED = "jobs/claimed/"
PREFIX_DONE = "jobs/done/"
PREFIX_FAILED = "jobs/failed/"
PREFIX_IDEM = "idem/"
PREFIX_RESULTS = "results/"
PREFIX_TMP = "tmp/"

#: claimed 超过此秒数视为僵死，可回收。
CLAIM_TIMEOUT_SEC = 3600

#: 重试上限（方案 §5：最多 2 次重试，即最多 3 次尝试）。
MAX_ATTEMPTS = 3

def _default_client():
    """生产路径：凭据由 EC2 instance profile 提供，不落盘。"""
    return boto3.client("s3", region_name=REGION)


_client_factory: Callable[[], Any] = _default_client


def use_client_factory(factory: Callable[[], Any]) -> None:
    """注入 S3 client 工厂。仅供测试使用（生产走 instance profile）。"""
    global _client_factory
    _client_factory = factory


def reset_client_factory() -> None:
    global _client_factory
    _client_factory = _default_client


def _client():
    return _client_factory()


class S3Error(RuntimeError):
    """S3 操作失败。保留原始错误码，便于上层分类处理。"""

    def __init__(self, op: str, code: str, detail: str = ""):
        self.op = op
        self.code = code
        self.detail = detail
        super().__init__(f"{op} failed: {code} {detail}".strip())


def _wrap(op: str, fn):
    try:
        return fn()
    except botocore.exceptions.ClientError as e:
        resp = getattr(e, "response", {})
        code = resp.get("Error", {}).get("Code", type(e).__name__)
        raise S3Error(op, code, str(e)[:300]) from e


def _is_missing_error(code: str) -> bool:
    return code in ("NoSuchKey", "404", "NotFound")


# ----------------------------------------------------------------- 基础读写


def list_pending(limit: int = 10) -> List[str]:
    """列出待处理任务 id。需要 s3:ListBucket。"""
    c = _client()

    def _go():
        r = c.list_objects_v2(Bucket=QUEUE_BUCKET, Prefix=PREFIX_PENDING, MaxKeys=limit)
        out = []
        for o in r.get("Contents", []):
            key = o["Key"]
            if key.endswith(".json"):
                out.append(key[len(PREFIX_PENDING) : -len(".json")])
        return out

    return _wrap("list_pending", _go)


def list_keys(prefix: str, limit: int = 100) -> List[str]:
    """列出某前缀下的对象键（含完整键）。"""
    c = _client()

    def _go():
        r = c.list_objects_v2(Bucket=QUEUE_BUCKET, Prefix=prefix, MaxKeys=limit)
        return [o["Key"] for o in r.get("Contents", [])]

    return _wrap(f"list_keys({prefix})", _go)


def read_json(key: str, bucket: str = QUEUE_BUCKET) -> Dict[str, Any]:
    c = _client()

    def _go():
        r = c.get_object(Bucket=bucket, Key=key)
        return json.loads(r["Body"].read().decode("utf-8"))

    return _wrap(f"read_json({bucket}/{key})", _go)


def read_json_or_none(key: str, bucket: str = QUEUE_BUCKET) -> Optional[Dict[str, Any]]:
    """读 JSON；对象不存在返回 None，其它错误照抛。"""
    try:
        return read_json(key, bucket)
    except S3Error as e:
        if _is_missing_error(e.code):
            return None
        raise


def write_json(key: str, payload: Dict[str, Any], bucket: str = QUEUE_BUCKET) -> str:
    c = _client()
    body = json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True).encode("utf-8")

    def _go():
        c.put_object(
            Bucket=bucket, Key=key, Body=body, ContentType="application/json; charset=utf-8"
        )
        return f"s3://{bucket}/{key}"

    return _wrap(f"write_json({bucket}/{key})", _go)


def write_json_atomic(key: str, payload: Dict[str, Any], bucket: str = QUEUE_BUCKET) -> str:
    """临时键 → 回读校验 → 最终键。

    校验失败即删临时键并抛错，**绝不把未校验的产物放到最终键上**。
    """
    c = _client()
    body = json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True).encode("utf-8")
    tmp_key = f"{PREFIX_TMP}{uuid.uuid4().hex}.json"
    digest = hashlib.sha256(body).hexdigest()

    def _put_tmp():
        c.put_object(
            Bucket=bucket, Key=tmp_key, Body=body, ContentType="application/json; charset=utf-8"
        )

    def _read_back():
        return c.get_object(Bucket=bucket, Key=tmp_key)["Body"].read()

    def _promote():
        c.put_object(
            Bucket=bucket, Key=key, Body=body, ContentType="application/json; charset=utf-8"
        )

    _wrap("atomic:put_tmp", _put_tmp)
    try:
        got = _wrap("atomic:read_back", _read_back)
        if hashlib.sha256(got).hexdigest() != digest:
            raise S3Error("atomic:read_back", "ChecksumMismatch", "临时对象回读内容不一致")
        _wrap("atomic:promote", _promote)
    finally:
        try:
            _wrap("atomic:cleanup_tmp", lambda: c.delete_object(Bucket=bucket, Key=tmp_key))
        except S3Error:
            pass  # tmp/ 前缀本身有生命周期规则兜底，不因清理失败而掩盖主流程
    return f"s3://{bucket}/{key}"


def delete(key: str, bucket: str = QUEUE_BUCKET) -> None:
    c = _client()
    _wrap(f"delete({bucket}/{key})", lambda: c.delete_object(Bucket=bucket, Key=key))


def head_input(key: str, bucket: str = INPUT_BUCKET) -> Optional[int]:
    """输入对象字节数。对象不存在返回 None。用于下载前预检超限。"""
    c = _client()

    def _go():
        return c.head_object(Bucket=bucket, Key=key)["ContentLength"]

    try:
        return _wrap(f"head_input({bucket}/{key})", _go)
    except S3Error as e:
        if _is_missing_error(e.code):
            return None
        raise


# ----------------------------------------------------------------- 队列状态


def claim(job_id: str, worker_id: str) -> Optional[Dict[str, Any]]:
    """尝试认领任务。返回 job dict；pending 已不存在则返回 None。

    ⚠️ 非原子：两个 worker 可能同时读到同一 pending 并都认为自己认领成功。
    因此下游必须容忍重复执行 —— 结果写入本身是幂等的（见模块 docstring）。

    ``attempt`` **沿用** pending 里已有的值，绝不重置为 1 —— 重置会让
    :func:`requeue_for_retry` 的递增每次被抹平，``MAX_ATTEMPTS`` 永远用不满，
    坏任务于是无限重投。
    """
    c = _client()
    pending_key = PREFIX_PENDING + job_id + ".json"
    claimed_key = PREFIX_CLAIMED + job_id + ".json"
    try:
        r = c.get_object(Bucket=QUEUE_BUCKET, Key=pending_key)
        job = json.loads(r["Body"].read().decode("utf-8"))
    except botocore.exceptions.ClientError as e:
        code = getattr(e, "response", {}).get("Error", {}).get("Code", "")
        if _is_missing_error(code):
            return None
        raise S3Error("claim:get", code, str(e)[:300]) from e

    job["claimed_at"] = time.time()
    job["worker_id"] = worker_id
    job["attempt"] = int(job.get("attempt") or 1)
    write_json(claimed_key, job)
    delete(pending_key)
    return job


def reclaim_stale(
    worker_id: str, timeout_sec: int = CLAIM_TIMEOUT_SEC, limit: int = 100
) -> List[str]:
    """把超时未完成的 claimed 任务放回 pending。返回被回收的 job_id 列表。

    为什么需要：claim 是「先写 claimed、再删 pending」，中间崩溃会让任务卡在 claimed
    里再也不被任何人看到。回收时把 attempt 加一，超过 :data:`MAX_ATTEMPTS` 的直接判死，
    避免坏任务 crash loop。
    """
    now = time.time()
    reclaimed: List[str] = []

    claimed_keys = list_keys(PREFIX_CLAIMED, limit=limit)
    for key in claimed_keys:
        if not key.endswith(".json"):
            continue
        job_id = key[len(PREFIX_CLAIMED) : -len(".json")]
        try:
            job = read_json(key)
        except S3Error as e:
            if _is_missing_error(e.code):
                continue  # 别人刚完成并清了 claimed
            raise

        claimed_at = job.get("claimed_at") or 0
        if now - claimed_at < timeout_sec:
            continue

        attempt = int(job.get("attempt") or 1) + 1
        if attempt > MAX_ATTEMPTS:
            job["attempt"] = attempt
            job["reclaimed_by"] = worker_id
            write_json_atomic(PREFIX_FAILED + job_id + ".json", job)
            delete(key)
            reclaimed.append(job_id)
            continue

        resumed = dict(job)
        resumed["attempt"] = attempt
        resumed["reclaimed_by"] = worker_id
        resumed.pop("worker_id", None)
        resumed.pop("claimed_at", None)
        write_json(PREFIX_PENDING + job_id + ".json", resumed)
        delete(key)
        reclaimed.append(job_id)

    return reclaimed


def mark_done(job: Dict[str, Any], result: Dict[str, Any], worker_id: str) -> str:
    """结果落 done/ 并清 claimed。结果对象须已通过契约校验。"""
    job_id = str(job["job_id"])
    uri = write_json_atomic(PREFIX_DONE + job_id + ".json", result)
    _record_idempotency(job, result, f"{PREFIX_DONE}{job_id}.json")
    _clear_claimed(job_id)
    return uri


def mark_failed(job: Dict[str, Any], result: Dict[str, Any], worker_id: str) -> str:
    """结果落 failed/ 并清 claimed。"""
    job_id = str(job["job_id"])
    uri = write_json_atomic(PREFIX_FAILED + job_id + ".json", result)
    _record_idempotency(job, result, f"{PREFIX_FAILED}{job_id}.json")
    _clear_claimed(job_id)
    return uri


def mark_attempt_failed(job: Dict[str, Any], result: Dict[str, Any]) -> str:
    """可重试的中间失败：留诊断记录，但**不**登记幂等索引、**不**清 claimed。

    登记索引会把一次抖动变成永久结论（重试再也跑不到），所以中间失败与终态失败
    必须走两条路。
    """
    job_id = str(job["job_id"])
    return write_json_atomic(PREFIX_FAILED + job_id + ".json", result)


def _clear_claimed(job_id: str) -> None:
    try:
        delete(PREFIX_CLAIMED + job_id + ".json")
    except S3Error:
        pass  # claimed 已不存在不影响完成语义


def _record_idempotency(job: Dict[str, Any], result: Dict[str, Any], result_key: str) -> None:
    """登记 request_id → 权威结果。失败不阻断：结果本身已落在 done/failed 上。"""
    request_id = job.get("request_id")
    if not request_id:
        return
    entry = {
        "request_id": request_id,
        "job_id": str(job["job_id"]),
        "job_type": job.get("job_type"),
        "status": result.get("status"),
        "result_key": result_key,
        "recorded_at": time.time(),
    }
    try:
        write_json(idem_key(request_id), entry)
    except S3Error:
        pass


def publish_alias(job_id: str, alias_payload: Dict[str, Any]) -> str:
    """把**已构建好**的别名对象写到 ``done/<job_id>.json`` 或 ``failed/<job_id>.json``。

    为什么需要别名：生产者只会在 ``done/<自己的 job_id>.json`` 上等答案。幂等命中时若只是
    「跳过执行」，换了 job_id 的重投方会永远等不到 —— 那是静默丢件，不是幂等。

    队列层不认识状态语义，也不负责构造别名对象（那是契约的活，见 ``contract.build_alias``）；
    这里只做「按 payload.status 选前缀、原子写」。
    """
    prefix = PREFIX_DONE if alias_payload.get("status") != "failed" else PREFIX_FAILED
    key = f"{prefix}{job_id}.json"
    write_json_atomic(key, alias_payload)
    return key


def idem_key(request_id: str) -> str:
    """request_id → 幂等索引键。哈希掉任意字符，避免键名注入。"""
    return PREFIX_IDEM + hashlib.sha256(request_id.encode("utf-8")).hexdigest()[:32] + ".json"


#: 幂等候选的来源标签。
SOURCE_DONE = "done/<job_id>"
SOURCE_FAILED = "failed/<job_id>"
SOURCE_IDEM = "idem"


@dataclass(frozen=True)
class ExistingResult:
    """查到的既有结果候选。**是否为终态由调用方用 contract.is_terminal 判定** ——
    队列层不认识状态语义，别让它替契约做判断。"""

    source: str
    result: Dict[str, Any]


def find_existing_result(job: Dict[str, Any]) -> Optional[ExistingResult]:
    """查同一任务是否已有结果。三层，从最权威到最间接：

    1. ``done/<job_id>``  —— 同一 job_id 重投，必然终态
    2. 幂等索引 → 结果键 —— 换了 job_id 但 request_id 相同（只登记终态）
    3. ``failed/<job_id>`` —— 兜住没有 request_id 的失败任务

    返回 None 表示从未跑过，可以正常执行。
    """
    job_id = str(job["job_id"])

    hit = read_json_or_none(PREFIX_DONE + job_id + ".json")
    if hit is not None:
        return ExistingResult(SOURCE_DONE, hit)

    request_id = job.get("request_id")
    if request_id:
        entry = read_json_or_none(idem_key(request_id))
        if entry is not None:
            result = read_json_or_none(entry["result_key"])
            if result is not None:
                return ExistingResult(SOURCE_IDEM, result)

    hit = read_json_or_none(PREFIX_FAILED + job_id + ".json")
    if hit is not None:
        return ExistingResult(SOURCE_FAILED, hit)

    return None


# ----------------------------------------------------------------- 重试语义

def attempt_of(job: Dict[str, Any]) -> int:
    return int(job.get("attempt") or 1)


def should_retry(job: Dict[str, Any], result: Dict[str, Any]) -> bool:
    """失败后是否值得重投：错误码可重试 且 未用满 MAX_ATTEMPTS。"""
    if result.get("status") != "failed":
        return False
    if not result.get("retryable"):
        return False
    return attempt_of(job) < MAX_ATTEMPTS


def requeue_for_retry(job: Dict[str, Any], result: Dict[str, Any]) -> str:
    """把任务放回 pending 等下一轮（指数退避由 worker 的 poll 节奏承担）。"""
    resumed = {k: v for k, v in job.items() if k not in ("worker_id", "claimed_at")}
    resumed["attempt"] = attempt_of(job) + 1
    resumed["retry_of"] = str(job["job_id"])
    resumed["last_error"] = (result.get("error") or {}).get("code")
    return write_json(PREFIX_PENDING + str(job["job_id"]) + ".json", resumed)


# ----------------------------------------------------------------- 产物传输


def download_input(input_key: str, dest_path: str, bucket: str = INPUT_BUCKET) -> str:
    """下载输入音频到本地。需要 s3:GetObject on 输入前缀。"""
    c = _client()
    os.makedirs(os.path.dirname(dest_path) or ".", exist_ok=True)

    def _go():
        c.download_file(bucket, input_key, dest_path)
        return dest_path

    return _wrap(f"download_input({bucket}/{input_key})", _go)


def upload_result(local_path: str, result_key: str) -> str:
    """上传产物到 results/。需要 s3:PutObject on results/*。"""
    c = _client()

    def _go():
        c.upload_file(local_path, QUEUE_BUCKET, PREFIX_RESULTS + result_key)
        return f"s3://{QUEUE_BUCKET}/{PREFIX_RESULTS}{result_key}"

    return _wrap(f"upload_result({result_key})", _go)


def sha256_file(path: str, chunk: int = 1024 * 1024) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for block in iter(lambda: f.read(chunk), b""):
            h.update(block)
    return h.hexdigest()


def object_content_length(key: str, bucket: str) -> int:
    c = _client()

    def _go():
        return c.head_object(Bucket=bucket, Key=key)["ContentLength"]

    return _wrap(f"content_length({bucket}/{key})", _go)


def presign(key: str, bucket: str = INPUT_BUCKET, expires: int = 3600) -> str:
    """生成预签名 URL。只做本地 HMAC 签名，不需要访问 AWS 网络。"""
    c = _client()
    try:
        return c.generate_presigned_url(
            "get_object", Params={"Bucket": bucket, "Key": key}, ExpiresIn=expires
        )
    except Exception as e:
        raise S3Error("presign", type(e).__name__, str(e)[:200]) from e


def worker_id() -> str:
    # os.uname 是 Unix only；本地（Windows）跑测试时退回 platform.node()
    try:
        host = os.uname().nodename
    except AttributeError:  # pragma: no cover - 平台分支
        import platform

        host = platform.node() or "unknown-host"
    return f"{host}-{uuid.uuid4().hex[:8]}"
