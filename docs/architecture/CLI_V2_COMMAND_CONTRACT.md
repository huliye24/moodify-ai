# Moodify CLI v2 Command Contract

The official entry point is `python -m moodify` or the installed `moodify` console command.

Available v1 commands:

```text
version
capabilities
project init PROJECT_DIR
project inspect PROJECT_DIR
asset import PROJECT_DIR INPUT --copy-mode reference
plan create PROJECT_DIR --intent JSON_OR_FILE [--dry-run]
run execute PROJECT_DIR --plan-id ID --output-dir NEW_DIR
run verify PROJECT_DIR --run-id ID
```

Successful stdout contains exactly one UTF-8 JSON document. Errors contain exactly one UTF-8 JSON document on stderr and return non-zero. Every result includes `schema_version`, `command` and `status`.

Exit-code classes: `0` success; `2` invalid request, missing project, unsafe plan or existing output; `3` unexpected command/I/O failure; `4` source-integrity or render failure; `5` verification failure.

The CLI never overwrites an existing project or render directory. `--dry-run` plans cannot execute. Reference imports are idempotent by resolved path plus SHA-256. Other copy modes fail explicitly until implemented.

