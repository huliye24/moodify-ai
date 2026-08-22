# MFD-007 Release & Update Policy

## 1. Internal Alpha

Purpose:

- team testing
- trusted tester testing
- install/upgrade verification

Can be unsigned if signing is unavailable.

Must be clearly marked:

```text
UNSIGNED_INTERNAL_ALPHA
```

---

## 2. Public Alpha

Requires release gate:

- signing available
- installer verified
- update origin controlled
- security audit
- release notes
- checksums
- rollback instruction
- human approval

---

## 3. Update states

```text
DISABLED
CHECKING
UP_TO_DATE
AVAILABLE
DOWNLOADING
READY
ERROR
```

Update state is separate from playback state.

---

## 4. Update principle

> Playback must not depend on update success.

If update service is down:

```text
Moodify still opens
Moodify still plays
```

---

## 5. Install update

Do not force-install while active playback is happening without an explicit product policy.

For Alpha:

> notify / stage update, install on user-approved restart or app quit.

---

## 6. Rollback

Every external release should retain at least the previous known-good installer/version.

MFD-007 prepares this policy.

MFD-008 validates final release procedure.
