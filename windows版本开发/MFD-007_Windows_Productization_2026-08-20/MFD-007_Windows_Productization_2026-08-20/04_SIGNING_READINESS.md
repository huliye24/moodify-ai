# MFD-007 Windows Signing Readiness

## Status values

```text
SIGNING_AVAILABLE
SIGNING_CONFIGURED_NOT_VERIFIED
SIGNING_NOT_AVAILABLE
```

---

## If available

Verify:

- executable signature
- installer signature
- publisher identity
- timestamp
- install behavior

Record evidence.

---

## If unavailable

Do not block internal Alpha.

But mark:

```text
PUBLIC_ALPHA_RELEASE = BLOCKED_BY_SIGNING
```

Do not:

- self-sign and call it trusted
- commit certificate
- bypass Windows security
- disable SmartScreen
- instruct users to weaken OS security as product behavior

---

## Credential boundary

Credentials belong only in:

```text
approved signing environment
or
protected CI release secret
```

Never in Desktop runtime.
