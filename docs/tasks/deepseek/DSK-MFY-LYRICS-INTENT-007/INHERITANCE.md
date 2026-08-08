# INHERITANCE — DSK-MFY-LYRICS-INTENT-007

## What the Next Executor Inherits

### Single entry (unchanged)
```powershell
py -3.12 -m moodify_bridge.cli refine prepare SPEC.yaml --output-dir NEW_DIR
```

### Optional lyrics evidence
Add `lyrics:` to OnePointSpec YAML. System collects structural evidence only. Body stays in `evidence/lyrics/`.

### Zero new vocabulary
The 12-word LANGUAGE_CANON is preserved. No sixth narrative center. Action sentence appends "Lyrics structural evidence was collected." when lyrics present.

### Four-layer evidence discipline
Source facts / Human declarations / Limited inference / Unknown. Edition 0.1 performs zero inference.

### Deterministic analysis
Section labels (regex), repeated lines (normalized SHA-256), line/paragraph counts. All reproducible.

### Security boundaries
Path traversal, NUL bytes, non-UTF-8, symlinks, directory paths → hard rejection (exit 2). Unknown rights → NEEDS_EVIDENCE (body not read). Body never in default surface.

### Compatible
All 72 tests pass. No schema/migration changes. Old CLI unchanged.
