"""adapter 层的公共件：Core 调用器、上下文、产物描述、错误分类。

纪律（方案 W2）
--------------
adapter 只做一件事：把 ``job_type`` 映射到**已有** Core/CLI 能力，并声明产物。
超时、下载、上传、状态转换、证据封装都归 worker，不归 adapter。
"""

from __future__ import annotations

import json
import os
import subprocess
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Sequence

from contract import NOT_ALIGNABLE

#: 产物角色，与 schemas/cloud/cpu_result.0.1.schema.json 的 outputs[].role 一致。
ROLES = ("report", "evidence", "log", "media", "manifest", "other")


class AdapterError(RuntimeError):
    """带稳定错误码的 adapter 失败。``code`` 直接进结果 JSON 的 error.code。"""

    def __init__(self, code: str, message: str, detail: str = ""):
        self.code = code
        self.message = message
        self.detail = detail
        super().__init__(f"{code}: {message}")


@dataclass(frozen=True)
class Artifact:
    """一件待上传的产物。

    ``key_suffix`` 是相对 ``output_prefix`` 的键名，必须是纯 POSIX 相对路径 ——
    不接受绝对路径或 ``..``，避免产物逃出自身前缀。
    """

    path: str
    role: str
    key_suffix: str

    def __post_init__(self) -> None:
        if self.role not in ROLES:
            raise ValueError(f"未知产物角色 {self.role!r}，允许：{', '.join(ROLES)}")
        suffix = self.key_suffix.replace("\\", "/")
        if suffix.startswith("/") or ".." in suffix.split("/") or not suffix:
            raise ValueError(f"产物键名非法：{self.key_suffix!r}")


@dataclass
class AdapterResult:
    """adapter 的返回：一个状态 + 一批产物 + 复现所需的版本信息。"""

    status: str
    artifacts: List[Artifact] = field(default_factory=list)
    params: Dict[str, Any] = field(default_factory=dict)
    core_version: str = NOT_ALIGNABLE
    tool_versions: Dict[str, str] = field(default_factory=dict)
    #: 领域结论摘要（如 judge 的 workflow_decision）。进证据，但**不**改判状态。
    verdict: Optional[Dict[str, Any]] = None


@dataclass
class AdapterContext:
    """worker 交给 adapter 的运行环境。"""

    job: Dict[str, Any]
    work_dir: Path
    input_path: Path
    out_dir: Path
    scratch_dir: Path
    core: "CoreRunner"
    timeout_seconds: int
    log: Callable[[str], None] = print

    @property
    def params(self) -> Dict[str, Any]:
        return dict(self.job.get("params") or {})


def read_params(ctx: AdapterContext, allowed: Sequence[str], required: Sequence[str] = ()) -> dict:
    """取并校验 adapter 自己的参数。

    未知键必须显式拒绝：静默忽略会让生产者以为参数生效了。
    """
    params = ctx.params
    unknown = sorted(set(params) - set(allowed))
    if unknown:
        raise AdapterError(
            "SCHEMA_INVALID",
            f"{ctx.job['job_type']} 不认识参数：{', '.join(unknown)}",
            f"允许：{', '.join(sorted(allowed)) or '（无）'}",
        )
    missing = [k for k in required if k not in params]
    if missing:
        raise AdapterError(
            "SCHEMA_INVALID",
            f"{ctx.job['job_type']} 缺少必需参数：{', '.join(missing)}",
        )
    return params


class CoreRunner:
    """以子进程方式调用 Core 的唯一通路。

    子进程而不是 in-process：analyze 要跑几分钟、峰值内存数 GB，worker 必须能施加
    超时与内存上限，并且不能因 Core 的 import 失败而一起死掉。
    """

    def __init__(
        self,
        python_exe: str,
        core_entry: str,
        env: Optional[Dict[str, str]] = None,
        log: Callable[[str], None] = print,
    ):
        self.python_exe = python_exe
        self.core_entry = core_entry
        self.env = env
        self.log = log
        self._version: Optional[str] = None

    def _run(self, argv: Sequence[str], timeout: int) -> subprocess.CompletedProcess:
        env = dict(os.environ)
        if self.env:
            env.update(self.env)
        env.setdefault("PYTHONUNBUFFERED", "1")
        try:
            return subprocess.run(
                [self.python_exe, self.core_entry, *argv],
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=timeout,
                env=env,
            )
        except subprocess.TimeoutExpired as exc:
            raise AdapterError(
                "TIMEOUT", f"Core 调用超过 {timeout}s 未返回", f"argv={list(argv)}"
            ) from exc

    def version(self) -> str:
        """运行期 Core 版本。取不到写 not_alignable —— 不猜、不写死。"""
        if self._version is not None:
            return self._version
        try:
            info = self.call(["version"], timeout=60)
            self._version = info.get("core_version", NOT_ALIGNABLE)
        except AdapterError:
            self._version = NOT_ALIGNABLE
        return self._version

    def call(self, argv: Sequence[str], timeout: int, out_path: Optional[str] = None) -> dict:
        """跑一条 core_entry 命令并返回解析后的信封。

        失败一律抛 :class:`AdapterError`，错误码按「是环境问题还是任务问题」分类：
        Core 装不上 → CORE_NOT_AVAILABLE（可重试）；Core 跑了但拒绝 → CORE_JOB_FAILED（不可重试）。
        """
        if out_path:
            argv = [*argv, "--out", out_path]
        proc = self._run(argv, timeout)

        payload: Optional[dict] = None
        if out_path and os.path.isfile(out_path):
            try:
                with open(out_path, "r", encoding="utf-8") as f:
                    payload = json.load(f)
            except (OSError, json.JSONDecodeError):
                payload = None

        if payload is None and proc.stdout.strip():
            try:
                payload = json.loads(proc.stdout)
            except json.JSONDecodeError:
                payload = None

        if payload is None:
            raise AdapterError(
                "CORE_JOB_FAILED",
                "core_entry 未产出可解析的 JSON",
                f"rc={proc.returncode} stderr={proc.stderr[-400:]!r}",
            )

        if payload.get("ok") is False or proc.returncode != 0:
            err_type = str(payload.get("error_type", ""))
            # 环境问题（Core 没装）与任务问题（Core 跑了并拒绝）必须分得开：
            # 前者装上就能重试，后者重投多少次都一样。
            code = "CORE_NOT_AVAILABLE" if err_type in ("ModuleNotFoundError", "ImportError") \
                else "CORE_JOB_FAILED"
            raise AdapterError(
                code,
                payload.get("error", "Core 调用失败"),
                f"{err_type}: {payload.get('traceback', '')[-600:]}",
            )

        return payload


