# W10 Preflight

```text
W09_STATUS = PASS
W10_GATE = PASS
TRACK_AUTHORITY = LibraryTrack / LibraryService
PLAYBACK_AUTHORITY = PlaybackService
RECOVERY_AUTHORITY = LocalStateStore v5 / RecoveryService
API_CLIENT_REALITY = BffClient supports bootstrap, catalogue, Track, session, favorites, recent plays, play events; no cloud preparation methods
CLOUD_ENDPOINT_REALITY = live public BFF responds; preparation/job endpoints absent
AUTH_REALITY = live bootstrap exposes no account/creator writes; desktop bearer model is not the deployed upload cookie/CSRF model
UPLOAD_REALITY = PUT /media route exists and was invite-beta verified on 2026-08-13, but is unavailable to current anonymous Windows client
OBJECT_STORAGE_REALITY = server-managed authenticated media namespace was historically verified; not accessible through current desktop auth
JOB_STATUS_REALITY = no product preparation status endpoint found or live
PREPARED_SOURCE_REALITY = no preparation result/source contract found or live
CURRENT_VERIFIED_CLOUD_CHAIN = public catalogue Track -> remote playback only; no Local Track -> preparation -> status chain
```

Live check on 2026-08-21: `/bootstrap` HTTP 200 with `account_actions=false`, `creator_writes=false`; `/preparations` 404; `/jobs` 404; GET `/media` 405 (PUT route only).
