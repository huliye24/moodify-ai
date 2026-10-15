"""测试用的任务/输入构造器。"""

from __future__ import annotations

import hashlib
import json
from typing import Any, Dict, Optional

import contract
import s3queue

INPUT_BUCKET = s3queue.INPUT_BUCKET
QUEUE_BUCKET = s3queue.QUEUE_BUCKET
DEFAULT_INPUT_KEY = "raw/non-ai/fixtures/tone.wav"


def sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def make_job(
    *,
    job_id: str = "11111111-1111-4111-8111-111111111111",
    request_id: str = "req-0001",
    job_type: str = "smoke",
    bucket: str = INPUT_BUCKET,
    key: str = "raw/non-ai/fixtures/tone.wav",
    sha256: Optional[str] = None,
    output_prefix: Optional[str] = None,
    params: Optional[Dict[str, Any]] = None,
    limits: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    job: Dict[str, Any] = {
        "schema_version": contract.JOB_SCHEMA_VERSION,
        "job_id": job_id,
        "request_id": request_id,
        "job_type": job_type,
        "input": {
            "bucket": bucket,
            "key": key,
            "sha256": sha256 or ("0" * 64),
        },
        "output_prefix": output_prefix or f"results/{job_id}/",
        "created_at": "2026-10-15T10:00:00Z",
    }
    if params is not None:
        job["params"] = params
    if limits is not None:
        job["limits"] = limits
    return job


def submit(fake, job: Dict[str, Any], *, prefix: str = s3queue.PREFIX_PENDING) -> str:
    """把任务投进队列，返回键。"""
    key = f"{prefix}{job['job_id']}.json"
    fake.seed(QUEUE_BUCKET, key, json.dumps(job).encode("utf-8"))
    return key


def seed_input(fake, data: bytes, key: str = DEFAULT_INPUT_KEY) -> str:
    """放一个输入对象，**返回它的键**（不是哈希 —— 哈希请用 :func:`sha256_hex`）。"""
    fake.seed(INPUT_BUCKET, key, data)
    return key


def read_json(fake, bucket: str, key: str) -> Dict[str, Any]:
    return json.loads(fake.get(bucket, key).decode("utf-8"))
