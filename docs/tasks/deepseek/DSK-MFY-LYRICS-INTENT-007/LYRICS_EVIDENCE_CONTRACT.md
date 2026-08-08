# LYRICS_EVIDENCE_CONTRACT — DSK-MFY-LYRICS-INTENT-007

**Status:** Frozen before any code change.

## 1. Input Contract: LyricsRef (within OnePointSpec)

### Fields

| Field | Type | Required | Meaning |
|---|---|---|---|
| `path` | `str` | YES (if lyrics present) | Absolute or relative path to UTF-8 .txt |
| `language` | `str` (BCP-47) | YES | e.g. `zh-CN`, `en`, `ja` |
| `version` | `str` (enum) | YES | `authorized-draft`, `authorized-final`, `owner-provided` |
| `rights_basis` | `str` (enum) | YES | `owner-provided`, `public-domain`, `licensed`, `unknown` |
| `declared_intent` | `str` (1–500 chars) | NO | Human-authored; never machine-generated |
| `encoding` | `str` | NO (default `utf-8`) | Only `utf-8` accepted |

### Validation Rules

1. `rights_basis` must be in `{owner-provided, public-domain, licensed}` to read/analyze text body.
2. `rights_basis: unknown` → `NEEDS_EVIDENCE`; the spec reference is retained but no lyrics directory is created and the body is NOT read.
3. `rights_basis` missing → strict schema rejection (exit 2); body NOT read.
4. File does not exist → rejected (exit 2).
5. File is directory, symlink, junction, or not a regular file → rejected (exit 2).
6. Path contains `..` or resolves outside working scope → rejected (exit 2).
7. File exceeds size cap (1 MB) → rejected.
8. File contains NUL bytes or is not valid UTF-8 → rejected.
9. `language` must use the accepted BCP-47-shaped subset (e.g. `zh-CN`, `en`). `mixed` is an explicit declaration; no automatic language inference occurs.
10. An empty or whitespace-only file → rejected (exit 2).
11. `encoding` may only be `utf-8`; a different declaration is a schema rejection.

### When LyricsRef is Absent

OnePointSpec without `lyrics` field → behavior identical to 006. No lyrics evidence generated. Action field unchanged.

## 2. Output: LyricsEvidence

### Structure (written to `evidence/lyrics_evidence.json`)

```json
{
  "schema_version": "1.0.0",
  "source_facts": {
  "path": "authorized local evidence path",
    "sha256": "...",
    "byte_size": 1234,
    "language": "zh-CN",
    "version": "authorized-draft",
    "rights_basis": "owner-provided",
    "line_count": 40,
    "paragraph_count": 8,
    "has_explicit_section_labels": true,
    "section_labels_found": ["Verse 1", "Chorus", "Verse 2", "Bridge", "Chorus"]
  },
  "declared_intent": "第一人称在克制与释放之间移动。",
  "structural_observations": {
    "sections": [
      {"label": "Verse 1", "start_line": 1, "end_line": 8, "line_count": 8},
      {"label": "Chorus", "start_line": 9, "end_line": 12, "line_count": 4}
    ],
    "repeated_lines": [
      {"text_hash": "sha256_of_normalized_line", "occurrences": 4, "locations": [9, 19, 29, 39]}
    ],
    "normalized_repetition_count": 4
  },
  "uncertainties": [
    "Section labels are explicit in text; not machine-classified.",
    "declared_intent is author-provided; no machine inference was performed."
  ],
  "conflicts": []
}
```

### Rules

- `source_facts` only contains verifiable, reproducible facts.
- `declared_intent` is echoed verbatim from input; never generated.
- `structural_observations` use deterministic algorithms only (label regex, line hashing).
- `uncertainties` is always populated when any interpretation is involved.
- `conflicts` records any tension between lyrics evidence and `must_preserve`/`must_avoid`.

## 3. Evidence Package

All lyrics-derived files go under `evidence/lyrics/`:

```text
evidence/lyrics/
  original.txt           # bit-for-bit copy (only if rights allow)
  original.txt.sha256    # SHA-256 of original
  lyrics_evidence.json   # the structured evidence document
```

`package_manifest.json` in `evidence/` covers all lyrics evidence files with SHA-256.

## 4. Default Surface Rules

- Body text NEVER appears in `result.json`, `summary.md`, `summary.html`, or CLI stdout.
- Default summary may say "Lyrics evidence was collected and is available in evidence/lyrics/."
- Action field: if lyrics present, append "Lyrics structural evidence was collected." — no body text.
- Entrust field: unchanged in structure; may note owner should review lyrics evidence.

## 5. Conflict Rules

When lyrics evidence reveals tension with OnePointSpec:

| Condition | Status | Action |
|---|---|---|
| declared_intent contradicts must_preserve | NEEDS_EVIDENCE | Entrust to owner |
| Lyrics body contains words matching must_avoid | WARN | Record in conflicts; do not block |
| Rights basis unknown or missing | NEEDS_EVIDENCE | Body not read |

## 6. State Transitions

```
No lyrics in spec → normal 006 flow
Lyrics + valid rights → process → READY_FOR_REVIEW (or FAILED if hash/format issues)
Lyrics + unknown rights → NEEDS_EVIDENCE → owner provides rights → READY_FOR_REVIEW
Lyrics + missing/path/format/empty failure → exit 2 (no traceback, no partial package)
Lyrics + conflict → NEEDS_EVIDENCE (body processed, conflict recorded)
```

## 7. Compatibility

- Zero modification to existing OnePointSpec schema — `lyrics` is optional.
- Zero modification to DuckDB, migrations, or store.py.
- Old `refine prepare` without lyrics in spec → identical behavior.
- All 006 tests continue to pass unchanged.
