# MFD-006 Reliability Evidence Template

## Environment

```text
Windows:
Electron:
Desktop version:
Desktop commit:
Backend API version:
```

## Local state

```text
state path:
schema version:
write strategy:
migration strategy:
corruption fallback:
```

## Persisted fields

```text
last track:
position:
volume:
window:
other:
```

## Sensitive state

```text
session storage:
refresh token storage:
signed URL persisted: NO
service key present: NO
```

## Restart tests

```text
normal restart:
forced process kill:
position restore:
volume restore:
window restore:
```

## Session tests

```text
expired:
refresh success:
refresh failure:
concurrent refresh:
```

## Manifest tests

```text
expired:
refresh:
concurrent refresh:
playback recovery:
```

## Network

```text
disconnect:
state:
reconnect:
retry:
```

## Corruption

```text
invalid JSON:
bad schema:
bad volume:
bad window bounds:
```

## Stress

```text
50 track switches:
overlap:
request explosion:
memory observation:
listener observation:
```

## Known limitations

Only verified limitations.
