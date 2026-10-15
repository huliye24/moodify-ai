#!/usr/bin/env python
"""Wave Field local runner — the Desktop <-> Core boundary for the v0 lane.

**Orchestration only.** Every algorithm lives in
``moodify-core-package/src/moodify/wavefield/`` (models / renderer / hearing /
search / record).  This script must never grow a DSP step: a second rendering
implementation in the shell is exactly what "One Core" forbids.

Protocol: **one JSON object in on stdin, one JSON object out on stdout.**

    {"action": "create-session", "case_dir": "...", "source_path": "..."}

Actions
-------
``create-session``  validate source, write session.json/search.json, render
                    A/B/C into the case, hear every candidate, write ORIGINAL.
``render-search``   re-render + re-hear an existing session (same source+policy).
``inspect``         read-only state; writes nothing.
``choose``          append one human choice to the append-only ledger.
``export``          materialise the chosen result + manifest into export/.

Every response carries ``ok``.  Failures print
``{"ok": false, "code": "...", "detail": "..."}`` and exit 1, so the shell can
surface a real reason instead of a bare exit code.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

# ── 显式 UTF-8：中文 Windows 的控制台默认代码页会把中文错误信息写坏 ──────────────
for stream in (sys.stdout, sys.stderr):
    try:
        stream.reconfigure(encoding="utf-8")  # type: ignore[union-attr]
    except (AttributeError, ValueError):  # pragma: no cover - non-reconfigurable stream
        pass


ACTIONS = ("create-session", "render-search", "inspect", "choose", "export")


def emit(payload: dict) -> None:
    """Exactly one JSON object on stdout, on a single line."""
    sys.stdout.write(json.dumps(payload, ensure_ascii=False) + "\n")
    sys.stdout.flush()


def fail(code: str, detail: str = "") -> int:
    emit({"ok": False, "code": code, "detail": detail})
    return 1


def require_case_dir(raw) -> Path:
    """A Wave Field lane only ever mounts inside a real case."""
    if not raw or not isinstance(raw, str):
        raise ValueError("case_dir is required")
    case_dir = Path(raw)
    if not case_dir.is_dir():
        raise FileNotFoundError(f"case directory does not exist: {case_dir}")
    if not (case_dir / "case.json").is_file():
        raise ValueError(f"not a Moodify case (no case.json): {case_dir}")
    return case_dir


def require_source(payload: dict, case_dir: Path) -> Path:
    """Source audio for a session: explicit ``source_path`` or the case's own record."""
    raw = payload.get("source_path")
    if not raw:
        recorded = case_dir / "source_path.json"
        if recorded.is_file():
            try:
                raw = json.loads(recorded.read_text(encoding="utf-8")).get("path")
            except (OSError, json.JSONDecodeError):
                raw = None
    if not raw or not isinstance(raw, str):
        raise ValueError("no source_path given and case/source_path.json has none")
    source = Path(raw)
    if not source.is_file():
        raise FileNotFoundError(f"source audio not found: {source}")
    return source


# ── actions ──────────────────────────────────────────────────────────────────


def action_create_session(payload: dict) -> dict:
    from moodify.wavefield.search import run_field_search

    case_dir = require_case_dir(payload.get("case_dir"))
    source = require_source(payload, case_dir)
    state = run_field_search(case_dir, source_path=str(source))
    return {
        "ok": True,
        "action": "create-session",
        "state": state,
        "detail": "已渲染 A / B / C 三个波场候选并完成听测。",
    }


def action_render_search(payload: dict) -> dict:
    from moodify.wavefield.record import read_session, wavefield_dir
    from moodify.wavefield.search import run_field_search

    case_dir = require_case_dir(payload.get("case_dir"))
    session = read_session(case_dir)
    if not session:
        return {
            "ok": False,
            "code": "SESSION_MISSING",
            "detail": f"没有可重渲染的波场会话（缺 session.json）：{wavefield_dir(case_dir)}",
        }
    source = Path(session["source_path"])
    if not source.is_file():
        return {
            "ok": False,
            "code": "SOURCE_NOT_FOUND",
            "detail": f"会话记录的源音频已不在：{source}",
        }
    state = run_field_search(case_dir, source_path=str(source))
    return {"ok": True, "action": "render-search", "state": state}


