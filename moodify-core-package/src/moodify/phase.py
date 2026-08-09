"""Runtime product boundary for Moodify.

Phase I asks one question: ``Can machines learn to hear?``  Product surfaces
therefore default to the auditory loop.  Preserved Phase II laboratories can
only be exposed through an explicit experimental opt-in.
"""

from __future__ import annotations

import os


PHASE2_ENV = "MOODIFY_ENABLE_PHASE2_EXPERIMENTS"


def phase2_experiments_enabled() -> bool:
    """Return whether preserved Phase II surfaces may be exposed."""
    return os.getenv(PHASE2_ENV, "").strip().lower() in {"1", "true", "yes", "on"}
