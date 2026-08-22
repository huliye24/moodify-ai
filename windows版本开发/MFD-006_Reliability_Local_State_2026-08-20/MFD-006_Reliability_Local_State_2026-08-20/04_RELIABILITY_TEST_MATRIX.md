# MFD-006 Reliability Test Matrix

## Restart

| Case | Expected |
|---|---|
| normal close/reopen | track/position/volume restore |
| kill process/reopen | safe recovery |
| update local state during quit | no corruption |

## Local state corruption

| Case | Expected |
|---|---|
| invalid JSON | safe reset |
| unknown schema | migration/reset |
| volume > 1 | clamp/default |
| negative position | reset |
| invalid window position | visible fallback |

## Session

| Case | Expected |
|---|---|
| valid session | normal |
| expired session | refresh |
| refresh success | continue |
| refresh failure | auth-required |
| concurrent 401s | one refresh flight |

## Manifest

| Case | Expected |
|---|---|
| valid manifest | play |
| expired manifest | refresh |
| concurrent refresh need | one refresh flight |
| refresh failure | typed recoverable error |
| signed URL stored on disk | MUST NOT HAPPEN |

## Network

| Case | Expected |
|---|---|
| API offline | typed error |
| media offline | playback error |
| reconnect | retry works |
| repeated failure | bounded retries |
| non-retryable 403 | no retry loop |

## Race

| Case | Expected |
|---|---|
| next x10 quickly | last intent wins |
| previous/next mix | no overlap |
| seek during switch | safe |
| play during load | safe |
| quit during request | no hang |

## Stress

- [ ] 50 track switches
- [ ] no audible overlap
- [ ] no obvious listener leak
- [ ] no request explosion
- [ ] memory remains broadly stable
