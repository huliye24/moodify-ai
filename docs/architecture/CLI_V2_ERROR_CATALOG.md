# Moodify CLI v2 Error Catalog

| Code | Meaning |
|---|---|
| `PROJECT_NOT_FOUND` / `PROJECT_INVALID` | Missing or invalid canonical project |
| `UNSAFE_PROJECT_PATH` | Project root is an unsupported link/junction |
| `OUTPUT_EXISTS` | Refuses to overwrite a project or render directory |
| `SOURCE_INVALID` / `SOURCE_HASH_MISMATCH` | Source missing, invalid or changed |
| `INTENT_INVALID` / `PLAN_UNSAFE` | Intent schema or parameter safety failed |
| `ASSET_REQUIRED` / `PLAN_NOT_FOUND` / `RUN_NOT_FOUND` | Referenced entity is unavailable |
| `DRY_RUN_PLAN` | Dry-run plans are not executable |
| `CAPABILITY_UNSUPPORTED` | Requested declared capability is unavailable |
| `RENDER_FAILED` | Renderer returned a failure |
| `VERIFICATION_FAILED` | Artifact or source evidence did not verify |
| `COMMAND_FAILED` | Unclassified command or I/O failure |

All errors are machine-readable, emitted on stderr and paired with a non-zero exit code.
