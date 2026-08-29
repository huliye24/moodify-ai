"""Legacy core-package bootstrap — the single sanctioned sys.path entry point.

Phase B.1: all engine access to the legacy ``moodify-core-package``
implementation goes through ``engine.adapters``. This module is the only
place in the entire repository allowed to modify ``sys.path`` so the
legacy package (not yet pip-installed in every environment) becomes
importable.

When the core implementation is either installed as a dependency or its
code is fully migrated into ``engine/``, this module becomes a no-op and
can be deleted without touching any consumer.
"""

from __future__ import annotations

import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
_CORE_SRC = _REPO_ROOT / "moodify-core-package" / "src"

_BOOTSTRAPPED = False


def ensure_core_package() -> bool:
    """Make ``moodify-core-package/src`` importable once, if needed.

    Returns True when the legacy ``moodify`` package is importable
    (either it already was, or the bootstrap succeeded).
    """
    global _BOOTSTRAPPED
    if _BOOTSTRAPPED:
        return True
    _BOOTSTRAPPED = True
    try:
        import moodify  # noqa: F401  (already importable)
        return True
    except ImportError:
        pass
    if _CORE_SRC.is_dir():
        path_str = str(_CORE_SRC)
        if path_str not in sys.path:
            sys.path.insert(0, path_str)
        return True
    return False


def core_package_available() -> bool:
    """Whether the legacy core package can currently be imported."""
    try:
        import moodify  # noqa: F401
        return True
    except ImportError:
        return ensure_core_package()
