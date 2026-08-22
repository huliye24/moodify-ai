# Queue Mutation Policy

- Play Now inserts a new current QueueItem immediately after the prior current location while keeping remaining items.
- Play Next inserts directly after current; repeated actions use latest-first order.
- Append preserves input order at the tail.
- Duplicate Track IDs are allowed.
- Removing a future item is immediate.
- Removing current detaches its QueueItem while audio continues; ended advances to the nearest surviving successor.
- Reorder is an atomic full-ID permutation and preserves current QueueItem identity/audio.
- Clear removes future items and keeps current playing item.

No mutation writes Playlist, PlaylistItem, Library or filesystem data.
