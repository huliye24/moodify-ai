# W01-P06 Acceptance Checklist

## Gates
- [ ] READY contract loaded
- [ ] object access contract loaded
- [ ] secret ownership loaded
- [ ] Android reality scan complete

## Delivery
- [ ] READY-only guard
- [ ] authorization
- [ ] metadata contract
- [ ] signed URL/proxy ADR
- [ ] bounded expiry
- [ ] refresh path
- [ ] range/seek
- [ ] stable Track identity
- [ ] no source/stem accidental exposure

## Android
- [ ] existing player reused where viable
- [ ] PLAY
- [ ] PAUSE
- [ ] seek
- [ ] buffering
- [ ] reconnect
- [ ] URL refresh
- [ ] next/previous/swipe if in scope
- [ ] lifecycle behavior
- [ ] audio focus behavior

## Failure
- [ ] playback taxonomy
- [ ] compute failure isolation
- [ ] missing object behavior
- [ ] expired URI behavior

## Security
- [ ] no OSS secret in APK
- [ ] no DB secret in APK
- [ ] no external processing API secret in APK
- [ ] HTTPS production path
- [ ] no full signed URL in durable logs

## Evidence
- [ ] playback events
- [ ] render traceability
- [ ] correlation ID

## E2E
- [ ] READY test track plays end-to-end
- [ ] seek works
- [ ] pause/resume works
- [ ] expiry refresh works if applicable

## Scope
- [ ] no compute changes
- [ ] no state-machine changes
- [ ] no unrelated UI expansion
- [ ] no iOS/offline/community work

## Handoff
- [ ] P07 handoff complete
- [ ] stop after P06
