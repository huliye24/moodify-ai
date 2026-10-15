#!/usr/bin/env python3
"""mirror.py — 把仓库的 ``ops/cloud_worker/`` **单向**生成到外部部署副本。

裁决（2026-10-15）：源码权威在仓库；``E:/亚马逊云/宁夏CPU节点/deploy/`` 降级为
**由本脚本生成的部署产物**，禁止反向成为源码权威。

流水线::

    仓库 ops/cloud_worker/            ← 唯一的源码
            │ mirror.py（本脚本，单向）
            ▼
    E:/亚马逊云/宁夏CPU节点/deploy/   ← 部署镜像 + 回滚副本
            │ tools/sync.py（SFTP）
            ▼
    /home/ubuntu/moodify-worker/.deploy/
            │ deploy.sh
            ▼
    /home/ubuntu/moodify-worker/

用法::

    python mirror.py --dry-run            # 只报告将要发生什么，一个字节都不写
    python mirror.py                      # 先备份现有镜像，再生成
    python mirror.py --manifest out.json  # 顺带写一份逐文件 sha256 清单
    python mirror.py --verify             # 只校验镜像与源码是否逐文件一致

纪律
----
- **单向**：只从仓库流向镜像，绝不反向读取。
- **先备份**：改动镜像前把现有内容整份复制到带时间戳的 backups/。
- **不镜像 __pycache__**：字节码是生成物，跨机器复用只会带来「改了 .py 仍加载缓存」。
- **逐文件可校验**：``--manifest`` 与 ``--verify`` 让「镜像 == 源码」成为可复现的断言。
- 不触碰 S3，不触碰节点。
"""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Tuple

REPO_ROOT = Path(__file__).resolve().parents[3]
SOURCE = REPO_ROOT / "ops" / "cloud_worker"
NODE_HOME = Path("E:/亚马逊云/宁夏CPU节点")
MIRROR = NODE_HOME / "deploy"
BACKUPS = NODE_HOME / "backups"

#: 不进镜像的东西：生成物与缓存。
EXCLUDE_DIRS = {"__pycache__", ".pytest_cache"}
EXCLUDE_SUFFIXES = {".pyc", ".pyo"}


def _iter_files(root: Path) -> Dict[str, Path]:
    """相对路径 → 绝对路径。排除缓存与字节码。"""
    out: Dict[str, Path] = {}
    if not root.is_dir():
        return out
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        rel = path.relative_to(root)
        if any(part in EXCLUDE_DIRS for part in rel.parts):
            continue
        if path.suffix in EXCLUDE_SUFFIXES:
            continue
        out[rel.as_posix()] = path
    return out


def sha256_of(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def manifest_of(root: Path) -> Dict[str, str]:
    """相对路径 → sha256。"""
    return {rel: sha256_of(p) for rel, p in sorted(_iter_files(root).items())}


def plan() -> Tuple[List[str], List[str], List[str]]:
    """返回 (新增, 更新, 删除) 的相对路径列表。"""
    src = manifest_of(SOURCE)
    dst = manifest_of(MIRROR)

    added = sorted(set(src) - set(dst))
    updated = sorted(rel for rel in set(src) & set(dst) if src[rel] != dst[rel])
    removed = sorted(set(dst) - set(src))
    return added, updated, removed


def backup() -> Path:
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    BACKUPS.mkdir(parents=True, exist_ok=True)
    target = BACKUPS / f"deploy-{stamp}"
    if target.exists():
        # 同一秒内跑两次也不能覆盖上一次的备份
        for n in range(2, 100):
            candidate = BACKUPS / f"deploy-{stamp}-{n}"
            if not candidate.exists():
                target = candidate
                break
    shutil.copytree(MIRROR, target)
    return target


def apply(added: List[str], updated: List[str], removed: List[str]) -> None:
    MIRROR.mkdir(parents=True, exist_ok=True)
    for rel in added + updated:
        dest = MIRROR / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(SOURCE / rel, dest)
    for rel in removed:
        target = MIRROR / rel
        if target.is_file():
            target.unlink()
    # 「不镜像 __pycache__」不只是不写进去，也包括把残留的清掉 ——
    # 否则镜像里会留着一份和源码不同步的字节码，正是「改了 .py 仍加载缓存」的成因。
    for cache in [p for p in MIRROR.rglob("*") if p.is_dir() and p.name in EXCLUDE_DIRS]:
        shutil.rmtree(cache, ignore_errors=True)

    for path in sorted(MIRROR.rglob("*"), key=lambda p: len(p.parts), reverse=True):
        if path.is_dir() and not any(path.iterdir()):
            path.rmdir()


def verify() -> int:
    """镜像与源码逐文件比对。一致返回 0，不一致返回 1 并把差异打出来。"""
    src = manifest_of(SOURCE)
    dst = manifest_of(MIRROR)
    missing = sorted(set(src) - set(dst))
    extra = sorted(set(dst) - set(src))
    differing = sorted(rel for rel in set(src) & set(dst) if src[rel] != dst[rel])

    print(f"源码 {len(src)} 个文件 · 镜像 {len(dst)} 个文件")
    if not (missing or extra or differing):
        print("一致：镜像与源码逐文件 sha256 相同。")
        return 0
    for label, items in (("缺失", missing), ("多余", extra), ("不一致", differing)):
        for rel in items:
            print(f"  {label}  {rel}")
    print("不一致 —— 请重跑 mirror.py（不要手工改镜像）。")
    return 1


def main() -> int:
    ap = argparse.ArgumentParser(description="把 ops/cloud_worker 单向生成到外部部署副本")
    ap.add_argument("--dry-run", action="store_true", help="只报告，不写盘")
    ap.add_argument("--verify", action="store_true", help="只校验一致性")
    ap.add_argument("--no-backup", action="store_true", help="跳过备份（镜像本就是生成物时）")
    ap.add_argument("--manifest", metavar="PATH", help="把源码逐文件 sha256 写到该路径")
    args = ap.parse_args()

    if not SOURCE.is_dir():
        print(f"找不到源码目录：{SOURCE}", file=sys.stderr)
        return 2

    if args.verify:
        return verify()

    added, updated, removed = plan()

    print(f"源码:  {SOURCE}")
    print(f"镜像:  {MIRROR}")
    print(f"计划:  新增 {len(added)} · 更新 {len(updated)} · 删除 {len(removed)}")
    for label, items in (("新增", added), ("更新", updated), ("删除", removed)):
        for rel in items:
            print(f"  {label}  {rel}")

    if args.manifest:
        data = {"source": str(SOURCE), "files": manifest_of(SOURCE)}
        Path(args.manifest).write_text(
            json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8"
        )
        print(f"\n源码清单已写：{args.manifest}（{len(data['files'])} 个文件）")

    if args.dry_run:
        print("\n--dry-run：未写入任何文件。")
        return 0

    if not (added or updated or removed):
        print("\n镜像已是最新，无需改动。")
        return 0

    if not args.no_backup and MIRROR.is_dir():
        target = backup()
        print(f"\n已备份现有镜像 → {target}")
    elif not MIRROR.is_dir():
        print("\n镜像目录不存在，将新建（无需备份）。")

    apply(added, updated, removed)
    print(f"\n镜像已更新：{MIRROR}")

    rc = verify()
    if rc == 0:
        print("下一步： python E:/亚马逊云/宁夏CPU节点/tools/sync.py")
    return rc


if __name__ == "__main__":
    sys.exit(main())
