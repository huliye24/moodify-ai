"""让 `pytest ops/cloud_worker/tests` 能直接 import contract / s3queue / worker。

worker 的一份源码要在两个形态下工作：仓库形态（本目录）与部署形态
（`<worker_root>/`）。部署形态由 deploy.sh 把模块平铺到 worker 根目录，
所以运行时是平铺 import；这里把 `ops/cloud_worker` 与 `ops/cloud_worker/lib`
加进 sys.path，让仓库形态与部署形态的 import 路径一致。
"""

import os
import sys

import pytest

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_HERE)

for _p in (_ROOT, os.path.join(_ROOT, "lib")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from fake_s3 import FakeS3  # noqa: E402
import s3queue  # noqa: E402


@pytest.fixture
def fake_s3():
    """把 s3queue 的 client 工厂换成内存实现，测完恢复。"""
    fake = FakeS3()
    s3queue.use_client_factory(lambda: fake)
    try:
        yield fake
    finally:
        s3queue.reset_client_factory()


@pytest.fixture
def work_root(tmp_path, monkeypatch):
    """把 worker 的工作根目录指到临时目录。"""
    import worker

    root = tmp_path / "work"
    monkeypatch.setattr(worker, "WORK_ROOT", root)
    return root
