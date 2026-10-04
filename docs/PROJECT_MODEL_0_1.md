# Project Model 0.1

Implementation documentation for `moodify.project` — the **Song Project**, the
persistent working object of a production.

Protocol string: `moodify.project/0.1`

> This document describes what is implemented. It is not a strategy document,
> and it does not describe capabilities that do not exist yet.

---

## What a Song Project is

A Song Project is the long-lived representation of **one piece of music being
produced**. It owns its source audio, it is reopened rather than recreated, and
it reserves a canonical place for every capability that will attach to it later.

Before this layer existed, Moodify's working object was an isolated audio file.
After it, the working object is a project directory that survives across
sessions and accumulates state.

A project is created from exactly one source audio file:

```python
from pathlib import Path
from moodify.project import create_project, load_project

created = create_project(Path("song.wav"), Path("projects"))
project_dir = Path("projects") / created.project_id
reopened = load_project(project_dir)

assert reopened.project_id == created.project_id
assert reopened.source.content_hash == created.source.content_hash
```

No GUI is opened, no network is used, and the source audio is never modified.

---

## Directory layout

```text
<projects_root>/
└── project_<32 lowercase hex chars>/
    ├── project.json
    ├── source/
    │   └── original.<ext>
    ├── stems/
    ├── analysis/
    ├── transcription/
    ├── score/
    ├── edits/
    ├── session/
    ├── renders/
    ├── verification/
    ├── exports/
    └── provenance/
```

`source/` and `project.json` are the only entries with content in Project Model
0.1. The remaining ten directories are **reserved**: they are created empty so
that later capabilities have a defined home instead of inventing one. Creating
them is not a claim that anything writes to them yet.

---

## Manifest

`project.json` is the project's canonical record, written with the repository's
existing canonical JSON conventions
(`moodify.contracts.serialization.to_canonical_json`): UTF-8, sorted keys,
compact separators, no `NaN`/`Infinity`.

Two typed models carry it, both inheriting `CanonicalModel` (frozen,
`extra="forbid"`):

**`ProjectAsset`** — a project-owned file:

```text
asset_id       asset_<32 hex>          canonical ID
kind           "source"                AssetKind
logical_path   "source/original.wav"   project-relative, POSIX separators
original_name  "song.wav"              the name the user supplied
media_type     "audio/wav"
content_hash   "sha256:<64 hex>"
size_bytes     int
created_at     tz-aware UTC datetime
```

**`ProjectManifest`** — the project:

```text
schema_version "1.0"                    canonical contract schema
protocol       "moodify.project/0.1"    project protocol (NOT schema_version)
project_id     project_<32 hex>
display_name   str | None
source         ProjectAsset
assets         { "source": asset_id }
stems, analysis, transcription, score, edits,
session, renders, verification, exports, provenance   all {} in 0.1
created_at     tz-aware UTC datetime
```

`protocol` and `schema_version` version **different things** and are deliberately
not conflated: `schema_version` versions the canonical contract shape; `protocol`
versions the persisted project format. The manifest type pins `protocol` with a
`Literal`, so any other value fails validation.

Two invariants are enforced by a model validator: the source asset must be of
kind `source`, and `assets["source"]` must reference it.

### Paths are relative

Canonical project records never store absolute paths. Every project-owned
artifact is addressed by a project-relative logical path, so a project directory
stays relocatable and a persisted path can never name a file outside it.

---

## Source immutability

The user's source file is **only ever read**.

Creation copies its bytes to `source/original.<ext>` with no transcoding, no
resampling, no normalization, no metadata rewrite and no DSP. Both the original
and the copy are hashed, and creation fails if the digests differ. The copy's
digest is what the manifest records.

```text
user's song.wav ──read──▶ source/original.wav
      │                          │
      └── sha256 ──┐   ┌── sha256 ┘
                  ▼   ▼
              must be equal
```

**Reopening verifies, it does not repair.** `load_project` re-checks that the
source exists, is a file, and matches the recorded size and digest. If the
content no longer matches, loading fails loudly — the recorded hash is never
silently updated, because a persisted project is evidence-bearing state.

### Failure behaviour

`create_project` never overwrites an existing directory (the target is created
with `exist_ok=False`, and a collision raises `ProjectExistsError`). If creation
fails partway, the directory this call created is removed, so a failed run
cannot leave a misleading half-written project behind. The user's input is never
deleted.

```text
ProjectError
├── ProjectValidationError   not a valid project / invalid source
├── ProjectExistsError       a project already exists at the target
└── ProjectIntegrityError    persisted content no longer matches its digest
```

### Path traversal

Persisted logical paths are treated as untrusted input. Two layers refuse an
escape:

1. `ProjectAsset` rejects absolute paths, backslash separators and any `..`
   component at validation time.
2. `_resolve_inside` resolves the candidate against the project root and
   requires the result to remain contained within it — decided on **resolved
   paths**, not string prefixes, so a sibling such as `project_x_evil` is not
   mistaken for `project_x`.

---

## Relationship to `ProductionCase`

They are different objects and both remain:

| | Song Project | `ProductionCase` |
| --- | --- | --- |
| Scope | one produced piece of music | one bounded unit of production/evidence work |
| Lifetime | long-lived, reopened | created, completed, closed |
| Contains | source asset + reserved domains | measurements, evidence, rules, judgments |
| Identity | `project_*` | `case_*` |

A Song Project will eventually contain **many** `ProductionCase` records. That
linkage is deliberately not built yet: `moodify.project` is a new, coexisting
layer, and `ProductionCase`, `analyze_to_case` and `reopen_case` are unchanged
by this work.

There is no `moodify project ...` CLI command in 0.1. The model is proven
through the Python API and its tests; the interface is the next task.

---

## Intentionally not implemented yet

Project Model 0.1 creates the place where a music project can exist. It does
not yet give anything a way to operate on it.

- **No CLI 2.0** — no `moodify project create/show/status`.
- **No Sound Protocol 0.3** and no Production Graph / DAG execution.
- **No stems, MIDI, MusicXML, score rendering, lyrics, mix or mastering.** The
  reserved directories are empty; the reserved manifest sections are `{}`.
- **No `ProductionCase` ↔ Project linkage** — no case is created or referenced
  by a project.
- **No project mutation.** `CanonicalModel` is frozen and there is no update
  API. Future updates should build a validated replacement manifest and
  atomically replace `project.json`.
- **No migration** of existing case bundles into projects.

### Notes for the next task

- `create_project` returns a `ProjectManifest`, not a wrapper object. If CLI 2.0
  needs the directory too, `project_root(projects_root, project_id)` derives it.
- `AUDIO_EXTENSIONS` is imported from `moodify.sound_protocol` rather than
  re-declared, to avoid a second extension registry. That module transitively
  imports `numpy` (via `v01_presets`), which is heavier than this layer strictly
  needs — if the project layer ends up on a minimal import path, relocating the
  constant to a lighter module is the fix.
- The reserved manifest sections are typed `dict[str, Any]` and JSON-frozen.
  The task that owns each domain should replace its placeholder with a typed
  model rather than growing the untyped dict.
