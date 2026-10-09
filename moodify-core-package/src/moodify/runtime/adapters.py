"""Bounded, read-only probe primitives.

Every adapter here answers one small question about *now* and nothing else.
None of them:

* writes to disk; * installs anything; * downloads anything;
* starts a production job; * prompts interactively; * runs unbounded.

Subprocess discipline (all of it explicit, none of it inherited):

* argument arrays only, never shell strings;
* an explicit timeout on every call — the child is killed on expiry, which
  ``subprocess.run`` performs before it re-raises ``TimeoutExpired``;
* ``stdin`` is ``DEVNULL`` so a child can never block on input;
* stdout/stderr are captured and truncated to a bounded size;
* python children are started with ``PYTHONUTF8=1``/``PYTHONIOENCODING=utf-8``
  — the GBK console trap is a runtime contract on China-region Windows
  (``docs/development/THINKPAD_RUNTIME_ARCHITECTURE.md`` §3).

An adapter that cannot conclude returns the honest "could not verify" fact;
it never guesses a positive.
"""

from __future__ import annotations

import importlib
import importlib.metadata
import json
import os
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

#: Bound for an executable version probe. Long enough for cold starts on
#: slow disks, short enough that a wedged binary cannot stall a diagnostic.
EXECUTABLE_TIMEOUT_S = 15.0

#: Bound for one external-venv import probe. ``import music21`` measures
#: ~5.4 s cold on the ThinkPad, ``import basic_pitch`` ~2.3 s; 60 s leaves
#: room for cold caches without letting a broken child run free.
VENV_TIMEOUT_S = 60.0

#: Output kept from any child. Enough for a first line and a short error,
#: never enough to buffer a runaway process's output.
_MAX_OUTPUT_CHARS = 2000

#: One version string kept, bounded.
_MAX_VERSION_CHARS = 120


# ── facts ─────────────────────────────────────────────────────────────────────

@dataclass(frozen=True)
class ExecutableFact:
    """What one executable probe learned."""

    path: str | None = None
    version: str | None = None
    found: bool = False
    ran: bool = False
    timed_out: bool = False
    error: str | None = None


@dataclass(frozen=True)
class VenvFact:
    """What one external-venv probe learned.

    ``python_version`` is the *venv interpreter's* version — the requirements
    of a venv-backed provider are satisfied by that interpreter, not by the
    one running the probe.
    """

    environment: str | None = None
    python_version: str | None = None
    packages: dict[str, dict[str, Any]] = field(default_factory=dict)
    """module name → {ok: bool, version: str | None, error: str | None}"""

    timed_out: bool = False
    error: str | None = None


# ── in-process probes ─────────────────────────────────────────────────────────

def platform_version() -> str:
    """Version of the interpreter running the probe."""
    return "{}.{}.{}".format(*sys.version_info[:3])


def version_at_least(version: str, minimum: str) -> bool:
    """Whether *version* >= *minimum*, comparing numeric dot segments."""
    def parts(text: str) -> tuple[int, ...]:
        out: list[int] = []
        for segment in text.split("."):
            digits = "".join(ch for ch in segment if ch.isdigit())
            out.append(int(digits) if digits else 0)
        return tuple(out)

    a, b = parts(version), parts(minimum)
    length = max(len(a), len(b))
    return a + (0,) * (length - len(a)) >= b + (0,) * (length - len(b))


def import_fact(module: str, distribution: str | None,
                pin: str | None) -> dict[str, Any]:
    """Import *module* in this process and read its distribution version.

    Importing is the verification: a distribution whose metadata is present
    can still fail to import (the ABI-mismatch failure mode this repository
    has already been bitten by), so metadata alone is not accepted as proof.
    """
    fact: dict[str, Any] = {
        "module": module,
        "ok": False,
        "version": None,
        "error": None,
        "pin": pin,
        "pin_ok": None,
    }
    try:
        importlib.import_module(module)
        fact["ok"] = True
    except Exception as exc:
        # Boundary: a broken native package can raise anything of its own at
        # import (the ABI-mismatch failure mode this repo has been bitten
        # by). Converting any failure into a fact is this adapter's whole
        # job; letting it crash the diagnostic would hide the very state
        # the probe exists to report.
        fact["error"] = _short(f"{type(exc).__name__}: {exc}")
        return fact
    if distribution:
        try:
            fact["version"] = importlib.metadata.version(distribution)
        except importlib.metadata.PackageNotFoundError:
            fact["version"] = None
        except Exception as exc:  # boundary: corrupt metadata is not absence
            fact["version"] = None
            fact["error"] = _short(f"metadata: {type(exc).__name__}: {exc}")
    if pin is not None and fact["version"] is not None:
        fact["pin_ok"] = fact["version"] == pin
    return fact


