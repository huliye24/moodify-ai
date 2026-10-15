"""内存版 S3 —— 让队列语义（竞争、回收、幂等、原子写）能在本地无凭据地测。

只实现 worker 真正用到的那几个动作。任何「测不到就不测」的取舍都在这里显式记着：
``download_file`` / ``upload_file`` 是 boto3 的托管传输接口，语义等价于 get/put。
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple

from botocore.exceptions import ClientError


class _Body:
    def __init__(self, data: bytes):
        self._data = data

    def read(self) -> bytes:
        return self._data


class FakeS3:
    """按 (bucket, key) 存字节的内存对象存储。"""

    def __init__(self) -> None:
        self.objects: Dict[Tuple[str, str], bytes] = {}
        self.calls: List[str] = []
        #: 形如 {"put_object": Exception(...)}，用于故障注入
        self.fail_on: Dict[str, Exception] = {}
        #: 命中这些前缀的键，写入时被替换成坏字节（模拟回读校验失败）
        self.corrupt_prefixes: set = set()

    # ------------------------------------------------------------ 测试辅助

    def seed(self, bucket: str, key: str, data: bytes) -> None:
        self.objects[(bucket, key)] = data

    def get(self, bucket: str, key: str) -> Optional[bytes]:
        return self.objects.get((bucket, key))

    def keys(self, bucket: str, prefix: str = "") -> List[str]:
        return sorted(k for (b, k) in self.objects if b == bucket and k.startswith(prefix))

    def _maybe_fail(self, op: str) -> None:
        exc = self.fail_on.get(op)
        if exc is not None:
            raise exc

    @staticmethod
    def _missing(op: str, key: str, code: str = "NoSuchKey") -> ClientError:
        return ClientError({"Error": {"Code": code, "Message": f"missing {key}"}}, op)

    # ------------------------------------------------------------ S3 接口

    def put_object(self, Bucket: str, Key: str, Body: bytes, **kwargs: Any) -> dict:
        self.calls.append(f"put:{Key}")
        self._maybe_fail("put_object")
        # If-None-Match: * —— 真正的条件写：键已存在就 412，让 S3（这里是替身）裁定谁赢
        if kwargs.get("IfNoneMatch") == "*" and (Bucket, Key) in self.objects:
            raise ClientError(
                {"Error": {"Code": "PreconditionFailed", "Message": "object exists"}},
                "PutObject",
            )
        data = bytes(Body)
        if any(Key.startswith(p) for p in self.corrupt_prefixes):
            data = b'{"corrupted": true}'
        self.objects[(Bucket, Key)] = data
        return {}

    def get_object(self, Bucket: str, Key: str, **kwargs: Any) -> dict:
        self.calls.append(f"get:{Key}")
        self._maybe_fail("get_object")
        data = self.objects.get((Bucket, Key))
        if data is None:
            raise self._missing("GetObject", Key)
        return {"Body": _Body(data), "ContentLength": len(data)}

    def head_object(self, Bucket: str, Key: str, **kwargs: Any) -> dict:
        self.calls.append(f"head:{Key}")
        self._maybe_fail("head_object")
        data = self.objects.get((Bucket, Key))
        if data is None:
            # 真实 boto3 的 head_object 对缺失对象回 404 而不是 NoSuchKey
            raise self._missing("HeadObject", Key, code="404")
        return {"ContentLength": len(data)}

    def delete_object(self, Bucket: str, Key: str, **kwargs: Any) -> dict:
        self.calls.append(f"delete:{Key}")
        self._maybe_fail("delete_object")
        self.objects.pop((Bucket, Key), None)
        return {}

    def list_objects_v2(self, Bucket: str, Prefix: str = "", MaxKeys: int = 1000, **kwargs: Any) -> dict:
        self.calls.append(f"list:{Prefix}")
        self._maybe_fail("list_objects_v2")
        hits = sorted(k for (b, k) in self.objects if b == Bucket and k.startswith(Prefix))
        contents = [{"Key": k} for k in hits[:MaxKeys]]
        return {"Contents": contents, "IsTruncated": len(hits) > MaxKeys}

    def download_file(self, Bucket: str, Key: str, Filename: str, **kwargs: Any) -> None:
        self.calls.append(f"download:{Key}")
        self._maybe_fail("download_file")
        data = self.objects.get((Bucket, Key))
        if data is None:
            raise self._missing("GetObject", Key)
        with open(Filename, "wb") as f:
            f.write(data)

    def upload_file(self, Filename: str, Bucket: str, Key: str, **kwargs: Any) -> None:
        self.calls.append(f"upload:{Key}")
        self._maybe_fail("upload_file")
        with open(Filename, "rb") as f:
            self.objects[(Bucket, Key)] = f.read()

    def generate_presigned_url(self, *args: Any, **kwargs: Any) -> str:
        return "https://example.invalid/presigned"
