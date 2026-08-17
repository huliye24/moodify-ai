# MFY-CR-P02 — Authority Diff

Audit result of every authority document against the new product direction
(2026-08-17). Classification values: KEEP_AS_IS / KEEP_WITH_POINTER /
UPDATE_MINIMALLY / SUPERSEDE / HISTORICAL_ONLY.

## Classification

| Document | Classification | Reason |
|---|---|---|
| `AGENTS.md` (root) | UPDATE_MINIMALLY | Product identity block conflicted with reconstruction-first direction. Updated minimally: product objective added, Ear kept as internal foundation, authority order gained the Constitution. Everything else (three disciplines, asset loop, judgment authority, DoD, single ProductionCase/Evidence/state machine, human listening authority) untouched. |
| `README.md` | UPDATE_MINIMALLY | Product entry updated to reconstruction-first; Ear documented as internal foundation; "implementation remains partial, not production-proven" statement added. Not a marketing rewrite. |
| `docs/PHASE1_CONSTITUTION.md` | KEEP_WITH_POINTER | Internal data-foundation constitution stays LIVE and unchanged; the new Constitution references it. Its "not a consumer product" statement refers to the internal research infrastructure, not the new product. |
| `docs/AUDITORY_INTELLIGENCE_ARCHITECTURE.md` | KEEP_AS_IS | Internal Ear architecture remains valid. |
| `docs/ASSET_MODEL.md` | KEEP_AS_IS | Evidence/asset loop remains the internal evidence model. |
| `docs/LEGACY_AND_EXPERIMENTAL_POLICY.md` | KEEP_AS_IS | Classification policy is direction-neutral. |
| `docs/REPOSITORY_STATUS.md` | KEEP_WITH_POINTER | Status/verification snapshot; its 2026-08-14 identity line predates the constitution. Pointer added via Constitution (not rewritten — it is a dated status record). |
| `docs/CODE_FREEZE_POLICY.md` | KEEP_AS_IS | Data-foundation freeze authority, unchanged; reconstruction phase adds no new code in P02. |
| `docs/PROJECT_SNAPSHOT_*.md` | HISTORICAL_ONLY | Dated snapshots; retain for provenance. |
| `docs/PR_DISPOSITION.md` | HISTORICAL_ONLY | Record of PR handling; retained as-is. |

## Conflicts found and resolved

1. **AGENTS.md "Do not regress ... to preset/DSP product"** — kept (the
   reconstruction identity does not regress; the sentence remains correct and
   now also protects against reconstruction being treated as presets).
2. **PHASE1_CONSTITUTION.md §1 "not a consumer product"** — no conflict: it
   governs the internal research infrastructure. The new Constitution governs
   the product. Relationship recorded via pointer.

## No second authority

- One ProductionCase / Evidence / state machine: unchanged (root AGENTS.md
  `Change Discipline` + PHASE1_CONSTITUTION.md §3 preserved verbatim).
- Human listening authority: unchanged (root AGENTS.md `Judgment Authority`
  preserved verbatim).
- No new state machine, no new evidence system was created.
