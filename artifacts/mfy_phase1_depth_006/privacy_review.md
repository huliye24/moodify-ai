# Privacy Review

- Filesystem-only cache; no cloud, telemetry, API, Redis, database or object store.
- Cache identity uses source content hash, not filename/path.
- Portable decoded probe removes absolute source path.
- Cache supports size inspection, per-source clearing and full clearing through `moodify cache`.
- Original source bytes are not duplicated.
