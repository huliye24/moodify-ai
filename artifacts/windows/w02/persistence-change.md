# Persistence Change

Schema changed from v1 to v2 by adding:

```text
library:
  tracks: LibraryTrack[]
```

Writes continue to use temporary-file-plus-rename atomic replacement. Library mutations flush immediately so import/remove cannot remain only in memory. Validation rejects malformed Track records without clearing otherwise valid state.

On first v1 load, the original file is copied once to `local-state.json.v1.bak`, the v2 state is atomically written, and repeat startup observes v2 without repeating migration. Existing playback/window/app fields are retained. Renderer playlist localStorage is neither cleared nor repurposed.
