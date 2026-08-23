# Migration Report

```text
MIGRATION_REQUIRED = YES
OLD_SCHEMA = LocalState v1 (playback/window/app)
NEW_SCHEMA = LocalState v2 (+ library.tracks)
ROWS / RECORDS BEFORE = no Library records existed
ROWS / RECORDS AFTER = 0 Library records at migration; imports append thereafter
RELATION CHECK = playlist-name localStorage preserved unchanged; PlaylistItem did not exist
ROLLBACK = local-state.json.v1.bak
RESULT = PASS (idempotency and backup covered by automated test)
```
