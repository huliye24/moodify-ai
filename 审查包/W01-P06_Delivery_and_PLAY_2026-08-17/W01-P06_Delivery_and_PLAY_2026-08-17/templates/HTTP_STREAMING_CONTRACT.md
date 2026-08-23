# HTTP Streaming Contract

## Required

- HTTPS
- correct Content-Type
- Content-Length
- ETag
- Accept-Ranges where supported
- byte range semantics
- safe redirects
- bounded timeout
- retry-safe GET
- cache policy
- signed URL TTL / token TTL

## Validation

- first play
- seek forward
- seek backward
- resume
- partial network interruption
- expired delivery credential refresh
- object missing
