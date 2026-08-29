"""Temporary compatibility bootstrap for the legacy core package.

Phase B T0.5: the engine delegates real analysis work to the existing,
tested implementation in ``moodify-core-package/src/moodify``. Until the
T1 shim/adapter mechanism lands, this module makes the legacy package
importable when it is not pip-installed in the active environment.

This shim will be REMOVED when engine modules own migrated code
(see docs/MIGRATION_PLAN_AND_TASKS.md, task T1).
"""

from __future__ import annotations

import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[1]
_CORE_SRC = _REPO_ROOT / "moodify-core-package" / "src"

_BOOTSTRAPPED = False


def ensure_core_package() -> None:
    """Add ``moodify-core-package/src`` to sys.path once, if needed."""
    global _BOOTSTRAPPED
    if _BOOTSTRAPPED:
        return
    _BOOTSTRAPPED = True
    try:
        import moodify  # noqa: F401  (already importable)
        return
    except ImportError:
        pass
    if _CORE_SRC.is_dir():
        path_str = str(_CORE_SRC)
        if path_str not in sys.path:
            sys.path.insert(0, path_str)
