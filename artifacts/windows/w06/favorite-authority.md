# Favorite Authority

Favorite is `{ track_id, created_at }` in LocalState schema v4, owned by `LibraryExperienceService`. Toggle is idempotent and persisted by the sole LocalStateStore. No metadata is copied. Unavailable Tracks retain favorites. W02 removal hard-removes the Track reference, so `LocalStateStore.setLibrary` prunes its Favorite relation; original files remain untouched.