def ffmpeg_version(ffmpeg_exe: str) -> str:
    """ffmpeg 版本首行。取不到写 not_alignable。"""
    try:
        proc = subprocess.run(
            [ffmpeg_exe, "-version"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=30,
        )
        first = (proc.stdout or "").splitlines()
        return first[0].strip() if first else NOT_ALIGNABLE
    except (OSError, subprocess.SubprocessError):
        return NOT_ALIGNABLE


def run_tool(argv: Sequence[str], timeout: int, code: str = "TOOL_FAILED") -> subprocess.CompletedProcess:
    """跑一个外部工具（如 ffmpeg）。超时与失败都转成带码的 AdapterError。"""
    try:
        proc = subprocess.run(
            list(argv),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=timeout,
        )
    except subprocess.TimeoutExpired as exc:
        raise AdapterError("TIMEOUT", f"{argv[0]} 超过 {timeout}s 未返回") from exc
    except OSError as exc:
        raise AdapterError(code, f"无法执行 {argv[0]}", str(exc)) from exc
    if proc.returncode != 0:
        raise AdapterError(
            code, f"{Path(argv[0]).name} 退出码 {proc.returncode}", (proc.stderr or "")[-600:]
        )
    return proc


def artifact_from(ctx: AdapterContext, path: Path, role: str, key_suffix: str) -> Artifact:
    return Artifact(path=str(path), role=role, key_suffix=key_suffix)


def write_json_artifact(
    ctx: AdapterContext, name: str, payload: dict, role: str = "report"
) -> tuple[Artifact, Path]:
    """把一份 JSON 写进 out_dir 并登记为产物。"""
    path = ctx.out_dir / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2, default=str), encoding="utf-8"
    )
    rel = path.relative_to(ctx.out_dir).as_posix()
    return Artifact(path=str(path), role=role, key_suffix=rel), path


def elapsed(started: float) -> float:
    return round(time.time() - started, 3)


#: 默认不上传的中间产物后缀。.npz 是分析中间态（数 MB~数十 MB），不是证据本身。
DEFAULT_SKIP_SUFFIXES = (".npz", ".pyc")


def collect_tree_artifacts(
    ctx: AdapterContext,
    root: Path,
    *,
    skip_suffixes: Sequence[str] = DEFAULT_SKIP_SUFFIXES,
    max_bytes: Optional[int] = None,
) -> tuple[List[Artifact], List[Dict[str, Any]]]:
    """把 ``root`` 下的文件登记为产物。

    返回 ``(artifacts, skipped)``。**跳过的必须被记录并写进结果** —— 静默截断会让
    「跑完了」读成「证据齐了」。
    """
    artifacts: List[Artifact] = []
    skipped: List[Dict[str, Any]] = []

    for path in sorted(root.rglob("*")):
        if not path.is_file():
            continue
        rel = path.relative_to(root).as_posix()
        if path.suffix.lower() in skip_suffixes:
            skipped.append({"key_suffix": rel, "reason": "intermediate"})
            continue
        size = path.stat().st_size
        if max_bytes is not None and size > max_bytes:
            skipped.append({"key_suffix": rel, "reason": f"size {size} > {max_bytes}"})
            continue
        artifacts.append(Artifact(path=str(path), role=_role_for(rel), key_suffix=rel))

    return artifacts, skipped


def _role_for(rel: str) -> str:
    name = rel.rsplit("/", 1)[-1].lower()
    if name.startswith("report"):
        return "report"
    if name.endswith(".png"):
        return "evidence"
    if name.endswith(".json") or name.endswith(".jsonl") or name.endswith(".md"):
        return "evidence"
    return "other"
