# Playback Restore Policy

Current Track identity, position and volume are restored. Position is finite, non-negative and clamped to loaded duration; volume clamps to 0–1. `last_status` is policy evidence only: even previous PLAYING loads as READY and `play()` is never called.

If Track exists but source is unavailable, its identity remains current with `SOURCE_UNAVAILABLE/ERROR`; Queue remains. Removed/unknown Track IDs are dropped during relation validation and the session falls back safely.
