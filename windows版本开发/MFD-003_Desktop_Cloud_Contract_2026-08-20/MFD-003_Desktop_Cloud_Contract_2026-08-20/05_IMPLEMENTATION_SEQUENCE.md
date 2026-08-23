# MFD-003 Implementation Sequence

## Step 1 — Preflight

- [ ] MFD-002 GO
- [ ] Desktop repo clean
- [ ] backend repo / deployment identified
- [ ] current auth identified
- [ ] current BFF identified
- [ ] current media delivery identified

## Step 2 — Read-only inventory

- [ ] endpoints
- [ ] auth
- [ ] track model
- [ ] media model
- [ ] Android calls
- [ ] internal/public split

## Step 3 — Contract decision

- [ ] session
- [ ] track
- [ ] library
- [ ] playback manifest
- [ ] errors
- [ ] API version

## Step 4 — Security decision

- [ ] user token
- [ ] no service key
- [ ] signed URL
- [ ] authorization
- [ ] logging redaction

## Step 5 — Backend minimum changes

Only if needed.

- [ ] BFF route
- [ ] response models
- [ ] auth guard
- [ ] playback manifest generator
- [ ] error mapping

## Step 6 — Desktop API client

- [ ] typed client
- [ ] session
- [ ] library
- [ ] playback manifest
- [ ] errors
- [ ] timeout/cancel

## Step 7 — Contract tests

- [ ] backend
- [ ] Desktop
- [ ] invalid cases
- [ ] authorization
- [ ] expiry

## Step 8 — Real integration smoke

- [ ] real session
- [ ] real track
- [ ] real manifest
- [ ] resource HEAD/range reachability
- [ ] no audio playback required

## Step 9 — Documentation

- [ ] contract
- [ ] auth
- [ ] security
- [ ] gaps
- [ ] MFD-004 prerequisites

## Step 10 — Final audit

- [ ] no secrets
- [ ] no direct DB
- [ ] no internal endpoint leak
- [ ] no MFD-004 scope creep
