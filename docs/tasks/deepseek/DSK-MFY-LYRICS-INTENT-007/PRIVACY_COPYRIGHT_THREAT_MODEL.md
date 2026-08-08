# PRIVACY_COPYRIGHT_THREAT_MODEL — DSK-MFY-LYRICS-INTENT-007

## Threat Surface

| Threat | Vector | Mitigation |
|---|---|---|
| Body text in stdout/stderr | CLI output, Typer exceptions | Stable error codes only; no body in messages |
| Body text in result.json | JSON serialization | Action/entrust only use summaries |
| Body text in summary.md/html | Markdown/HTML generation | Summary builder doesn't access body |
| Body text in exception stack traces | Python traceback | All expected errors caught; no bare exceptions with body |
| Path traversal | `..` in lyrics path | `_validate_lyrics_path` rejects `..` and resolves |
| Symlink escape | Symlinks to sensitive files | Rejected by `_validate_lyrics_path` |
| Large file DoS | >1MB lyrics file | Hard cap in `_load_lyrics_safe` |
| NUL byte injection | Binary disguised as text | Detected and rejected |
| Non-UTF-8 encoding | Malformed bytes | Detected and rejected |
| Copyright: body copied without rights | evidence/lyrics/original.txt | `rights_basis` guard; unknown → no copy |
| Metadata privacy: author identity inferred | Misuse of declared_intent | Prohibited inference; declared_intent is owner-provided |
| Evidence copy retention after deletion request | evidence/lyrics/ on disk | File responsibility of operator; documented in HANDOFF |

## Data Flow Security

```
Lyrics file (owner-provided, rights-authorized)
  → _validate_lyrics_path (path safety)
  → _load_lyrics_safe (encoding, size, NUL check)
  → original.txt copy → evidence/lyrics/
  → _analyze_lyrics_structure (deterministic stats)
  → lyrics_evidence.json → evidence/lyrics/
  → package_manifest.json (hash inventory)
Body text NEVER exits evidence/lyrics/ directory.
```

## False Positive Risk

Surface-level conflict detection (keyword overlap between declared_intent and must_avoid) has false positive risk. Conflicts ARE recorded but never auto-resolve. Human owner always decides.
