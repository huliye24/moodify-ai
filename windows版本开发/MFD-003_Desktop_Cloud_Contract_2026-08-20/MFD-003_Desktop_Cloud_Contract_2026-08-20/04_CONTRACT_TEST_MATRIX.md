# MFD-003 Contract Test Matrix

## Session

| Case | Expected |
|---|---|
| no token | 401 |
| malformed token | 401 |
| expired token | 401 / SESSION_EXPIRED |
| valid token | 200 |
| revoked token | 401 |

## Library

| Case | Expected |
|---|---|
| valid user | only visible tracks |
| no tracks | empty list, not error |
| unauthorized | 401 |
| backend unavailable | typed error |

## Track

| Case | Expected |
|---|---|
| existing visible track | 200 |
| missing track | 404 |
| inaccessible track | 403 or product-safe 404 |
| malformed id | 4xx typed error |

## Playback Manifest

| Case | Expected |
|---|---|
| ready track | 200 |
| processing track | typed PLAYBACK_NOT_READY |
| failed track | typed unavailable/failed |
| missing asset | typed ASSET_UNAVAILABLE |
| unauthorized track | denied |
| expired session | denied |

## Stream URL

| Case | Expected |
|---|---|
| valid URL before expiry | resource accessible |
| expired URL | denied / expired |
| malformed URL | denied |
| copied URL after expiry | denied |
| resource missing | clear failure |

## Logging

- [ ] no Authorization header
- [ ] no refresh token
- [ ] no full signed URL query
- [ ] request_id retained
- [ ] status retained
- [ ] latency retained

## Desktop client

- [ ] timeout
- [ ] cancellation
- [ ] typed decode
- [ ] typed errors
- [ ] invalid response rejected
- [ ] API base URL config
- [ ] no hardcoded service secret
