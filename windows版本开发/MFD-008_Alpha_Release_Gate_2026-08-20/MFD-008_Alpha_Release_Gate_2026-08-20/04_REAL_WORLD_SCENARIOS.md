# MFD-008 Real-world Scenario Tests

## Scenario 1 — New User / Clean Machine

```text
download installer
install
launch
authenticate
see track
play
pause
seek
next
quit
```

Expected:

> no developer knowledge required.

---

## Scenario 2 — Daily Return

```text
launch next day
session restores
last track returns
position returns
press Play
```

Expected:

> continuity without stale signed URL reuse.

---

## Scenario 3 — Bad Wi-Fi

```text
playing
network drops
media fails
network returns
retry
play resumes
```

Expected:

> no crash, no infinite retry.

---

## Scenario 4 — Session Expired

```text
launch
session expired
refresh
continue
```

If refresh fails:

> clear auth-required state.

---

## Scenario 5 — Rapid User

```text
next next previous next
play pause play
seek
```

Expected:

> last intent wins, no overlap.

---

## Scenario 6 — Second Launch

```text
Moodify running
user double-clicks shortcut again
```

Expected:

> existing instance focused, no duplicate engine.

---

## Scenario 7 — Upgrade

```text
use old alpha
install new alpha
launch
state restored
play
```

Expected:

> upgrade is boring.

---

## Scenario 8 — Uninstall

```text
quit
uninstall
```

Expected:

> app removed cleanly, Cloud account untouched.
