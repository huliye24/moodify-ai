# Reorder Behavior

The domain accepts a complete ordered list of PlaylistItem IDs. It rejects missing, foreign or duplicate IDs, then updates all positions in one in-memory snapshot and performs one atomic store write. UI exposes low-noise up/down controls.

Remove reindexes the remaining relations. Add appends at the current end. Unavailable Track relations participate normally. Ordering is therefore independent of React/DOM order and survives restart.
