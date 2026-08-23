# MFD-008 Defect Policy

## P0 — Release Blocker

Examples:

- app cannot install
- app cannot launch
- app cannot play real Cloud audio
- wrong-user track access
- service key bundled
- token leakage
- crash loop
- duplicate simultaneous playback
- corrupted state prevents startup
- malicious/uncontrolled update origin
- installer destructive behavior

Decision:

> NO-GO

---

## P1 — Alpha Blocker

Examples:

- seek broadly broken
- session refresh unreliable
- manifest expiry cannot recover
- close/quit leaves audio running unpredictably
- upgrade breaks persisted state
- uninstall broken
- tray cannot fully quit

Decision:

> Usually NO-GO.

Can become CONDITIONAL only through explicit human acceptance.

---

## P2 — Known Alpha Issue

Examples:

- minor layout issue
- media overlay metadata delay
- non-critical log wording
- edge-case window placement

Decision:

> Can release as Alpha if documented.

---

## P3 — Polish

Examples:

- spacing
- animation refinement
- copy
- non-blocking icon detail

Decision:

> Does not block Alpha.
