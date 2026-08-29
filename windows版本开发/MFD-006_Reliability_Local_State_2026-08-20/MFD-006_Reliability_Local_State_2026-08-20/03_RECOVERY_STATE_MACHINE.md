# MFD-006 Recovery State Machine

This is not a second playback state machine.

It is a failure/recovery policy map.

---

## Session

```text
VALID
  ↓ expiry
EXPIRED
  ↓ refresh available
REFRESHING
  ├── success → VALID
  └── failure → AUTH_REQUIRED
```

---

## Manifest

```text
VALID
  ↓ expiry / rejection
STALE
  ↓ refresh
REFRESHING
  ├── success → VALID
  └── failure → PLAYBACK_RECOVERABLE_ERROR
```

---

## Network

```text
ONLINE
  ↓ failure
DEGRADED/OFFLINE
  ↓ bounded retry or user retry
RECOVERING
  ├── success → ONLINE
  └── failure → DEGRADED/OFFLINE
```

---

## Local state

```text
LOAD
  ├── valid → READY
  ├── migratable → MIGRATE → READY
  └── corrupt → RESET_SAFE_DEFAULTS → READY
```

---

## Rule

任何 recovery loop 必须：

- bounded
- observable
- cancellable
- non-recursive
- non-infinite
