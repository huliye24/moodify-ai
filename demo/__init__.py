"""Moodify Demo — one upload → one Intelligence Report.

The demo pipeline contains NO analysis logic of its own.
It orchestrates the Moodify Intelligence Engine and renders the
unified Intelligence Report schema.

Chain:  demo → engine → analysis modules (core-package) → report generator
"""

__version__ = "0.1.0"
