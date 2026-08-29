# Moodify Desktop Alpha — Rollback Template

## Current release

```text
version:
commit:
installer:
```

## Last known good

```text
version:
commit:
installer:
sha256:
```

## Rollback steps

1. Quit Moodify completely.
2. Uninstall current build if required by installer model.
3. Install last known good build.
4. Launch.
5. Validate session.
6. Validate last track/local state compatibility.
7. Validate Play.

## Local state compatibility

```text
forward compatible:
backward compatible:
migration caveat:
reset required:
```

## Cloud compatibility

Rollback must not require DB/manual data surgery.

If API contract is incompatible:

> release must be blocked or server compatibility restored.
