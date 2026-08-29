# Schema Migration

LocalState advances v4 → v5 by adding `recovery = EMPTY_RECOVERY`; durable collections are untouched and migration is idempotent with the existing pre-migration backup. Recovery inner schema is v1. Missing/legacy fields default and validate; unknown fields are ignored. A future recovery schema becomes an empty session only. A future LocalState version resets unsupported playback/recovery fields while preserving recognized Library/Playlist/Favorite/History collections.
