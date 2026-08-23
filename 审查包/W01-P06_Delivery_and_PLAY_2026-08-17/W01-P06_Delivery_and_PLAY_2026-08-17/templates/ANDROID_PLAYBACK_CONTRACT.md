# Android Playback Contract

## Player

Reuse current engine if viable.

## Input

`PlaybackMetadata`

## Player States

- IDLE
- LOADING
- BUFFERING
- PLAYING
- PAUSED
- ENDED
- ERROR

These are client playback states, not Job lifecycle states.

## Commands

- play
- pause
- resume
- seek
- next / previous or swipe if current product scope
- retry
- refresh delivery entry

## Expired URI Recovery

1. detect delivery auth/expiry failure
2. request fresh PlaybackMetadata
3. preserve track_id
4. preserve playback position if safe
5. load refreshed URI
6. resume

## Failure Isolation

No Android playback error may mutate a READY Job into FAILED.
