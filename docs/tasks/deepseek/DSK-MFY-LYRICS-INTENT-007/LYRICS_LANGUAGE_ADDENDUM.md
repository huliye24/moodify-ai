# LYRICS_LANGUAGE_ADDENDUM — DSK-MFY-LYRICS-INTENT-007

## Principle

This addendum extends LANGUAGE_CANON.md without adding a sixth narrative center or increasing the 12-word external vocabulary.

## Default Surface: Still Five Centers

| Center | With lyrics present | Without lyrics |
|---|---|---|
| Essence | Unchanged | Unchanged |
| Protect | Unchanged | Unchanged |
| Allow | Unchanged | Unchanged |
| Action | Appended: "Lyrics structural evidence was collected." | Unchanged |
| Entrust | Unchanged (may note: "Lyrics evidence available for review") | Unchanged |

## Permitted Language on Default Surface

The only additional phrases permitted when lyrics evidence exists:

- "Lyrics structural evidence was collected."
- "Lyrics evidence is available in evidence/lyrics/."
- "Declared intent was recorded."

## Forbidden on Default Surface

- Any lyrics body text (even one line)
- "The lyrics are about..."
- "The song expresses..."
- Sentiment/emotion labels
- Section content summaries
- Word frequency statistics
- "Key themes identified: ..."
- Any inference about author

## Internal Vocabulary (evidence-only, not in default surface)

| Term | Where used |
|---|---|
| `source_facts` | `evidence/lyrics/lyrics_evidence.json` |
| `declared_intent` | Input field + evidence |
| `structural_observations` | `evidence/lyrics/lyrics_evidence.json` |
| `section_labels` | `evidence/lyrics/lyrics_evidence.json` |
| `repeated_lines` | `evidence/lyrics/lyrics_evidence.json` |
| `uncertainties` | `evidence/lyrics/lyrics_evidence.json` |
| `conflicts` | `evidence/lyrics/lyrics_evidence.json` |

## No New Canonical Words

The 12-word LANGUAGE_CANON is preserved unchanged. No term is added, removed, or redefined.
