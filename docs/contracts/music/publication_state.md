# Moodify Music — Publication State Contract

Status: FROZEN (Rev.2 Phase B)

## States

```text
draft ──▶ published ──▶ unlisted ──▶ archived
  ▲          │             │
  └──────────┴─────────────┘ (explicit authorized transitions only)
```

| State | Meaning |
|---|---|
| draft | owned by creator, not publicly visible |
| published | public track URL `/t/{id}` live |
| unlisted | accessible via direct URL, hidden from discovery |
| archived | withdrawn; not served to listeners |

## Rules

- Publishing requires: ownership verified, a current version exists, basic
  required metadata valid.
- Publication transitions are recorded in `audit_events`
  (`track.published` etc.).
- `published_at` set on transition to published.
- Missing cover never blocks publication (Moodify vinyl default).

## Ear Boundary

Ear job status (queued/processing/succeeded/failed) is unrelated to
publication state. No mapping is performed automatically.
