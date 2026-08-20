# Legacy and Experimental Policy

**Status:** CANONICAL classification policy

**Public identity authority:** `AGENTS.md` → `docs/canon/*` → `docs/brand/public/*`

**Updated:** 2026-08-20

## Purpose

Moodify has evolved through multiple architectures.

The goal is not to erase that history. The goal is to prevent historical implementations from becoming competing authorities.

## Status Labels

Every significant subsystem should eventually be classifiable as:

### CANONICAL
Used by the supported mainline.

### EXPERIMENTAL
Active research; may change without compatibility guarantees.

### LEGACY
Previously used; preserved for compatibility or migration.

### HISTORICAL
Kept for research/provenance only.

### UNRESOLVED
Authority has not yet been decided by a human.

## Rules

1. A newer file is not automatically more canonical.
2. A larger subsystem is not automatically more canonical.
3. A branch being “ahead” does not make it authoritative.
4. Do not merge stale architecture wholesale.
5. Preserve tests before migration.
6. Prefer narrow adapters over duplicate orchestration systems.
7. When a legacy system is bypassed, say so explicitly.
8. Deletion requires a separate evidence-backed cleanup task.

## DSP / Post-Processing Reclassification

Legacy descriptions of Moodify as a post-processing system should not be treated as the current product identity.

The useful processing code remains active as the:

> Auditory Intervention Laboratory

## Documentation Rule

Historical papers can retain their original terminology.

Current public entry points must use the canonical **Moodify Music / Moodify Player** identity, the product principle **Listen. Then Play.**, and the primary action **Play**. Moodify Ear / Auditory Intelligence may appear only as an explicitly internal system or in research, evidence, and historical contexts.

Recommended current entry points:

- root `README.md`;
- root `AGENTS.md`;
- package README;
- architecture docs;
- current API/package metadata.

Historical documents should be clearly identifiable as `HISTORICAL`, `SUPERSEDED`, or `INTERNAL` if they contradict the current public identity. A historical document's original wording may be preserved for provenance, but its header must point readers to `docs/canon/CURRENT_CANON.md`.