def action_inspect(payload: dict) -> dict:
    from moodify.wavefield.record import inspect

    case_dir = require_case_dir(payload.get("case_dir"))
    return {"ok": True, "action": "inspect", "state": inspect(case_dir)}


def action_choose(payload: dict) -> dict:
    from moodify.wavefield.record import (
        append_decision,
        candidate_path,
        inspect,
        read_case_id,
        read_field,
        read_render,
        read_session,
    )

    case_dir = require_case_dir(payload.get("case_dir"))
    kept = payload.get("kept")
    role = payload.get("role") or "creator"

    candidate_row = None
    field_row = None
    session = read_session(case_dir)
    if kept and kept != "ORIGINAL":
        audio = candidate_path(case_dir, kept)
        render = read_render(case_dir, kept)
        if not audio.is_file():
            return {
                "ok": False,
                "code": "CANDIDATE_MISSING",
                "detail": f"{kept} 还没有渲染产物：{audio}",
            }
        spec = read_field(case_dir, kept)
        field_row = spec.to_dict() if spec else None
        candidate_row = {
            "audio_path": str(audio),
            "output_sha256": render.output_sha256 if render else None,
            "field_id": spec.field_id if spec else None,
        }

    result = append_decision(
        case_dir,
        kept=kept,
        role=role,
        request_id=payload.get("request_id"),
        candidate=candidate_row,
        field=field_row,
        source_sha256=(session or {}).get("source_sha256"),
        engine_version=(session or {}).get("engine_version"),
        renderer=(session or {}).get("renderer"),
    )
    return {
        "ok": True,
        "action": "choose",
        "created": result["created"],
        "case_id": read_case_id(case_dir),
        "record": result["record"],
        "state": inspect(case_dir),
    }


def action_export(payload: dict) -> dict:
    from moodify.wavefield.record import export_chosen, reproduce_chosen

    case_dir = require_case_dir(payload.get("case_dir"))
    manifest = export_chosen(case_dir, kept=payload.get("kept"))
    # 导出即当场验证可复现：写进 case 的是「可重放」这一事实，而不是一句承诺。
    reproduced = reproduce_chosen(case_dir)
    return {
        "ok": True,
        "action": "export",
        "manifest": manifest,
        "reproduced": reproduced,
        "detail": (
            "已导出所选结果，并当场重渲染验证哈希一致。"
            if reproduced.get("ok")
            else "已导出，但重渲染哈希不一致——记录如实反映。"
        ),
    }


HANDLERS = {
    "create-session": action_create_session,
    "render-search": action_render_search,
    "inspect": action_inspect,
    "choose": action_choose,
    "export": action_export,
}


def run(payload: dict) -> dict:
    action = payload.get("action")
    if action not in HANDLERS:
        return {
            "ok": False,
            "code": "UNKNOWN_ACTION",
            "detail": f"action 必须是 {list(ACTIONS)} 之一，收到 {action!r}",
        }
    return HANDLERS[action](payload)


def main() -> int:
    if "--actions" in sys.argv:
        emit({"ok": True, "actions": list(ACTIONS)})
        return 0

    raw = sys.stdin.read()
    if not raw.strip():
        return fail("EMPTY_REQUEST", "stdin 需要一个 JSON 对象")
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError as exc:
        return fail("MALFORMED_REQUEST", str(exc))
    if not isinstance(payload, dict):
        return fail("MALFORMED_REQUEST", "顶层必须是 JSON 对象")

    try:
        response = run(payload)
    except FileNotFoundError as exc:
        return fail("SOURCE_NOT_FOUND", str(exc))
    except ValueError as exc:
        # FieldSpecError / WaveFieldRecordError are both ValueError subclasses and
        # both carry a machine-readable .code — prefer it when present.
        return fail(getattr(exc, "code", "INVALID_REQUEST"), getattr(exc, "detail", "") or str(exc))
    except RuntimeError as exc:
        return fail(getattr(exc, "code", "RUNNER_FAILED"), getattr(exc, "detail", "") or str(exc))
    except Exception as exc:  # noqa: BLE001 — last line of defence: the shell must see a reason
        return fail("UNEXPECTED_ERROR", f"{type(exc).__name__}: {exc}")

    if not response.get("ok"):
        return fail(
            response.get("code", "ACTION_FAILED"), response.get("detail", "") or ""
        )
    emit(response)
    return 0


if __name__ == "__main__":
    sys.exit(main())
