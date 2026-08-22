# ADR — Signed URL vs Streaming Proxy

## Problem

How should Android receive a READY render?

## Option A — Signed Object URL

### Benefits
- lower API bandwidth
- simpler One Song path
- native range support if object store supports it

### Costs/Risks
- URL expiry
- signed query exposure risk
- object-store semantics visible indirectly

## Option B — API Streaming Proxy

### Benefits
- central authorization
- hides storage

### Costs/Risks
- API bandwidth
- range implementation
- extra failure point

## Selected

- decision:
- evidence:
- reason:
- TTL:
- refresh:
- fallback:
- revisit trigger:
