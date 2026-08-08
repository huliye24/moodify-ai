"""一键部署 Moodify API 到阿里云演示机（120.55.191.146）。

用法：
    python scripts/deploy_aliyun.py

打包 moodify-core-package + moodify_runtime → SFTP 上传 → 解压 →
pip install -e → systemctl restart moodify-api → 验证 /health。

凭据默认取本脚本内置值（用户自有服务器），可用环境变量覆盖：
    MOODIFY_DEPLOY_HOST / MOODIFY_DEPLOY_USER / MOODIFY_DEPLOY_PASSWORD
"""

from __future__ import annotations

import os
import tarfile
import tempfile
from pathlib import Path

import paramiko

HOST = os.environ.get("MOODIFY_DEPLOY_HOST", "120.55.191.146")
USER = os.environ.get("MOODIFY_DEPLOY_USER", "root")
PASSWORD = os.environ.get("MOODIFY_DEPLOY_PASSWORD", "Abc18322935072")
REMOTE_TAR = "/root/moodify_deploy.tar.gz"
REMOTE_PACKAGE_DIR = "/root/moodify-core-package"
SERVICE = "moodify-api"

REPO_ROOT = Path(__file__).resolve().parents[2]
INCLUDE = (
    "moodify-core-package/src",
    "moodify-core-package/pyproject.toml",
    "moodify-core-package/configs",
    "moodify-core-package/capability_registry.json",
    "moodify_runtime",
)


def _build_tar(path: Path) -> None:
    with tarfile.open(path, "w:gz") as tar:
        for relative in INCLUDE:
            source = REPO_ROOT / relative
            if not source.exists():
                print(f"[skip] {relative} (missing)")
                continue
            tar.add(source, arcname=relative, filter=_exclude)


def _exclude(tarinfo: tarfile.TarInfo) -> tarfile.TarInfo | None:
    name = tarinfo.name
    if any(part in name for part in ("__pycache__", ".egg-info", ".git", "/outputs", "/docs")):
        return None
    return tarinfo


def _remote(client: paramiko.SSHClient, command: str, timeout: int = 900) -> str:
    stdin, stdout, stderr = client.exec_command(command, timeout=timeout)
    out = stdout.read().decode()
    err = stderr.read().decode()
    return out + (f"\n[stderr] {err[-500:]}" if err.strip() else "")


def main() -> int:
    with tempfile.TemporaryDirectory() as td:
        local_tar = Path(td) / "moodify_deploy.tar.gz"
        print(f"[1/5] 打包 {REPO_ROOT} -> {local_tar}")
        _build_tar(local_tar)
        print(f"      {local_tar.stat().st_size / 1024:.0f} KB")

        print(f"[2/5] 连接 {USER}@{HOST}")
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(HOST, port=22, username=USER, password=PASSWORD, timeout=15)

        try:
            print("[3/5] 上传并解压")
            sftp = client.open_sftp()
            sftp.put(str(local_tar), REMOTE_TAR)
            sftp.close()
            _remote(client, f"cd /root && tar -xzf {REMOTE_TAR}")

            print("[4/5] 安装依赖并重启服务")
            install = (
                f"cd {REMOTE_PACKAGE_DIR} && "
                "/root/venv/bin/pip install -q -e . && "
                f"systemctl restart {SERVICE} && sleep 4 && "
                f"systemctl is-active {SERVICE}"
            )
            print(_remote(client, install).strip())

            print("[5/5] 验证 /health")
            import json

            health = _remote(client, "curl -s -m 10 http://127.0.0.1:8000/health", timeout=60).strip()
            data = json.loads(health)
            print(f"      status={data.get('status')} version={data.get('version')}")
            print("DEPLOY OK")
        finally:
            client.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
