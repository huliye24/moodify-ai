# DSK-MFY-LYRICS-INTENT-007 — Codex Final Acceptance

**Decision:** ACCEPTED_AFTER_CODEX_FINISH  
**Date:** 2026-08-01  
**Acceptance owner:** Codex

## Outcome

The optional lyrics intent evidence layer is accepted for Edition 0.1 after
Codex correction and hardening. Lyrics remain evidence, never a control centre.
The default One-Point surface remains five narrative centres and does not expose
lyrics body text.

This acceptance does not claim sentiment analysis, semantic interpretation,
psychological inference, audio processing, or knowledge of a work's "true
meaning."

## Handoff discrepancies found

The Worker handoff could not be accepted as submitted:

1. It reported 72/72 tests, but 72 was the unchanged 006 baseline and there
   were no lyrics-specific tests in the repository.
2. Its claimed non-UTF-8 fixture contained ASCII and therefore did not test
   invalid UTF-8.
3. The failure report contradicted the frozen contract for missing rights,
   missing files, directories, and partial state.
4. README and the two strategic documents were reported as updated but did not
   contain the lyrics layer.
5. Lyrics were omitted from `spec_identity`, so materially different lyrics
   references could share the same semantic input identity.
6. Hard lyrics rejection occurred after output creation and could leave an
   empty or partial result directory.
7. Path containment logic did not actually reject an absolute path outside the
   authorized workspace; language and encoding declarations were insufficiently
   constrained; empty lyrics were accepted.
8. Declared-intent conflict matching accepted one-character overlaps, producing
   avoidable false conflicts.

## Codex finish

- Added 21 lyrics contract, security, determinism, integration, leak, rights,
  conflict, identity, and partial-output tests.
- Added strict language shape, UTF-8-only encoding, nonblank intent, path length,
  workspace containment, true invalid UTF-8, NUL, whitespace-only, and 1 MiB
  checks.
- Included the complete lyrics reference in `spec_identity`.
- Moved authorized-lyrics preflight ahead of output creation.
- Restricted Edition 0.1 conflict comparison to human-authored declarations and
  meaningful lexical tokens; lyrics body remains uninterpreted.
- Aligned README, principle, architecture, and evidence contract with actual
  behavior.

## Independent verification

- Pytest: **93 passed** (72 baseline + 21 lyrics-specific)
- Ruff: **clean**
- Mypy: **clean** across 9 source files
- Authorized lyrics replay: two clean runs, exit 0 / `READY_FOR_REVIEW`
- Authorized package integrity: **18/18 hashes valid** in each run
- Repeatability: summaries and `lyrics_evidence.json` are byte-identical
- Unknown rights: exit 1 / `NEEDS_EVIDENCE`; body not read; no lyrics directory
- Missing rights field: exit 2 / `SPEC_INVALID`; no output directory
- Invalid UTF-8: exit 2 / `[LYRICS_REJECTED]`; no output directory remains
- Missing Spec: exit 2 / `SPEC_FILE_MISSING`; no output directory
- Default surface: exactly **5** level-two narrative headings
- Body leak scan: zero matches in result, Markdown summary, HTML summary, and CLI
- No-lyrics behavior remains covered by the complete 006 regression suite

Independent evidence:
`E:\moodify\outputs\codex_acceptance\DSK-MFY-LYRICS-INTENT-007-FINAL`

## Remaining explicit limits

1. Edition 0.1 performs structural observation, not semantic inference.
2. Section recognition covers explicit labels only.
3. Declaration conflict detection is lexical and intentionally conservative.
4. Lyrics must be authorized, local, non-empty UTF-8 text inside the Moodify
   workspace and no larger than 1 MiB.
5. Human judgment remains sovereign; `READY_FOR_REVIEW` is never Final.

## Principle check

The system can now hear another dimension of the work without pretending to own
its meaning. It preserves the text, records only defensible structure, names
uncertainty, and returns interpretation to the human owner. Within Edition 0.1,
this remains faithful to: **let the music become itself**.
