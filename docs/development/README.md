# Moodify Development Guide v1.0

**日期：** 2026-08-24
**阶段：** Moodify Entropy Reduction 002 — Mainline Context Freeze
**CANON_CHANGE：** `NO`
**执行状态：** 仅入口文件；未修改、删除、移动任何业务代码或目录。

---

## What to Maintain

Only these four systems are actively developed:

### 1. Web Player

```
apps/web/
```

- Primary user-facing listening surface
- Routes: `/` (home), `/listen`, `/t/[id]` (compat), `/library`
- Public Form aligned: Belief → Sound → Play → Proof
- Data source: Music BFF only

### 2. Android Player

```
apps/music-android/
```

- Mobile listening surface
- CI release: `moodify-music-*-release.yml`
- Contract shared with Web Player via Music BFF
- No second Android (`apps/android/` is frozen)

### 3. Music BFF

```
moodify-music-package/.../bff
```

- Single public API surface
- Endpoints: catalogue / track / playback URL / favorite / recent-play
- NOT responsible for: creator routes / license / support / billing / social

### 4. Cloud Production (Internal)

```
moodify-core-package/src/moodify/
```

- Ear / Auditory Intelligence
- v01_pipeline + data_factory
- NOT visible to users; only READY tracks reach the Player

---

## What NOT to Develop

Everything else is:

### Research

- MAMSE-001..016
- Physics / LLM / Lyric / Transcription
- Ear Workbench (`apps/ear-workbench/`)

### Experimental

- Reconstruction Job (billing not complete)
- reconstruction_factory
- era_diagnostic / identity_guard / reconstruction_objective (unmerged branches)

### Historical

- Legacy workflow engine
- Old Windows development
- Review/audit packages

### Frozen Products

- moodify-qa (second public product)
- moodify-pulse (second public product)
- Creator Studio, Marketplace, License, Billing, Enterprise API, Social features

---

## Decision Rule

Before adding anything new, ask:

> **Does this make users more willing to press Play again?**

If no → FREEZE.

---

## Active Development Entry Points

| File | Role |
|---|---|
| `docs/STATUS.md` | Current v1.0 working state |
| `docs/canon/CURRENT_CANON.md` | Product identity |
| `docs/canon/PRODUCT_BOUNDARY.md` | KEEP / FREEZE boundaries |
| `docs/cloud/README.md` | Cloud Production responsibilities |
| `docs/reduction/MAINLINE_DECLARATION.md` | Full boundary map |

---

## Testing

| System | Test Command |
|---|---|
| Web Player | `cd apps/web && npm run build && npm run lint` |
| Android Player | `cd apps/music-android && ./gradlew assembleRelease` |
| Music BFF | `cd moodify-music-package && pytest tests/` |
| Core | `cd moodify-core-package && pytest tests/` |

---

## Next

**Cloud Production 001** — Build the upload → process → READY → play loop:

```
Aliyun ECS
    |
    v
OSS (audio assets)
    |
    v
Worker
    |
    v
PolarDB (metadata)
    |
    v
Web Player
```

**下一步：Cloud Production 001。**