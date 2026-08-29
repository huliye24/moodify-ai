# W10 Acceptance Criteria

## A. Preflight
- [ ] W09_STATUS = PASS
- [ ] W10_GATE = PASS
- [ ] Track authority known
- [ ] Playback authority known
- [ ] Recovery authority known
- [ ] real API client located
- [ ] real cloud endpoints audited
- [ ] auth reality audited
- [ ] object storage reality audited

## B. Capability Truth
- [ ] every cloud capability classified
- [ ] CODE_ONLY not treated as live
- [ ] historical docs not treated as live
- [ ] no unverified AI claims
- [ ] no unverified pipeline claims

## C. Cloud Boundary
- [ ] one cloud client adapter
- [ ] no scattered fetch logic
- [ ] no second Track authority
- [ ] no second Playback authority

## D. CloudPreparation
- [ ] stable ID
- [ ] references Track
- [ ] status explicit
- [ ] user-facing status mapping simple
- [ ] internal job states hidden

## E. Request / Upload
- [ ] verified request path
- [ ] duplicate click safe
- [ ] idempotency strategy
- [ ] timeout
- [ ] upload failure safe
- [ ] unsupported file safe
- [ ] local source missing safe

## F. Authentication
- [ ] no service/admin key in client
- [ ] no DB credential in client
- [ ] no third-party provider secret in client
- [ ] auth failure handled
- [ ] signed upload/source token handling safe

## G. Status
- [ ] queued/preparing mapping
- [ ] ready mapping if supported
- [ ] failed mapping
- [ ] unknown backend status safe
- [ ] polling/backoff bounded
- [ ] restart refresh

## H. Prepared Source
- [ ] only implemented if backend truly provides it
- [ ] source validated
- [ ] expiry handled if relevant
- [ ] Track identity preserved
- [ ] playback source policy explicit
- [ ] cloud failure can fall back local

## I. Offline
- [ ] no network before request
- [ ] network loss during request
- [ ] network loss during polling
- [ ] local Playback remains usable
- [ ] Queue/Playlist remain usable

## J. Retry
- [ ] retryable/non-retryable split
- [ ] max attempts
- [ ] backoff
- [ ] no infinite retry
- [ ] no duplicate server tasks

## K. Recovery
- [ ] active preparation survives restart
- [ ] no automatic duplicate resubmit
- [ ] READY re-resolves source
- [ ] FAILED remains inspectable

## L. UI
- [ ] minimal preparation state only
- [ ] no Ear
- [ ] no Stem
- [ ] no Judge/Intervene/Verify
- [ ] no Evidence
- [ ] no provider names
- [ ] current Alpha visual direction preserved

## M. Security / Evidence
- [ ] endpoints/config safe
- [ ] logs do not expose secrets
- [ ] private audio not committed as fixtures
- [ ] evidence demonstrates real cloud status
- [ ] overclaim audit completed

## PASS Rule

允许三种结果：

```text
PASS    = verified end-to-end cloud bridge
PARTIAL = verified real subset only
BLOCKED = no safe/live client cloud path
```

不允许“愿景性 PASS”。
