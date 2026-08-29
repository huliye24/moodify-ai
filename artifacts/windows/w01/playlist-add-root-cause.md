# Add Track to Playlist — Root Cause

The break is structural and occurs before persistence:

1. `MinimalPlayer.tsx:231-239` creates and persists only `{id,name}` playlist records.
2. `MinimalPlayer.tsx:369-374` renders playlist buttons without an `onClick` or contextual action.
3. `MinimalPlayer.tsx:187-225` imports local tracks into React memory and temporary blob URLs only.
4. No `PlaylistItem` type, relation, mutation, IPC channel, database/JSON field, or test exists.

Therefore the journey stops at “choose Track -> Add to Playlist”: there is no UI entry or event, no domain mutation, and no relation to persist or rehydrate. This is not an ID mismatch or subscription bug. Playlist creation appears durable only because names live in `localStorage`; track membership has never been modeled.

Severity: P0 for the W03 playlist closure and a prerequisite design input for W02 Library. Repair should first establish durable Track identity/Library authority, then add a PlaylistItem relation referencing Track IDs. Queue order must remain independent from playlist order.
