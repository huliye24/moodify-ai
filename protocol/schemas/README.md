# protocol/schemas/

Machine-readable schemas for the protocol layer.

## Schema ownership rule

Every schema in this repository belongs to exactly one owner. Duplicated definitions of the
same fact are the specific failure this directory exists to prevent.

| Owner | Location | Holds |
|---|---|---|
| **protocol** | here | Wire-format contracts that cross an implementation boundary |
| **core** | `moodify-core-package/src/moodify/*/schema/` | Contracts internal to Core |
| **app-local** | beside the app | UI-local shapes not crossing a boundary |
| **research-only** | `docs/`, `research/` | Prototypes, explicitly non-normative |

The canonical Core contracts are generated into `schemas/canonical/` from the pydantic
models in `moodify-core-package/src/moodify/contracts/` by
`scripts/generate_canonical_schemas.py`. **Do not hand-edit generated schemas**, and do not
re-declare a Core contract here.

## Why this rule is written down

Before 2026-10-03 the repository carried four copies each of `contribution.schema.json`,
`evidence.schema.json`, and `reputation-evidence.schema.json`. Two of those copies were live
and differed in `$schema` dialect — `draft-07` versus `2020-12` — while sharing a single
`$id`. Consumers validating against "the" schema could get different answers depending on
which file they found first.

That is the concrete harm a schema owner map prevents. If you need a shape that already
exists elsewhere, import or reference it — do not restate it.