# ── executable probes ─────────────────────────────────────────────────────────

def executable_fact(resolver, *, timeout_s: float = EXECUTABLE_TIMEOUT_S) -> ExecutableFact:
    """Resolve an executable and run its version command, bounded.

    *resolver* is the canonical resolution function (for ffmpeg/ffprobe this
    is ``moodify.auditory.decode``'s memoized resolver — the probe reuses the
    runtime's own resolution semantics instead of inventing a second one).
    It raises when the binary is absent.
    """
    try:
        path = resolver()
    except Exception as exc:
        # Boundary: the resolver is pluggable and reports absence by raising
        # (FfmpegNotFound, OSError, …); any raise means "not resolvable here".
        return ExecutableFact(found=False, error=_short(f"{type(exc).__name__}: {exc}"))
    try:
        proc = subprocess.run(
            [path, "-version"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            stdin=subprocess.DEVNULL,
            timeout=timeout_s,
        )
    except subprocess.TimeoutExpired:
        return ExecutableFact(path=str(path), found=True, timed_out=True)
    except OSError as exc:
        return ExecutableFact(path=str(path), found=True,
                              error=_short(f"{type(exc).__name__}: {exc}"))
    stdout = _bounded(proc.stdout)
    stderr = _bounded(proc.stderr)
    version = None
    if proc.returncode == 0:
        first = next((line.strip() for line in stdout.splitlines() if line.strip()), "")
        version = _short(first[: _MAX_VERSION_CHARS]) if first else None
    return ExecutableFact(
        path=str(path),
        version=version,
        found=True,
        ran=proc.returncode == 0,
        error=None if proc.returncode == 0 else _short(f"exit {proc.returncode}: {stderr}"),
    )


# ── external venv probes ──────────────────────────────────────────────────────

#: The probe child: report the interpreter version and import each requested
#: module, then exit. One child per venv (not one per package) so the import
#: cost is paid once and the whole answer is one bounded JSON line. Imports
#: only — no inference, no model load, no network, no writes.
_VENV_PROBE_SCRIPT = r"""
import importlib, importlib.metadata, json, sys

packages = json.loads(sys.argv[1])
out = {
    "python": "%d.%d.%d" % sys.version_info[:3],
    "packages": [],
}
for module, distribution in packages:
    entry = {"module": module, "ok": False, "version": None, "error": None}
    try:
        importlib.import_module(module)
        entry["ok"] = True
        if distribution:
            try:
                entry["version"] = importlib.metadata.version(distribution)
            except importlib.metadata.PackageNotFoundError:
                entry["version"] = None
    except Exception as exc:
        entry["error"] = "%s: %s" % (type(exc).__name__, exc)
    out["packages"].append(entry)
print(json.dumps(out))
"""


def venv_python(venv_dir: Path) -> Path | None:
    """The interpreter of *venv_dir* on this platform, if it exists."""
    for relative in ("Scripts/python.exe", "bin/python"):
        candidate = venv_dir / relative
        if candidate.is_file():
            return candidate
    return None


def venv_fact(venv_dir: Path, packages: tuple[tuple[str, str | None], ...],
              *, timeout_s: float = VENV_TIMEOUT_S) -> VenvFact:
    """Run the interpreter of *venv_dir* to check it and its imports.

    Existence of the venv directory is not the fact — the interpreter has to
    run and the modules have to import. The child receives the package list
    as a JSON argument, its output is one JSON line from stdout, and
    ``PYTHONUTF8=1``/``PYTHONIOENCODING=utf-8`` are set so a cp936 console
    cannot turn a healthy import into a crash.
    """
    interpreter = venv_python(venv_dir)
    if interpreter is None:
        return VenvFact(environment=str(venv_dir), error="venv python not found")
    env = dict(os.environ)
    env["PYTHONUTF8"] = "1"
    env["PYTHONIOENCODING"] = "utf-8"
    arg = json.dumps([[module, distribution] for module, distribution in packages])
    try:
        proc = subprocess.run(
            [str(interpreter), "-c", _VENV_PROBE_SCRIPT, arg],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            stdin=subprocess.DEVNULL,
            timeout=timeout_s,
            env=env,
        )
    except subprocess.TimeoutExpired:
        return VenvFact(environment=str(venv_dir), timed_out=True)
    except OSError as exc:
        return VenvFact(environment=str(venv_dir),
                        error=_short(f"{type(exc).__name__}: {exc}"))
    if proc.returncode != 0:
        return VenvFact(environment=str(venv_dir),
                        error=_short(f"exit {proc.returncode}: {_bounded(proc.stderr)}"))
    payload = _last_json_line(proc.stdout)
    if payload is None:
        return VenvFact(environment=str(venv_dir),
                        error="probe output was not one JSON object")
    packages_out: dict[str, dict[str, Any]] = {}
    for entry in payload.get("packages", []):
        if isinstance(entry, dict) and isinstance(entry.get("module"), str):
            packages_out[entry["module"]] = {
                "ok": bool(entry.get("ok")),
                "version": entry.get("version"),
                "error": _short(entry["error"]) if entry.get("error") else None,
            }
    return VenvFact(
        environment=str(venv_dir),
        python_version=payload.get("python"),
        packages=packages_out,
    )


# ── environment resolution ────────────────────────────────────────────────────

#: A directory containing both of these is the repository root.
_REPO_MARKERS = ("moodify-core-package", "moodify-desktop")


def repo_root(start: Path | None = None) -> Path | None:
    """The repository root, found by walking up from this file.

    Returns ``None`` when the package runs outside a source checkout (for
    example a non-editable site-packages install) — the caller then has no
    default venv location to offer, which is a fact to report, not to guess
    around.
    """
    current = (start or Path(__file__)).resolve()
    for _ in range(8):
        if all((current / marker).is_dir() for marker in _REPO_MARKERS):
            return current
        if current.parent == current:
            return None
        current = current.parent
    return None


def venv_candidates(venv_name: str, env_var: str,
                    *, start: Path | None = None) -> tuple[Path, ...]:
    """Where a named external venv may live, in resolution order.

    Mirrors the desktop shell's contract (``moodify-desktop/src/runtime.js``):
    an explicit environment override first — the override is explicit and is
    validated by the probe like any other candidate — then the repository
    default. A missing default directory is not silently skipped past.
    """
    candidates: list[Path] = []
    override = os.environ.get(env_var, "").strip()
    if override:
        candidates.append(Path(override).expanduser().resolve())
    root = repo_root(start)
    if root is not None:
        default = (root / venv_name).resolve()
        if default not in candidates:
            candidates.append(default)
    return tuple(candidates)


# ── helpers ───────────────────────────────────────────────────────────────────

def _bounded(text: str | None) -> str:
    text = text or ""
    return text if len(text) <= _MAX_OUTPUT_CHARS else text[:_MAX_OUTPUT_CHARS] + "…"


def _short(text: str | None) -> str | None:
    if text is None:
        return None
    text = " ".join(text.split())
    return text if len(text) <= _MAX_VERSION_CHARS else text[: _MAX_VERSION_CHARS] + "…"


def _last_json_line(stdout: str) -> dict[str, Any] | None:
    """The child's payload is the last JSON object line of stdout."""
    for line in reversed((stdout or "").splitlines()):
        line = line.strip()
        if not line.startswith("{"):
            continue
        try:
            payload = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(payload, dict):
            return payload
    return None
