# History Authority

History is an append-only bounded event list in LocalState schema v4:

```text
HistoryEntry { id, track_id, played_at, kind = PLAYBACK_STARTED }
```

`LibraryExperienceService` is the sole writer/reader. Retention is capped at the newest 5,000 events for Alpha. Repeated meaningful plays remain separate events. Recently Played sorts descending then uniquely projects by `track_id`. Library removal retains historical evidence, while projections safely omit a missing Track.
