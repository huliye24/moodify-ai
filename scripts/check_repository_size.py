#!/usr/bin/env python3
"""Repository size guard — 阻止大型二进制再次进入源码仓库。

WHY THIS EXISTS
  Moodify 的 GitHub 仓库约 306 MB，一次完整 clone 在慢网络上要 50 分钟。
  体积几乎全部来自**历史里**的旧大型 blob（runs.tar.gz 99MB、
  moodify-mainline-codex.bundle 84MB、backend/*.exe、classes.dex、APK 等）。
  这些类型今天已被 .gitignore 正确阻止，但忽略规则只挡**未跟踪**文件——
  一旦某个大文件进过一次历史，它就永久留在克隆成本里。

  所以这里守的是**未来**：任何新的 >10 MiB 跟踪文件都必须在 PR 阶段失败，
  而不是等到某天有人抱怨克隆慢。

  本轮不改写历史（见 MOODIFY_REPOSITORY_SLIM_001 Decision A），
  因此这个守卫是唯一能防止体积继续增长的机制。

检查什么
  基于 `git ls-tree -r HEAD`，**只检查 Git 跟踪的文件**。
  刻意不扫描文件系统：venv / node_modules / 本地模型 / 构建产物会造成大量假阳性，
  而它们本来就不该、也不会被提交。

阈值
  单文件默认 10 MiB。不用 GitHub 的 100 MB 上限——那太晚了：
  我们的目标不是「不触发 GitHub 报错」，而是「保持源码仓库轻量」。
  当前最大的正常文件约 8.24 MB（baseline 测试音频），所以 10 MiB 留有余量。

allowlist
  `.repository-size-allowlist`：每行 `path`，以 `#` 开头为理由注释。
  allowlist 是**例外**，不是方便之门；每一项都必须写明为什么必须进 Git。

用法
  python scripts/check_repository_size.py            # 守卫（exit 1 = 超限）
  python scripts/check_repository_size.py --report   # 附带完整审计输出
"""
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
MIB = 1024 * 1024
DEFAULT_LIMIT_MIB = 10
ALLOWLIST_PATH = REPO_ROOT / '.repository-size-allowlist'

# HEAD tracked size 健康度（§22）。这是**仓库整体指标**，不是单文件上限。
HEAD_PREFERRED_MIB = 30
HEAD_WARNING_MIB = 50

# 这些类别默认不该出现在 Git 里。命中时会额外提示正确去处。
FORBIDDEN_HINTS = {
    '.exe': 'Windows 可执行文件 → GitHub Releases / Actions artifacts',
    '.msi': '安装包 → GitHub Releases',
    '.apk': 'Android 包 → GitHub Releases',
    '.zip': '归档 → Releases / Actions artifacts',
    '.7z': '归档 → Releases / Actions artifacts',
    '.rar': '归档 → Releases / Actions artifacts',
    '.tar': '归档 → Releases / Actions artifacts',
    '.gz': '归档 → Releases / Actions artifacts',
    '.tgz': '归档 → Releases / Actions artifacts',
    '.bundle': 'Git bundle → 不要进仓库',
    '.dll': '二进制库 → vendor 或 Releases',
    '.so': '二进制库 → vendor 或 Releases',
    '.dylib': '二进制库 → vendor 或 Releases',
    '.onnx': '模型权重 → 运行时下载 / Releases',
    '.pt': '模型权重 → 运行时下载 / Releases',
    '.pth': '模型权重 → 运行时下载 / Releases',
    '.safetensors': '模型权重 → 运行时下载 / Releases',
    '.ckpt': '模型权重 → 运行时下载 / Releases',
}


def git(*args: str) -> str:
    res = subprocess.run(['git', *args], cwd=REPO_ROOT, capture_output=True,
                         text=True, encoding='utf-8', errors='replace')
    if res.returncode != 0:
        raise RuntimeError(f'git {" ".join(args)} failed: {res.stderr.strip()}')
    return res.stdout


def tracked_files(source: str = 'HEAD') -> list[tuple[int, str]]:
    """要检查的 (size, path) 列表。

    source='HEAD'  → 已提交的树（CI 用这个：PR 里检查的就是将要合入的内容）
    source='index' → 暂存区（提交**之前**自检用；否则你会盯着一个还没反映
                     你刚 `git rm` 的旧数字，以为守卫坏了）
    """
    out: list[tuple[int, str]] = []
    if source == 'HEAD':
        for line in git('ls-tree', '-r', '-l', 'HEAD').splitlines():
            meta, _, path = line.partition('\t')
            parts = meta.split()
            if len(parts) >= 4 and parts[3].isdigit():
                out.append((int(parts[3]), path))
        return out

    # index：ls-files -s 给 <mode> <sha> <stage>\t<path>，大小需要查对象库
    entries: list[tuple[str, str]] = []
    for line in git('ls-files', '-s').splitlines():
        meta, _, path = line.partition('\t')
        parts = meta.split()
        if len(parts) >= 2:
            entries.append((parts[1], path))
    if not entries:
        return out
    res = subprocess.run(['git', 'cat-file', '--batch-check=%(objectsize)'],
                         cwd=REPO_ROOT, input='\n'.join(b for b, _ in entries),
                         capture_output=True, text=True, encoding='utf-8',
                         errors='replace')
    for (_blob, path), size_line in zip(entries, res.stdout.splitlines()):
        try:
            out.append((int(size_line.strip()), path))
        except ValueError:
            pass
    return out


