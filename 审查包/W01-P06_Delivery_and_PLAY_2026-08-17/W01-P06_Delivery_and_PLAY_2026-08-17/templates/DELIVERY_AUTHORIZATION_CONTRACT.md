# Delivery Authorization Contract

## Request

- authenticated actor:
- track_id:
- app version:
- correlation_id:

## Checks

1. Track exists
2. Track is READY
3. Final render object exists
4. Actor/access scope may play it
5. Object access class permits delivery
6. Delivery entry is issued with bounded TTL

## Result

- playback_session_id
- playback metadata
- URI/proxy token
- expiry

## Forbidden

- public-read default bucket
- permanent mobile OSS credential
- permanent URL written into Track record