def read_allowlist() -> dict[str, str]:
    """path -> reason。没有 allowlist 文件就返回空。"""
    if not ALLOWLIST_PATH.exists():
        return {}
    entries: dict[str, str] = {}
    pending_reason: list[str] = []
    for raw in ALLOWLIST_PATH.read_text(encoding='utf-8').splitlines():
        line = raw.strip()
        if not line:
            continue
        if line.startswith('#'):
            pending_reason.append(line.lstrip('#').strip())
            continue
        entries[line] = ' '.join(pending_reason) if pending_reason else '(no reason given)'
        pending_reason = []
    return entries


def category_hint(path: str) -> str | None:
    lower = path.lower()
    for ext, hint in FORBIDDEN_HINTS.items():
        if lower.endswith(ext):
            return hint
    return None


def main() -> int:
    ap = argparse.ArgumentParser(description='Fail when a large file enters Git.')
    ap.add_argument('--limit-mib', type=float, default=DEFAULT_LIMIT_MIB,
                    help=f'single-file limit in MiB (default {DEFAULT_LIMIT_MIB})')
    ap.add_argument('--report', action='store_true',
                    help='also print the full size audit')
    ap.add_argument('--index', action='store_true',
                    help='measure the staged index instead of HEAD (pre-commit self-check)')
    args = ap.parse_args()

    source = 'index' if args.index else 'HEAD'
    limit = int(args.limit_mib * MIB)
    files = tracked_files(source)
    allowlist = read_allowlist()
    total = sum(s for s, _ in files)

    print(f'repository size guard — {len(files)} tracked files ({source}), '
          f'{total / MIB:.1f} MiB total, single-file limit {args.limit_mib:g} MiB')

    if args.report:
        print()
        print('=== 最大的 30 个已跟踪文件 ===')
        for size, path in sorted(files, reverse=True)[:30]:
            print(f'{size / MIB:9.2f} MiB  {path}')

    # ── HEAD 健康度（软指标，只警告不失败）────────────────────────────────
    head_mib = total / MIB
    print()
    label = 'staged index' if source == 'index' else 'HEAD tracked size'
    if head_mib < HEAD_PREFERRED_MIB:
        print(f'{label}: {head_mib:.1f} MiB — preferred (<{HEAD_PREFERRED_MIB} MiB)')
    elif head_mib < HEAD_WARNING_MIB:
        print(f'::warning title=Repository size::{label} {head_mib:.1f} MiB '
              f'is in the {HEAD_PREFERRED_MIB}-{HEAD_WARNING_MIB} MiB band.')
    else:
        print(f'::warning title=Repository size::{label} {head_mib:.1f} MiB exceeds '
              f'{HEAD_WARNING_MIB} MiB — review required.')

    # ── 单文件违规 ─────────────────────────────────────────────────────────
    violations = [(s, p) for s, p in files if s > limit and p not in allowlist]

    if violations:
        print()
        print('=' * 72)
        for size, path in sorted(violations, reverse=True):
            print('ERROR: large tracked file detected')
            print(f'  path : {path}')
            print(f'  size : {size / MIB:.2f} MiB ({size} bytes)')
            print(f'  limit: {args.limit_mib:g} MiB')
            hint = category_hint(path)
            if hint:
                print(f'  use  : {hint}')
            print()
        print(f'{len(violations)} file(s) exceed the limit and are not allowlisted.')
        print()
        print('If such a file genuinely must live in Git, add its path to')
        print(f'  {ALLOWLIST_PATH.name}')
        print('with a comment stating why. The allowlist is for exceptions,')
        print('not for convenience.')
        return 1

    # ── allowlist 使用情况（透明化）────────────────────────────────────────
    if allowlist:
        print()
        print(f'allowlisted (>= limit): {len(allowlist)} entry(ies)')
        for path, reason in allowlist.items():
            present = any(p == path for _s, p in files)
            mark = 'present' if present else 'NOT PRESENT (stale entry?)'
            print(f'  {path} — {mark}')
            print(f'      reason: {reason}')

    print()
    print('repository size guard: OK')
    return 0


if __name__ == '__main__':
    sys.exit(main())
